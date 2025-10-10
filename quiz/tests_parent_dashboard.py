from datetime import timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Assignment, AssignmentResult, ParentProfile, UserProfile, UserStat


class ParentDashboardTests(TestCase):
	def setUp(self):
		self.parent = User.objects.create_user(username="parent", password="pw12345", email="parent@example.com")
		self.child = User.objects.create_user(username="learner", password="pw12345", email="child@example.com")
		UserProfile.objects.create(user=self.parent, first_name="Parent", last_name="Tester")
		UserProfile.objects.create(user=self.child, first_name="Child", last_name="Learner")

	def _login_parent(self):
		self.client.login(username="parent", password="pw12345")

	def _verify_parent_gate(self):
		current_year = timezone.now().year
		age = 30
		birth_year = current_year - age
		response = self.client.post(
			reverse("quiz:parent_dashboard"),
			{"parent_gate_submit": "1", "age": age, "birth_year": birth_year},
			follow=True,
		)
		self.assertEqual(response.status_code, 200)

	def _login_child(self):
		self.client.login(username="learner", password="pw12345")

	def test_parent_can_link_child_and_create_assignment(self):
		self._login_parent()
		self._verify_parent_gate()
		add_child_response = self.client.post(
			reverse("quiz:parent_dashboard"),
			{"child_identifier": "learner", "add_child_submit": "1"},
			follow=True,
		)
		self.assertEqual(add_child_response.status_code, 200)
		parent_profile = ParentProfile.objects.get(user=self.parent)
		self.assertTrue(parent_profile.children.filter(pk=self.child.pk).exists())

		due_time = (timezone.now() + timedelta(days=1)).astimezone(timezone.get_current_timezone())
		due_field = due_time.strftime("%Y-%m-%dT%H:%M")
		assignment_response = self.client.post(
			reverse("quiz:parent_dashboard"),
			{
				"create_assignment_submit": "1",
				"assigned_to": str(self.child.pk),
				"game": "math",
				"due_date": due_field,
				"notes": "Practice your addition skills!",
			},
			follow=True,
		)
		self.assertEqual(assignment_response.status_code, 200)
		assignment = Assignment.objects.get(assigned_by=self.parent, assigned_to=self.child)
		self.assertEqual(assignment.game, "math")
		self.assertFalse(assignment.is_completed)
		self.assertEqual(len(mail.outbox), 1)
		self.assertIn("New Kids Quiz Game assignment", mail.outbox[0].subject)
		self.assertIn("child@example.com", mail.outbox[0].to)

	def test_child_can_mark_assignment_complete_and_notify_parent(self):
		parent_profile, _ = ParentProfile.objects.get_or_create(user=self.parent)
		parent_profile.children.add(self.child)
		assignment = Assignment.objects.create(
			assigned_by=self.parent,
			assigned_to=self.child,
			game="animals",
			due_date=timezone.now() + timedelta(days=2),
			notes="Explore the animal world!",
		)
		UserStat.objects.create(
			user=self.child,
			game="animals",
			score=85,
			correct=8,
			incorrect=2,
			time_spent=42.5,
		)

		self._login_child()
		list_response = self.client.get(reverse("quiz:child_assignments"))
		self.assertContains(list_response, "Animals Game")

		complete_response = self.client.post(reverse("quiz:assignment_mark_complete", args=[assignment.pk]), follow=True)
		self.assertEqual(complete_response.status_code, 200)
		assignment.refresh_from_db()
		self.assertTrue(assignment.is_completed)
		result = AssignmentResult.objects.get(assignment=assignment, user=self.child)
		self.assertEqual(result.score, 85)
		self.assertAlmostEqual(result.time_spent, 42.5)
		self.assertGreaterEqual(len(mail.outbox), 1)
		self.assertIn("completed", mail.outbox[-1].subject.lower())
		self.assertIn("parent@example.com", mail.outbox[-1].to)
