from django.shortcuts import render
from .views import animals_game, animals, fruits, SPELLING_WORDS
import random
def mixed_game(request):
    # List of game types
    game_types = ["math", "animal", "fruit", "spelling", "time", "basic"]
    # Only pick a new question if GET or last answer was correct (or first load)
    pick_new = request.method == "GET" or request.session.get("mixed_correct", True)
    if pick_new:
        game_type = random.choice(game_types)
        request.session["mixed_type"] = game_type
        request.session["mixed_correct"] = False
        # Prepare new question for the current type
        if game_type == "math":
            a, b = random.randint(1, 20), random.randint(1, 20)
            op = random.choice(["+", "-", "×", "÷"])
            if op == "+":
                answer = a + b
                qtext = f"{a} + {b} = ?"
            elif op == "-":
                if b > a:
                    a, b = b, a
                answer = a - b
                qtext = f"{a} - {b} = ?"
            elif op == "×":
                # Use smaller numbers for multiplication
                a = random.randint(1, 12)
                b = random.randint(1, 12)
                answer = a * b
                qtext = f"{a} × {b} = ?"
            else:  # ÷
                # Ensure clean division
                b = random.randint(2, 12)
                answer = random.randint(2, 15)
                a = answer * b
                qtext = f"{a} ÷ {b} = ?"
            request.session["mixed_math_answer"] = answer
            question_context = {"question": qtext, "game_type": "math"}
        elif game_type == "animal":
            animal = random.choice(animals)
            request.session["mixed_animal_name"] = animal[0]
            animal_image_url = f"/static/quiz/images/animals/{animal[1]}"
            options = [animal[0]]
            while len(options) < 4:
                opt = random.choice(animals)[0]
                if opt not in options:
                    options.append(opt)
            random.shuffle(options)
            question_context = {"animal_image_url": animal_image_url, "options": options, "summary": animal[2], "game_type": "animal"}
        elif game_type == "fruit":
            fruit = random.choice(fruits)
            request.session["mixed_fruit_name"] = fruit[0]
            fruit_image_url = f"/static/quiz/images/fruits/{fruit[1]}"
            options = [fruit[0]]
            while len(options) < 4:
                opt = random.choice(fruits)[0]
                if opt not in options:
                    options.append(opt)
            random.shuffle(options)
            question_context = {"fruit_image_url": fruit_image_url, "options": options, "summary": fruit[2], "game_type": "fruit"}
        elif game_type == "spelling":
            word = random.choice(SPELLING_WORDS)
            request.session["mixed_spelling_word"] = word
            question_context = {"spelling_word": word, "game_type": "spelling"}
        elif game_type == "time":
            hour = random.randint(1, 12)
            minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
            correct_time = f"{hour}:{minute:02d}"
            request.session["mixed_time"] = correct_time
            choices = set()
            while len(choices) < 3:
                dhour = random.randint(1, 12)
                dminute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
                dstr = f"{dhour}:{dminute:02d}"
                if dstr != correct_time:
                    choices.add(dstr)
            choices = list(choices) + [correct_time]
            random.shuffle(choices)
            question_context = {"clock_time": correct_time, "choices": choices, "game_type": "time"}
        elif game_type == "basic":
            questions = [
                "How old are you?", "What is your favorite color?", "What is your favorite animal?", "What is your favorite food?", "What is your favorite game?", "What is your favorite book?", "What do you want to be when you grow up?", "What makes you happy?"
            ]
            q = random.choice(questions)
            question_context = {"basic_question": q, "game_type": "basic"}
        request.session["mixed_question_context"] = question_context
    else:
        game_type = request.session.get("mixed_type", "math")
        question_context = request.session.get("mixed_question_context", {})

    context = dict(question_context)
    context["game_type"] = game_type
    context["result"] = None

    if request.method == "POST":
        # Check answer for the current type
        if game_type == "math":
            correct = request.session.get("mixed_math_answer")
            try:
                user = int(request.POST.get("answer", ""))
                context["result"] = (user == correct)
            except:
                context["result"] = False
            if context["result"]:
                request.session["mixed_correct"] = True
            else:
                request.session["mixed_correct"] = False
        elif game_type == "animal":
            correct = request.session.get("mixed_animal_name")
            user = request.POST.get("answer", "")
            context["result"] = (user == correct)
            if context["result"]:
                request.session["mixed_correct"] = True
            else:
                request.session["mixed_correct"] = False
        elif game_type == "fruit":
            correct = request.session.get("mixed_fruit_name")
            user = request.POST.get("answer", "")
            context["result"] = (user == correct)
            if context["result"]:
                request.session["mixed_correct"] = True
            else:
                request.session["mixed_correct"] = False
        elif game_type == "spelling":
            correct = request.session.get("mixed_spelling_word", "").lower()
            user = request.POST.get("spelling", "").strip().lower()
            context["result"] = (user == correct)
            if context["result"]:
                request.session["mixed_correct"] = True
            else:
                request.session["mixed_correct"] = False
        elif game_type == "time":
            correct = request.session.get("mixed_time")
            user = request.POST.get("user_choice", "")
            context["result"] = (user == correct)
            if context["result"]:
                request.session["mixed_correct"] = True
            else:
                request.session["mixed_correct"] = False
        elif game_type == "basic":
            # Accept any answer, just move to next
            context["result"] = True
            request.session["mixed_correct"] = True

    return render(request, "quiz/mixed_game.html", context)
