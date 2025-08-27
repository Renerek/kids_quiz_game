import random
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import MathQuestion, QuizSession
import datetime

# Sample spelling words for the game
SPELLING_WORDS = [
    "apple", "banana", "orange", "elephant", "giraffe", "school", "friend", "beautiful", "family", "computer",
    "house", "tiger", "lion", "monkey", "zebra", "dolphin", "whale", "castle", "prince", "princess",
    "king", "queen", "knight", "dragon", "flower", "garden", "river", "mountain", "ocean", "forest",
    "pencil", "teacher", "student", "book", "paper", "scissors", "table", "chair", "window", "door",
    "rainbow", "cloud", "sunshine", "rain", "snow", "winter", "summer", "spring", "autumn", "playground"
]

def spelling_game(request):
    if request.method == 'POST':
        word = request.session.get('current_spelling_word', '').lower()
        user_spelling = request.POST.get('spelling', '').strip().lower()
        result = user_spelling == word
        return render(request, 'quiz/spelling.html', {'word': word, 'result': result})

    # Generate a new word for GET requests
    word = random.choice(SPELLING_WORDS)
    request.session['current_spelling_word'] = word
    return render(request, 'quiz/spelling.html', {'word': word})

def home(request):
	return render(request, 'quiz/home.html')

def start_quiz(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Player')
        request.session['user_name'] = name
        mode = request.POST.get('mode', 'mixed')
        session = QuizSession.objects.create(user=request.user if request.user.is_authenticated else None)
        request.session['quiz_session_id'] = session.id
        request.session['game_mode'] = mode
        return redirect('quiz:question')
    return render(request, 'quiz/start.html')

def question(request):
    session_id = request.session.get('quiz_session_id')
    session = QuizSession.objects.get(id=session_id)
    mode = request.session.get('game_mode', 'mixed')
    user_name = request.session.get('user_name', 'Player')
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    if mode == 'add':
        answer = a + b
        qtext = f"{a} + {b} = ?"
    elif mode == 'sub':
        if b > a:
            a, b = b, a
        answer = a - b
        qtext = f"{a} - {b} = ?"
    else:
        op = random.choice(['+', '-'])
        if op == '+':
            answer = a + b
            qtext = f"{a} + {b} = ?"
        else:
            if b > a:
                a, b = b, a
            answer = a - b
            qtext = f"{a} - {b} = ?"
    request.session['current_answer'] = answer
    return render(request, 'quiz/question.html', {'question': qtext, 'user_name': user_name})

def submit_answer(request):
    if request.method == 'POST':
        timeout = request.POST.get('timeout', 'false') == 'true'
        if timeout:
            return render(request, 'quiz/result.html', {'result': 'timeout'})

        answer_str = request.POST.get('answer', None)
        correct_answer = request.session.get('current_answer')
        try:
            user_answer = int(answer_str)
            result = user_answer == correct_answer
        except (TypeError, ValueError):
            result = False
        return render(request, 'quiz/result.html', {'result': result, 'correct_answer': correct_answer})
    return redirect('quiz:question')

def what_time_is_it(request):
    # Handle name submission first
    if 'user_name' not in request.session and request.method == 'POST' and 'name_submit' in request.POST:
        name = request.POST.get('name', 'Player')
        request.session['user_name'] = name
        return redirect('quiz:what_time')
    
    # If no name yet, show name entry form
    if 'user_name' not in request.session:
        return render(request, 'quiz/time_name_entry.html')
    
    # Generate random hour and minute for the clock
    hour = random.randint(1, 12)
    minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    clock_time = f"{hour}:{minute:02d}"
    
    result = None
    correct_time = None
    
    if request.method == 'POST':
        user_time = request.POST.get('user_time', '')
        clock_time = request.POST.get('clock_time', '')
        try:
            hour, minute = map(int, clock_time.split(':'))
            correct_time = f"{hour}:{minute:02d}"
            result = user_time == correct_time
        except (ValueError, TypeError):
            result = False
            correct_time = clock_time
        
        # Generate new time for next question
        hour = random.randint(1, 12)
        minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
        clock_time = f"{hour}:{minute:02d}"
    
    # Create digital clock display
    hour_str = str(hour)
    minute_str = f"{minute:02d}"
    
    return render(request, 'quiz/what_time_is_it.html', {
        'hour': hour,
        'minute': minute,
        'hour_str': hour_str,
        'minute_str': minute_str,
        'clock_time': clock_time,
        'result': result,
        'correct_time': correct_time,
        'user_name': request.session.get('user_name', 'Player')
    })

def basic_questions(request):
    # Handle name submission first
    if 'user_name' not in request.session and request.method == 'POST' and 'name_submit' in request.POST:
        name = request.POST.get('name', 'Player')
        request.session['user_name'] = name
        return redirect('quiz:basic_questions')
    
    # If no name yet, show name entry form
    if 'user_name' not in request.session:
        return render(request, 'quiz/basic_questions_name_entry.html')
    
    questions = [
        "How old are you?",
        "What is your father's name?",
        "What is your mother's name?",
        "How many brothers do you have?",
        "How many sisters do you have?",
        "What is your favorite color?",
        "What is your favorite animal?",
        "What is your favorite food?",
        "What is your teacher's name?",
        "What is your best friend's name?",
        "What is your favorite game?",
        "What is your favorite toy?",
        "What is your favorite book?",
        "What is your favorite subject in school?",
        "What do you want to be when you grow up?",
        "What is your favorite place to visit?",
        "What is your favorite TV show?",
        "What is your favorite movie?",
        "Do you have any pets? What are they?",
        "What makes you happy?"
    ]
    
    question_index = int(request.GET.get('q', 0))
    if question_index >= len(questions):
        # All questions answered, show results
        return render(request, 'quiz/basic_questions_result.html', {'answers': request.session.get('answers', {})})
    
    current_question = questions[question_index]
    
    if request.method == 'POST':
        answer = request.POST.get('answer', '')
        answers = request.session.get('answers', {})
        answers[current_question] = answer
        request.session['answers'] = answers
        
        # Move to next question
        next_index = question_index + 1
        return redirect(f'/quiz/basic-questions/?q={next_index}')
    
    return render(request, 'quiz/basic_questions.html', {
        'question': current_question, 
        'question_index': question_index,
        'total_questions': len(questions),
        'user_name': request.session.get('user_name', 'Player')
    })
