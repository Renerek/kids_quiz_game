
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserStat
from django.db.models import Sum, Max, Count
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.paginator import Paginator


@login_required
def user_stats(request):
    user = request.user
    stats = UserStat.objects.filter(user=user).order_by('-played_at')

    # Date range filter
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()
    date_filter = None
    if from_date:
        try:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            stats = stats.filter(played_at__date__gte=from_dt.date())
        except Exception:
            from_dt = None
    else:
        from_dt = None
    if to_date:
        try:
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            stats = stats.filter(played_at__date__lte=to_dt.date())
        except Exception:
            to_dt = None
    else:
        to_dt = None

    # Reset per_game stats if requested
    if request.method == "POST" and request.POST.get("reset_per_game") == "1":
        UserStat.objects.filter(user=user).delete()
        return redirect('quiz:user_stats')

    # Per-game summary
    per_game = stats.values('game').annotate(
        total_score=Sum('score'),
        total_correct=Sum('correct'),
        total_incorrect=Sum('incorrect'),
        best_score=Max('score'),
        plays=Count('id'),
        total_time=Sum('time_spent'),
        last_played=Max('played_at'),
    ).order_by('-plays')

    # Per-day breakdown (date range or last 7 days)
    today = timezone.now().date()
    if from_dt and to_dt:
        days = [(from_dt.date() + timedelta(days=i)) for i in range((to_dt.date() - from_dt.date()).days + 1)]
    elif from_dt:
        days = [from_dt.date()]
    elif to_dt:
        days = [to_dt.date()]
    else:
        days = [today - timedelta(days=i) for i in range(7)]
    per_day = []
    for day in days:
        day_stats = UserStat.objects.filter(user=user, played_at__date=day)
        per_day.append({
            'date': day,
            'plays': day_stats.count(),
            'score': day_stats.aggregate(Sum('score'))['score__sum'] or 0,
            'correct': day_stats.aggregate(Sum('correct'))['correct__sum'] or 0,
            'incorrect': day_stats.aggregate(Sum('incorrect'))['incorrect__sum'] or 0,
            'time_spent': day_stats.aggregate(Sum('time_spent'))['time_spent__sum'] or 0,
        })

    # Pagination for each section
    per_game_page = int(request.GET.get('per_game_page', 1))
    per_day_page = int(request.GET.get('per_day_page', 1))
    sessions_page = int(request.GET.get('sessions_page', 1))
    per_game_paginator = Paginator(list(per_game), 10)
    per_day_paginator = Paginator(per_day, 10)
    sessions_paginator = Paginator(list(stats), 10)

    context = {
        'per_game': per_game_paginator.get_page(per_game_page),
        'per_day': per_day_paginator.get_page(per_day_page),
        'stats': sessions_paginator.get_page(sessions_page),
        'from_date': from_date,
        'to_date': to_date,
        'per_game_paginator': per_game_paginator,
        'per_day_paginator': per_day_paginator,
        'sessions_paginator': sessions_paginator,
        'per_game_page': per_game_page,
        'per_day_page': per_day_page,
        'sessions_page': sessions_page,
    }
    return render(request, 'quiz/user_stats.html', context)
