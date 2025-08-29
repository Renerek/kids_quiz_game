
from django.test import TestCase, Client
from django.urls import reverse

class QuizViewsTests(TestCase):
	def test_start_quiz_view_get(self):
		response = self.client.get(reverse('quiz:start'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Enter your name")


	def test_question_view(self):
		# Setup session for question view
		from .models import QuizSession
		session = QuizSession.objects.create()
		session_id = session.id
		session_data = self.client.session
		session_data['quiz_session_id'] = session_id
		session_data['game_mode'] = 'add'
		session_data['user_name'] = 'TestUser'
		session_data.save()
		response = self.client.get(reverse('quiz:question'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "=")

	def test_submit_answer_view(self):
		# Simulate a full quiz flow
		from .models import QuizSession
		session = QuizSession.objects.create()
		session_id = session.id
		session_data = self.client.session
		session_data['quiz_session_id'] = session_id
		session_data['game_mode'] = 'add'
		session_data['user_name'] = 'TestUser'
		session_data.save()
		# Get a question to set current_answer
		response = self.client.get(reverse('quiz:question'))
		self.assertEqual(response.status_code, 200)
		# Extract answer from session
		answer = self.client.session.get('current_answer')
		response = self.client.post(reverse('quiz:submit_answer'), {'answer': str(answer)})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Correct")

	def test_what_time_is_it_main_game(self):
		# Setup session for what_time_is_it main game
		self.client.session['user_name'] = 'TestUser'
		self.client.session.save()
		response = self.client.get(reverse('quiz:what_time'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "What Time Is It?")

	def test_basic_questions_view(self):
		# Setup session for basic_questions view
		self.client.session['user_name'] = 'TestUser'
		self.client.session.save()
		response = self.client.get(reverse('quiz:basic_questions'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Basic Questions")
	def setUp(self):
		self.client = Client()

	def test_home_view(self):
		response = self.client.get(reverse('quiz:home'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Fun Learning for Kids")

	def test_colors_shapes_view(self):
		response = self.client.get(reverse('quiz:colors_shapes'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Colors & Shapes Learning Game")

	def test_spelling_game_view_get(self):
		response = self.client.get(reverse('quiz:spelling'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Spelling Game")

	def test_what_time_is_it_name_entry(self):
		# Should show name entry form if no user_name in session
		response = self.client.get(reverse('quiz:what_time'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "please enter your name:")
