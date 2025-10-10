from django.shortcuts import render
from django.utils.translation import gettext as _
from .views import animals_game, animals, fruits, SPELLING_WORDS, MISSPELLED_WORDS, REARRANGE_WORDS
import random
from .models import UserStat

def mixed_game(request):
    # List of game types
    game_types = ["math", "animal", "fruit", "spelling", "time", "basic", "correct_spelling", "rearrange_spelling"]
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
            question_context = {"question": qtext, "game_type": "math", "math_answer": answer}
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
            question_context = {
                "animal_image_url": animal_image_url,
                "options": options,
                "summary": animal[2],
                "animal_name": animal[0],
                "game_type": "animal",
            }
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
            question_context = {
                "fruit_image_url": fruit_image_url,
                "options": options,
                "summary": fruit[2],
                "fruit_name": fruit[0],
                "game_type": "fruit",
            }
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
        elif game_type == "correct_spelling":
            entry = random.choice(MISSPELLED_WORDS)
            request.session["mixed_correct_spelling_entry"] = entry
            question_context = {
                "incorrect_word": entry["incorrect"],
                "hint": entry.get("hint"),
                "game_type": "correct_spelling",
            }
        elif game_type == "rearrange_spelling":
            entry = random.choice(REARRANGE_WORDS)
            word = entry["word"]
            if word:
                scrambled = ''.join(random.sample(word, len(word)))
                while scrambled.lower() == word.lower() and len(word) > 1:
                    scrambled = ''.join(random.sample(word, len(word)))
            else:
                scrambled = word
            request.session["mixed_rearrange_entry"] = {"word": word, "hint": entry.get("hint"), "scrambled": scrambled}
            question_context = {
                "scrambled_word": scrambled,
                "hint": entry.get("hint"),
                "game_type": "rearrange_spelling",
            }
        request.session["mixed_question_context"] = question_context
    else:
        game_type = request.session.get("mixed_type", "math")
        question_context = request.session.get("mixed_question_context", {})

    context = dict(question_context)
    context["game_type"] = game_type
    context["result"] = None

    if request.method == "POST":
        # Check answer for the current type
        feedback_message = ""
        if game_type == "math":
            correct = request.session.get("mixed_math_answer")
            try:
                user = int(request.POST.get("answer", ""))
                context["result"] = (user == correct)
                context["user_answer"] = user
            except:
                context["result"] = False
                context["user_answer"] = request.POST.get("answer", "")
            if context["result"]:
                request.session["mixed_correct"] = True
                feedback_message = _("Great math work! You nailed that answer.")
            else:
                request.session["mixed_correct"] = False
                feedback_message = _("Not quite yet. Try the math problem again.")
            context["correct_answer"] = correct
        elif game_type == "animal":
            correct = request.session.get("mixed_animal_name")
            user = request.POST.get("answer", "")
            context["result"] = (user == correct)
            context["animal_name"] = correct
            context["user_answer"] = user
            if context["result"]:
                request.session["mixed_correct"] = True
                feedback_message = _("Awesome! %(name)s is the right pick.") % {"name": correct}
            else:
                request.session["mixed_correct"] = False
                feedback_message = _("Give it another look. Which animal matches best?")
        elif game_type == "fruit":
            correct = request.session.get("mixed_fruit_name")
            user = request.POST.get("answer", "")
            context["result"] = (user == correct)
            context["fruit_name"] = correct
            context["user_answer"] = user
            if context["result"]:
                request.session["mixed_correct"] = True
                feedback_message = _("Yum! %(name)s is correct.") % {"name": correct}
            else:
                request.session["mixed_correct"] = False
                feedback_message = _("Try again. Which fruit do you think it is?")
        elif game_type == "spelling":
            correct = request.session.get("mixed_spelling_word", "").lower()
            user = request.POST.get("spelling", "").strip().lower()
            context["result"] = (user == correct)
            context["correct_word"] = request.session.get("mixed_spelling_word", "")
            context["user_answer"] = request.POST.get("spelling", "")
            if context["result"]:
                request.session["mixed_correct"] = True
                feedback_message = _("Perfect spelling! Keep it up.")
            else:
                request.session["mixed_correct"] = False
                feedback_message = _("Listen carefully and try spelling it again.")
        elif game_type == "time":
            correct = request.session.get("mixed_time")
            user = request.POST.get("user_choice", "")
            context["result"] = (user == correct)
            context["correct_time"] = correct
            context["user_answer"] = user
            if context["result"]:
                request.session["mixed_correct"] = True
                feedback_message = _("Nice job reading the clock!")
            else:
                request.session["mixed_correct"] = False
                feedback_message = _("Check the clock carefully and pick another time.")
        elif game_type == "basic":
            # Accept any answer, just move to next
            context["result"] = True
            context["user_answer"] = request.POST.get("answer", "")
            request.session["mixed_correct"] = True
            feedback_message = _("Thanks for sharing! Let's see what's next.")
        elif game_type == "correct_spelling":
            entry = request.session.get("mixed_correct_spelling_entry", {})
            expected = entry.get("correct", "")
            user = request.POST.get("correct_spelling", "").strip()
            context["result"] = (user.lower() == expected.lower()) if expected else False
            context["correct_word"] = expected
            context["attempt_word"] = entry.get("incorrect")
            context["user_answer"] = user
            request.session["mixed_correct"] = bool(context["result"])
            if context["result"]:
                feedback_message = _("Well done fixing the spelling of %(word)s.") % {"word": expected or entry.get("incorrect") or ""}
            else:
                feedback_message = _("Not yet. Fix the spelling and try once more.")
        elif game_type == "rearrange_spelling":
            entry = request.session.get("mixed_rearrange_entry", {})
            expected = entry.get("word", "")
            user = request.POST.get("rearranged_word", "").strip()
            context["result"] = (user.lower() == expected.lower()) if expected else False
            context["correct_word"] = expected
            context["user_answer"] = user
            request.session["mixed_correct"] = bool(context["result"])
            if context["result"]:
                feedback_message = _("Super unscrambling skills!")
            else:
                feedback_message = _("Keep rearranging those letters.")

        if not feedback_message:
            feedback_message = _("Great job! That answer is correct.") if context.get("result") else _("Almost there. Give it another try.")

        if feedback_message:
            context["feedback_message"] = feedback_message

        # Record stat for mixed game if authenticated and answer submitted
        if request.user.is_authenticated:
            UserStat.objects.create(
                user=request.user,
                game="mixed",
                score=1 if context.get("result") else 0,
                correct=1 if context.get("result") else 0,
                incorrect=0 if context.get("result") else 1,
                time_spent=0.0
            )

    return render(request, "quiz/mixed_game.html", context)
