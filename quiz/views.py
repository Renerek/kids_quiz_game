import os
import random

# Animal name, image filename, and summary (3 sentences)
animals = [
    ("Snake", "snake.png", "This animal is a long, legless reptile that slithers on the ground. Most are harmless, but some are venomous. They are found in many habitats around the world."),
    ("Cheetah", "cheetah.png", "This animal is the fastest land animal, capable of running up to 70 mph. It has a slender body and distinctive black spots. They are wild cats found in Africa."),
    ("Cow", "cow.png", "This animal is a large, gentle farm animal raised for milk and meat. They are social animals and often live in herds. They are important in agriculture worldwide."),
    ("Crocodile", "crocodile.png", "This animal is a large reptile that lives in rivers and lakes. It has powerful jaws and is an excellent swimmer. These animals are ancient and have existed for millions of years."),
    ("Donkey", "donkey.png", "This animal is sturdy and known for its strength and endurance. They are often used as working animals on farms. They have long ears and a friendly nature."),
    ("Goat", "goat.png", "This animal is playful and curious, raised for milk, meat, and fiber. They can climb steep hills and rocky terrain. They are found on farms all over the world."),
    ("Pig", "pig.png", "This animal is intelligent and social, and loves to root in the ground. They are raised for their meat, called pork. They can be found on farms and sometimes as pets."),
    ("Rat", "rat.png", "This animal is small and clever, living in many environments. They are known for their adaptability and intelligence. Some people keep them as pets."),
    ("Sheep", "sheep.png", "This animal is gentle and raised for its wool, meat, and milk. They live in flocks and graze on grass. They have been domesticated for thousands of years."),
    ("Lion", "lion.png", "This animal is known as the king of the jungle. They live in groups called prides and are powerful hunters. They are wild animals found in Africa."),
    ("Tiger", "tiger.png", "This animal is the largest wild cat in the world. It has orange fur with black stripes and is an excellent swimmer. They live in forests and grasslands in Asia."),
    ("Elephant", "elephant.png", "This animal is the largest land animal on Earth. It has a long trunk and big ears. They are intelligent and live in family groups."),
    ("Giraffe", "giraffe.png", "This animal is the tallest in the world. It has a long neck to reach leaves high in trees. They live in the savannas of Africa."),
    ("Zebra", "zebra.png", "This animal is known for its black and white stripes. Each pattern is unique. They live in herds on the African plains."),
    ("Bear", "bear.png", "This animal is large and strong, found in forests and mountains. They eat both plants and animals. Some hibernate during the winter."),
    ("Monkey", "monkey.png", "This animal is playful and intelligent, living in trees. They use their tails and hands to swing and climb. They are found in many parts of the world."),
    ("Kangaroo", "kangaroo.png", "This animal is a marsupial from Australia. It has strong legs for jumping and carries its babies in a pouch. They live in groups called mobs."),
    ("Panda", "panda.png", "This animal is black and white and eats mostly bamboo. They are native to China and are known for their gentle nature. They are a symbol of wildlife conservation."),
    ("Fox", "fox.png", "This animal is small and clever with a bushy tail. They are known for their cunning and adaptability. They live in forests, grasslands, and even cities."),
    ("Rabbit", "rabbit.png", "This animal is small and gentle with long ears. They love to hop and eat vegetables. They can be found in the wild and as pets."),
    ("Dog", "dog.png", "This animal is loyal and friendly, often called man's best friend. They come in many breeds and sizes. They are kept as pets and help people in many ways."),
    ("Cat", "cat.png", "This animal is graceful and independent, and loves to play and nap. They are popular pets around the world. They can be affectionate and curious."),
    ("Horse", "horse.png", "This animal is strong and fast, used for riding and work. They have been companions to humans for thousands of years. They live on farms and in the wild."),
    ("Penguin", "penguin.png", "This animal is a bird that cannot fly but is an excellent swimmer. They live in cold regions like Antarctica. They have black and white feathers and waddle when they walk."),
    ("Owl", "owl.png", "This animal is a bird of prey with large eyes and excellent night vision. They are known for their hooting calls. They hunt small animals and live in forests and fields."),
    ("Frog", "frog.png", "This animal is a small amphibian that lives near water. It has smooth skin and long legs for jumping. They lay eggs in ponds and eat insects."),
    ("Turtle", "turtle.png", "This animal is a reptile with a hard shell that protects its body. They can live on land or in water. They move slowly and can live for many years."),
    ("Dolphin", "dolphin.png", "This animal is intelligent and playful, and lives in the ocean. They communicate with clicks and whistles. They are known for their friendly nature."),
    ("Parrot", "parrot.png", "This animal is a colorful bird that can mimic sounds and speech. They live in tropical regions and eat fruits and seeds. They are popular pets because of their intelligence.")
]

def animals_game(request):
    animal_dict = {a[0]: a for a in animals}
    if request.method == "POST":
        correct_animal = request.session.get("current_animal_name")
        answer = request.POST.get("answer")
        result = (answer == correct_animal)
        if result:
            # On correct, just show feedback - let JavaScript handle the transition
            animal_name = correct_animal
            animal = animal_dict[animal_name]
            animal_image_url = os.path.join("quiz/images/animals", animal[1])
            options = request.session.get("current_animal_options", [])
            summary = animal[2].replace(animal_name, "...")
            return render(request, "quiz/animals_game.html", {
                "animal_image_url": f"/static/{animal_image_url}",
                "options": options,
                "result": result,
                "summary": summary,
                "animal_name": animal_name,
                "user_answer": answer,
                "correct_answer": correct_animal,
            })
        else:
            # Show same animal and hint again
            animal_name = correct_animal
            animal = animal_dict[animal_name]
            animal_image_url = os.path.join("quiz/images/animals", animal[1])
            options = request.session.get("current_animal_options")
            if not options:
                options = [animal_name]
                while len(options) < 4:
                    opt = random.choice(animals)[0]
                    if opt not in options:
                        options.append(opt)
                random.shuffle(options)
            summary = animal[2].replace(animal_name, "...")
            return render(request, "quiz/animals_game.html", {
                "animal_image_url": f"/static/{animal_image_url}",
                "options": options,
                "result": result,
                "summary": summary,
                "animal_name": animal_name,
                "user_answer": answer,
                "correct_answer": correct_animal,
            })
    # GET: show new animal
    animal = random.choice(animals)
    request.session["current_animal_name"] = animal[0]
    animal_image_url = os.path.join("quiz/images/animals", animal[1])
    options = [animal[0]]
    while len(options) < 4:
        opt = random.choice(animals)[0]
        if opt not in options:
            options.append(opt)
    random.shuffle(options)
    request.session["current_animal_options"] = options
    animal_name = animal[0]
    summary = animal[2].replace(animal_name, "...")
    return render(request, "quiz/animals_game.html", {
        "animal_image_url": f"/static/{animal_image_url}",
        "options": options,
        "result": None,
        "summary": summary,
        "animal_name": animal_name,
    })

 # Fruit name, image filename, and summary (3 sentences)
fruits = [
        ("Apple", "apple.png", "This fruit is sweet and crunchy, and comes in red, green, or yellow. They are great for snacks and are used in many desserts. They are rich in fiber and vitamins."),
        ("Avocado", "avocado.png", "This fruit is creamy with a large seed inside. It is packed with healthy fats and nutrients. It is often used in salads and spreads like guacamole."),
        ("Banana", "banana.png", "This fruit is long and yellow with a soft, sweet inside. It is easy to peel and makes a great snack. It is a good source of potassium."),
        ("Blackberry", "blackberry.png", "This fruit is small and dark purple, growing on bushes. It is juicy and sweet with a slightly tart flavor. It is rich in vitamins and antioxidants."),
        ("Blue Grapes", "blue_grapes.png", "This fruit is small and round, growing in clusters. It is sweet and juicy, perfect for eating fresh or making juice. Grapes are also used to make raisins and wine."),
        ("Cherry", "cherry.png", "This fruit is small and round, and can be red or dark purple. It is sweet or tart and often used in pies and desserts. It is high in antioxidants."),
        ("Coconut", "coconut.png", "This fruit has a hard, brown shell and white, edible flesh inside. The water and milk from it are refreshing drinks. It grows on palm trees in tropical regions."),
        ("Cranberry", "cranberry.png", "This fruit is small and red with a tart taste. It is often used in juices and sauces. It is known for its health benefits, especially for the urinary tract."),
        ("Dragon Fruit", "dragon_fruit.png", "This fruit has a bright pink skin and white or red flesh with tiny black seeds. It is mildly sweet and very refreshing. It is also called pitaya and grows in warm climates."),
        ("Kiwi", "kiwi.png", "This fruit is small and brown with fuzzy skin and bright green flesh. It has a sweet and tangy flavor. It is rich in vitamin C and fiber."),
        ("Lemon", "lemon.png", "This fruit is yellow and sour, used to add flavor to food and drinks. It is high in vitamin C. Its juice is often used in cooking and baking."),
        ("Lime", "lime.png", "This fruit is small and green with a tart taste. It is used in drinks, desserts, and savory dishes. It is a good source of vitamin C."),
        ("Mango", "mango.png", "This fruit is juicy and tropical with orange flesh. It is sweet and fragrant, often called the king of fruits. It is enjoyed fresh or in smoothies and desserts."),
        ("Orange", "orange.png", "This fruit is round and orange-colored. It is juicy and sweet, perfect for eating or making juice. It is famous for its vitamin C content."),
        ("Papaya", "papaya.png", "This fruit is tropical with orange flesh and black seeds. It is sweet and soft, great for breakfast or smoothies. It helps with digestion and is rich in vitamins."),
        ("Passion Fruit", "passion_fruit.png", "This fruit has a tough purple skin and yellow, juicy seeds inside. It has a unique, sweet-tart flavor. It is used in drinks, desserts, and jams."),
        ("Peach", "peach.png", "This fruit is round and fuzzy with juicy, sweet flesh. It is delicious fresh or in pies and cobblers. It is a good source of vitamins A and C."),
        ("Pear", "pear.png", "This fruit is bell-shaped with soft, sweet flesh. It comes in green, yellow, or red varieties. It is great for snacking and baking."),
        ("Pineapple", "pineapple.png", "This fruit is tropical with spiky skin and sweet, yellow flesh. It is juicy and tangy, perfect for fruit salads. It is rich in vitamin C and enzymes."),
        ("Plum", "plum.png", "This fruit is small and round with smooth skin and a pit inside. It can be sweet or tart and comes in many colors. It is good for digestion and makes a tasty snack."),
        ("Pomegranate", "pomegranate.png", "This fruit has thick, red skin and is filled with juicy seeds. The seeds are sweet and tart, packed with antioxidants. It is often eaten fresh or juiced."),
        ("Strawberry", "strawberry.png", "This fruit is bright red and heart-shaped with tiny seeds on the outside. It is sweet and juicy, perfect for desserts. It is high in vitamin C."),
        ("Tomato", "tomato.png", "This fruit is red or yellow and often used as a vegetable. It is juicy and slightly tangy, used in salads, sauces, and soups. It is rich in vitamins and antioxidants."),
        ("Watermelon", "watermelon.png", "This fruit is large and green with sweet, juicy red flesh. It is very refreshing, especially in summer. It is mostly water and helps keep you hydrated."),
        ("Grapes", "grapes.png", "This fruit is small and round, growing in bunches. It can be green, red, or purple and is sweet and juicy. It is eaten fresh, dried as raisins, or made into juice."),
        ("Blueberries", "blueberries.png", "This fruit is tiny and blue-purple, growing on bushes. It is sweet and packed with antioxidants. It is great in cereals, muffins, and smoothies."),
        ("Raspberry", "raspberry.png", "This fruit is small and red or black with a sweet-tart flavor. It is soft and juicy, perfect for desserts. It is high in fiber and vitamins."),
        ("Pumpkin", "pumpkin.png", "This fruit is large and round with orange skin and flesh. It is used in soups, pies, and decorations for Halloween. It is rich in vitamins and fiber.")
    ]
    
def fruits_game(request):
    fruit_dict = {f[0]: f for f in fruits}
    if request.method == "POST":
        correct_fruit = request.session.get("current_fruit_name")
        answer = request.POST.get("answer")
        result = (answer == correct_fruit)
        if result:
            # On correct, just show feedback - let JavaScript handle the transition
            fruit_name = correct_fruit
            fruit = fruit_dict[fruit_name]
            fruit_image_url = os.path.join("quiz/images/fruits", fruit[1])
            options = request.session.get("current_fruit_options", [])
            summary = fruit[2]
            return render(request, "quiz/fruits_game.html", {
                "fruit_image_url": f"/static/{fruit_image_url}",
                "options": options,
                "result": result,
                "summary": summary,
                "fruit_name": fruit_name,
                "user_answer": answer,
                "correct_answer": correct_fruit,
            })
        else:
            # Show same fruit and hint again
            fruit_name = correct_fruit
            fruit = fruit_dict[fruit_name]
            fruit_image_url = os.path.join("quiz/images/fruits", fruit[1])
            options = request.session.get("current_fruit_options")
            if not options:
                options = [fruit_name]
                while len(options) < 4:
                    opt = random.choice(fruits)[0]
                    if opt not in options:
                        options.append(opt)
                random.shuffle(options)
            summary = fruit[2]
            return render(request, "quiz/fruits_game.html", {
                "fruit_image_url": f"/static/{fruit_image_url}",
                "options": options,
                "result": result,
                "summary": summary,
                "fruit_name": fruit_name,
                "user_answer": answer,
                "correct_answer": correct_fruit,
            })
    else:
        # GET: show new fruit
        fruit = random.choice(fruits)
        request.session["current_fruit_name"] = fruit[0]
        fruit_image_url = os.path.join("quiz/images/fruits", fruit[1])
        options = [fruit[0]]
        while len(options) < 4:
            opt = random.choice(fruits)[0]
            if opt not in options:
                options.append(opt)
        random.shuffle(options)
        request.session["current_fruit_options"] = options
        fruit_name = fruit[0]
        summary = fruit[2]
        return render(request, "quiz/fruits_game.html", {
            "fruit_image_url": f"/static/{fruit_image_url}",
            "options": options,
            "result": None,
            "summary": summary,
            "fruit_name": fruit_name,
        })
from django.core.mail import send_mail
from django.conf import settings
def contact(request):
    sent = False
    if request.method == "POST":
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        full_message = f"From: {email}\nSubject: {subject}\nMessage:\n{message}"
        send_mail(
            f"Contact Form: {subject}",
            full_message,
            settings.DEFAULT_FROM_EMAIL,
            ["ntumngiar@gmail.com"],
            fail_silently=False,
        )
        sent = True
    return render(request, "quiz/contact.html", {"sent": sent})

def login(request):
    return render(request, "quiz/login.html")

import random
from django.shortcuts import redirect, render

def colors_shapes(request):
    return render(request, "quiz/colors_shapes.html")

from .models import QuizSession

# Sample spelling words for the game
SPELLING_WORDS = [
    "apple",
    "banana",
    "orange",
    "elephant",
    "giraffe",
    "school",
    "friend",
    "cloud",
    "sunshine",
    "rain",
    "snow",
    "winter",
    "summer",
    "spring",
    "autumn",
    "playground",
]


def spelling_game(request):
    if request.method == "POST":
        word = request.session.get("current_spelling_word", "").lower()
        user_spelling = request.POST.get("spelling", "").strip().lower()
        result = user_spelling == word
        if result:
            # On correct, just show feedback - let JavaScript handle the transition
            return render(
                request,
                "quiz/spelling.html",
                {"word": word, "result": result},
            )
        else:
            # On incorrect, show same word again
            return render(
                request,
                "quiz/spelling.html",
                {"word": word, "result": result},
            )

    # Generate a new word for GET requests
    word = random.choice(SPELLING_WORDS)
    request.session["current_spelling_word"] = word
    return render(
        request,
        "quiz/spelling.html",
        {"word": word},
    )


def home(request):
    return render(
        request,
        "quiz/home.html",
    )


def start_quiz(request):
    if request.method == "POST":
        name = request.POST.get("name", "Player")
        request.session["user_name"] = name
        mode = request.POST.get("mode", "mixed")
        difficulty = request.POST.get("difficulty", "easy")
        session = QuizSession.objects.create(
            user=request.user if request.user.is_authenticated else None
        )
        request.session["quiz_session_id"] = session.id
        request.session["game_mode"] = mode
        request.session["difficulty"] = difficulty
        return redirect("quiz:question")
    return render(request, "quiz/start.html")


def question(request):
    session_id = request.session.get("quiz_session_id")
    session = QuizSession.objects.get(id=session_id)
    mode = request.session.get("game_mode", "mixed")
    user_name = request.session.get("user_name", "Player")
    difficulty = request.session.get("difficulty", "easy")
    # Set number range and time limit by difficulty
    if difficulty == "easy":
        min_num, max_num = 1, 10
        time_limit = 60
    elif difficulty == "medium":
        min_num, max_num = 5, 30
        time_limit = 30
    else:  # hard
        min_num, max_num = 10, 100
        time_limit = 15

    a = random.randint(min_num, max_num)
    b = random.randint(min_num, max_num)
    if mode == "add":
        answer = a + b
        qtext = f"{a} + {b} = ?"
    elif mode == "sub":
        if b > a:
            a, b = b, a
        answer = a - b
        qtext = f"{a} - {b} = ?"
    elif mode == "mul":
        # For multiplication, use smaller numbers to keep answers reasonable
        if difficulty == "easy":
            a = random.randint(1, 5)
            b = random.randint(1, 5)
        elif difficulty == "medium":
            a = random.randint(2, 10)
            b = random.randint(2, 10)
        else:  # hard
            a = random.randint(5, 15)
            b = random.randint(5, 15)
        answer = a * b
        qtext = f"{a} × {b} = ?"
    elif mode == "div":
        # For division, ensure clean division (no remainders)
        if difficulty == "easy":
            b = random.randint(2, 5)
            answer = random.randint(2, 10)
        elif difficulty == "medium":
            b = random.randint(3, 8)
            answer = random.randint(3, 15)
        else:  # hard
            b = random.randint(4, 12)
            answer = random.randint(5, 20)
        a = answer * b
        qtext = f"{a} ÷ {b} = ?"
    else:
        # Mixed mode - choose random operation
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
            if difficulty == "easy":
                a = random.randint(1, 5)
                b = random.randint(1, 5)
            elif difficulty == "medium":
                a = random.randint(2, 10)
                b = random.randint(2, 10)
            else:  # hard
                a = random.randint(5, 15)
                b = random.randint(5, 15)
            answer = a * b
            qtext = f"{a} × {b} = ?"
        else:  # ÷
            # Ensure clean division
            if difficulty == "easy":
                b = random.randint(2, 5)
                answer = random.randint(2, 10)
            elif difficulty == "medium":
                b = random.randint(3, 8)
                answer = random.randint(3, 15)
            else:  # hard
                b = random.randint(4, 12)
                answer = random.randint(5, 20)
            a = answer * b
            qtext = f"{a} ÷ {b} = ?"
    request.session["current_answer"] = answer
    request.session["current_question"] = qtext
    return render(
        request,
        "quiz/question.html",
        {
            "question": qtext,
            "user_name": user_name,
            "difficulty": difficulty,
            "time_limit": time_limit,
        },
    )


def submit_answer(request):
    if request.method == "POST":
        timeout = request.POST.get("timeout", "false") == "true"
        correct_answer = request.session.get("current_answer")
        if timeout:
            return render(request, "quiz/result.html", {"result": "timeout", "correct_answer": correct_answer})

        answer_str = request.POST.get("answer", None)
        try:
            user_answer = int(answer_str)
            result = user_answer == correct_answer
        except (TypeError, ValueError):
            result = False
        
        if result:
            # Correct answer - go to result page
            return render(
                request,
                "quiz/result.html",
                {"result": result, "correct_answer": correct_answer},
            )
        else:
            # Wrong answer - stay on question page with feedback
            session_id = request.session.get("quiz_session_id")
            session = QuizSession.objects.get(id=session_id)
            mode = request.session.get("game_mode", "mixed")
            user_name = request.session.get("user_name", "Player")
            difficulty = request.session.get("difficulty", "easy")
            
            # Get time limit for current difficulty
            if difficulty == "easy":
                time_limit = 60
            elif difficulty == "medium":
                time_limit = 30
            else:  # hard
                time_limit = 15
            
            # Get current question from session
            current_question = request.session.get("current_question", "")
            
            return render(
                request,
                "quiz/question.html",
                {
                    "question": current_question,
                    "user_name": user_name,
                    "difficulty": difficulty,
                    "time_limit": time_limit,
                    "wrong_answer": True,
                    "user_answer": user_answer if 'user_answer' in locals() else answer_str,
                },
            )
    return redirect("quiz:question")


def what_time_is_it(request):
    # Handle name submission first
    if (
        "user_name" not in request.session
        and request.method == "POST"
        and "name_submit" in request.POST
    ):
        name = request.POST.get("name", "Player")
        request.session["user_name"] = name
        return redirect("quiz:what_time")

    # If no name yet, show name entry form
    if "user_name" not in request.session:
        return render(request, "quiz/time_name_entry.html")

    # Generate random hour and minute for the clock
    hour = random.randint(1, 12)
    minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    clock_time = f"{hour}:{minute:02d}"

    result = None
    correct_time = None
    choices = []

    # Track attempts in session
    if 'time_attempts' not in request.session:
        request.session['time_attempts'] = 0

    if request.method == "POST":
        user_choice = request.POST.get("user_choice", "")
        clock_time = request.POST.get("clock_time", "")
        try:
            hour, minute = map(int, clock_time.split(":"))
            correct_time = f"{hour}:{minute:02d}"
            if user_choice == correct_time:
                result = 'correct'
                request.session['time_attempts'] = 0
            else:
                request.session['time_attempts'] += 1
                if request.session['time_attempts'] == 1:
                    result = 'incorrect'  # allow retry
                else:
                    result = 'show_answer'  # show correct answer and reset
                    request.session['time_attempts'] = 0
        except (ValueError, TypeError):
            result = 'show_answer'
            correct_time = clock_time
            request.session['time_attempts'] = 0

        # Only generate new time if it's a GET request (after JavaScript redirect)
        # For POST, just show feedback with current time
        if result != 'correct' and result != 'show_answer':
            # Keep the current time for incorrect answers that allow retry
            pass
        elif result == 'correct' or result == 'show_answer':
            # Just show feedback, let JavaScript handle the transition
            pass

    # Generate 3 distractor choices
    correct = f"{hour}:{minute:02d}"
    distractors = set()
    while len(distractors) < 3:
        dhour = random.randint(1, 12)
        dminute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
        dstr = f"{dhour}:{dminute:02d}"
        if dstr != correct:
            distractors.add(dstr)
    choices = list(distractors) + [correct]
    random.shuffle(choices)

    hour_str = str(hour)
    minute_str = f"{minute:02d}"

    return render(
        request,
        "quiz/what_time_is_it.html",
        {
            "hour": hour,
            "minute": minute,
            "hour_str": hour_str,
            "minute_str": minute_str,
            "clock_time": clock_time,
            "result": result,
            "correct_time": correct_time,
            "user_name": request.session.get("user_name", "Player"),
            "choices": choices,
        },
    )


def basic_questions(request):
    # Handle name submission first
    if (
        "user_name" not in request.session
        and request.method == "POST"
        and "name_submit" in request.POST
    ):
        name = request.POST.get("name", "Player")
        request.session["user_name"] = name
        return redirect("quiz:basic_questions")

    # If no name yet, show name entry form
    if "user_name" not in request.session:
        return render(request, "quiz/basic_questions_name_entry.html")

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
        "What makes you happy?",
    ]

    question_index = int(request.GET.get("q", 0))
    if question_index >= len(questions):
        # All questions answered, show results
        return render(
            request,
            "quiz/basic_questions_result.html",
            {"answers": request.session.get("answers", {})},
        )

    current_question = questions[question_index]

    if request.method == "POST":
        answer = request.POST.get("answer", "")
        answers = request.session.get("answers", {})
        answers[current_question] = answer
        request.session["answers"] = answers

        # Move to next question
        next_index = question_index + 1
        return redirect(f"/quiz/basic-questions/?q={next_index}")

    return render(
        request,
        "quiz/basic_questions.html",
        {
            "question": current_question,
            "question_index": question_index,
            "total_questions": len(questions),
            "user_name": request.session.get("user_name", "Player"),
        },
    )
