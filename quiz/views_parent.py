import logging
import smtplib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db.models import Avg, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string

from .forms import AddChildForm, AssignmentForm, ParentGateForm
from .models import Assignment, AssignmentResult, ParentProfile, UserProfile, UserStat

logger = logging.getLogger(__name__)

PARENT_GATE_SESSION_KEY = "parent_gate_session_verified"
PARENT_GATE_ONE_SHOT_KEY = "parent_gate_allow_once"


def _send_email_with_fallback(subject, text_body, html_body, recipient_list):
    if not recipient_list:
        return
    msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, recipient_list)
    if html_body:
        msg.attach_alternative(html_body, "text/html")
    try:
        msg.send(fail_silently=False)
    except smtplib.SMTPAuthenticationError:
        logger.exception("SMTP authentication failed while sending parent dashboard email")
        try:
            file_conn = get_connection(
                "django.core.mail.backends.filebased.EmailBackend",
                file_path=settings.EMAIL_FILE_PATH,
            )
            file_conn.send_messages([msg])
        except Exception:
            logger.exception("Failed to fallback to file backend for parent dashboard email after SMTP error")
    except Exception:
        logger.exception("Failed to send parent dashboard email")
        try:
            file_conn = get_connection(
                "django.core.mail.backends.filebased.EmailBackend",
                file_path=settings.EMAIL_FILE_PATH,
            )
            file_conn.send_messages([msg])
        except Exception:
            logger.exception("Failed to fallback to file backend for parent dashboard email after general error")


def _send_assignment_created_email(assignment):
    student = assignment.assigned_to
    if not student.email:
        return
    subject = f"New Kids Quiz Game assignment: {assignment.get_game_display()}"
    # Build absolute URL via settings.SITE_URL if provided
    base_url = getattr(settings, "SITE_URL", "")
    if base_url:
        dashboard_link = f"{base_url}{reverse('quiz:child_assignments')}"
    else:
        dashboard_link = reverse("quiz:child_assignments")
    due_str = timezone.localtime(assignment.due_date)
    context = {
        "student": student,
        "assigned_by": assignment.assigned_by,
        "assignment": assignment,
        "game_name": assignment.get_game_display(),
        "due_at": due_str,
        "notes": assignment.notes,
        "dashboard_link": dashboard_link,
    }
    text_body = render_to_string("quiz/emails/assignment_created.txt", context)
    html_body = render_to_string("quiz/emails/assignment_created.html", context)
    _send_email_with_fallback(subject, text_body, html_body, [student.email])


def _send_assignment_completed_email(assignment, result, parent_emails):
    if not parent_emails:
        return
    student = assignment.assigned_to
    subject = f"{student.username} completed {assignment.get_game_display()}"
    due_str = timezone.localtime(assignment.due_date)
    context = {
        "student": student,
        "assignment": assignment,
        "game_name": assignment.get_game_display(),
        "assigned_by": assignment.assigned_by,
        "due_at": due_str,
        "result": result,
    }
    text_body = render_to_string("quiz/emails/assignment_feedback.txt", context)
    html_body = render_to_string("quiz/emails/assignment_feedback.html", context)
    _send_email_with_fallback(subject, text_body, html_body, parent_emails)


@login_required
def parent_dashboard(request):
    profile = getattr(request.user, "profile", None)
    if profile is None:
        profile = UserProfile.objects.create(user=request.user, first_name=request.user.username)

    if request.method == "POST" and "parent_gate_submit" in request.POST:
        gate_form = ParentGateForm(request.POST)
        if gate_form.is_valid():
            profile.age = gate_form.cleaned_data["age"]
            profile.save(update_fields=["age"])
            request.session[PARENT_GATE_ONE_SHOT_KEY] = True
            request.session[PARENT_GATE_SESSION_KEY] = True
            messages.success(request, "Age verified. Welcome to the parent dashboard!")
            return redirect("quiz:parent_dashboard")
        return render(request, "quiz/parent_dashboard_gate.html", {"gate_form": gate_form})

    if request.method == "GET":
        gate_token = request.session.pop(PARENT_GATE_ONE_SHOT_KEY, False)
        if not gate_token:
            initial = {}
            if profile.age:
                initial["age"] = profile.age
            return render(request, "quiz/parent_dashboard_gate.html", {"gate_form": ParentGateForm(initial=initial)})
    elif not request.session.get(PARENT_GATE_SESSION_KEY):
        messages.info(request, "Please verify your age to access the parent dashboard.")
        return redirect("quiz:parent_dashboard")

    parent_profile, _ = ParentProfile.objects.get_or_create(user=request.user)
    children_qs = parent_profile.children.all()
    add_child_form = AddChildForm()
    assignment_form = AssignmentForm(children_queryset=children_qs)

    if request.method == "POST":
        if "add_child_submit" in request.POST:
            add_child_form = AddChildForm(request.POST)
            if add_child_form.is_valid():
                child = add_child_form.cleaned_data['child_identifier']
                if child == request.user:
                    messages.error(request, "You cannot add yourself as a child.")
                elif parent_profile.children.filter(pk=child.pk).exists():
                    messages.info(request, f"{child.username} is already linked to your dashboard.")
                else:
                    parent_profile.children.add(child)
                    messages.success(request, f"{child.username} has been added to your dashboard.")
                    request.session[PARENT_GATE_ONE_SHOT_KEY] = True
                return redirect("quiz:parent_dashboard")
        elif "create_assignment_submit" in request.POST:
            assignment_form = AssignmentForm(request.POST, children_queryset=children_qs)
            if assignment_form.is_valid():
                assignment = assignment_form.save(commit=False)
                assignment.assigned_by = request.user
                assignment.save()
                _send_assignment_created_email(assignment)
                messages.success(request, f"Assignment for {assignment.assigned_to.username} created successfully.")
                request.session[PARENT_GATE_ONE_SHOT_KEY] = True
                return redirect("quiz:parent_dashboard")

    children_data = []
    for child in children_qs:
        stats_qs = UserStat.objects.filter(user=child)
        total_sessions = stats_qs.count()
        last_played = stats_qs.order_by('-played_at').first()
        aggregates = stats_qs.aggregate(
            total_correct=Sum('correct'),
            total_incorrect=Sum('incorrect'),
            average_score=Avg('score'),
        ) if total_sessions else {"total_correct": 0, "total_incorrect": 0, "average_score": 0}

        if total_sessions:
            by_game_stats = stats_qs.values('game').annotate(
                total_correct=Sum('correct'),
                total_incorrect=Sum('incorrect'),
            ).order_by('-total_correct')
            by_game = []
            for row in by_game_stats:
                correct = row['total_correct'] or 0
                incorrect = row['total_incorrect'] or 0
                attempts = correct + incorrect
                accuracy = round((correct / attempts) * 100) if attempts else None
                by_game.append({
                    "game": row['game'],
                    "total_correct": correct,
                    "total_incorrect": incorrect,
                    "accuracy": accuracy,
                })
        else:
            by_game = []

        pending_assignments = Assignment.objects.filter(assigned_to=child, is_completed=False).order_by('due_date')
        completed_assignments = Assignment.objects.filter(assigned_to=child, is_completed=True).order_by('-due_date')

        children_data.append({
            "child": child,
            "total_sessions": total_sessions,
            "last_played": last_played.played_at if last_played else None,
            "total_correct": aggregates.get('total_correct') or 0,
            "total_incorrect": aggregates.get('total_incorrect') or 0,
            "average_score": round(aggregates.get('average_score') or 0, 1),
            "by_game": by_game,
            "pending_assignments": pending_assignments,
            "completed_assignments": completed_assignments[:5],
        })

    context = {
        "parent_profile": parent_profile,
        "children_data": children_data,
        "add_child_form": add_child_form,
        "assignment_form": assignment_form,
        "children_count": children_qs.count(),
    }
    return render(request, "quiz/parent_dashboard.html", context)


@login_required
def child_assignments(request):
    assignments = list(
        Assignment.objects.filter(assigned_to=request.user).select_related('assigned_by').order_by('is_completed', 'due_date')
    )
    results = AssignmentResult.objects.filter(user=request.user, assignment__in=assignments).select_related('assignment')
    results_map = {result.assignment_id: result for result in results}
    for assignment in assignments:
        assignment.result = results_map.get(assignment.id)
    context = {
        "assignments": assignments,
    }
    return render(request, "quiz/child_assignments.html", context)


@login_required
def assignment_mark_complete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, assigned_to=request.user)
    if assignment.is_completed:
        messages.info(request, "This assignment is already marked as completed.")
        return redirect("quiz:child_assignments")

    if request.method == "POST":
        latest_stat = UserStat.objects.filter(user=request.user, game=assignment.game).order_by('-played_at').first()
        result = AssignmentResult.objects.create(
            assignment=assignment,
            user=request.user,
            score=latest_stat.score if latest_stat else 0,
            correct=latest_stat.correct if latest_stat else 0,
            incorrect=latest_stat.incorrect if latest_stat else 0,
            time_spent=latest_stat.time_spent if latest_stat else 0.0,
        )
        assignment.is_completed = True
        assignment.save(update_fields=["is_completed"])
        parent_profile_qs = ParentProfile.objects.filter(children=assignment.assigned_to)
        parent_emails = [profile.user.email for profile in parent_profile_qs if profile.user.email]
        _send_assignment_completed_email(assignment, result, parent_emails)
        messages.success(request, "Great job! The assignment has been marked as completed.")
        return redirect("quiz:child_assignments")

    context = {
        "assignment": assignment,
    }
    return render(request, "quiz/assignment_confirm_complete.html", context)


@login_required
def assignment_delete(request, pk):
    if not request.session.get(PARENT_GATE_SESSION_KEY):
        messages.info(request, "Please verify your age to manage assignments.")
        return redirect("quiz:parent_dashboard")
    assignment = get_object_or_404(Assignment, pk=pk, assigned_by=request.user)
    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment removed.")
        request.session[PARENT_GATE_ONE_SHOT_KEY] = True
        return redirect("quiz:parent_dashboard")
    return render(request, "quiz/assignment_confirm_delete.html", {"assignment": assignment})


@login_required
def remove_child(request, child_id):
    if not request.session.get(PARENT_GATE_SESSION_KEY):
        messages.info(request, "Please verify your age to manage linked learners.")
        return redirect("quiz:parent_dashboard")
    parent_profile = get_object_or_404(ParentProfile, user=request.user)
    child = get_object_or_404(parent_profile.children, pk=child_id)
    if request.method == "POST":
        parent_profile.children.remove(child)
        messages.success(request, f"{child.username} has been removed from your dashboard.")
        request.session[PARENT_GATE_ONE_SHOT_KEY] = True
        return redirect("quiz:parent_dashboard")
    return render(request, "quiz/remove_child_confirm.html", {"child": child})
