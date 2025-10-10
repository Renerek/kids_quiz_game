def what_time_is_it(request):
    # Stats tracking for authenticated users
    from .models import UserStat

    # Always use user's profile name or username

    # Generate random hour and minute for the clock
    hour = random.randint(1, 12)
    minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    clock_time = f"{hour}:{minute:02d}"

    result = None
    correct_time = None
    choices = []
    feedback_overlay = None

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
                if request.user.is_authenticated:
                    UserStat.objects.create(
                        user=request.user,
                        game="time",
                        score=1,
                        correct=1,
                        incorrect=0,
                        time_spent=0.0
                    )
                feedback_overlay = {
                    "result": "correct",
                    "voice_message": f"Great job! {correct_time} matches the clock.",
                    "heading": "Correct!",
                    "subtitle": f"{correct_time} is exactly right.",
                    "body": "A new clock will appear in just a moment.",
                    "correct_delay": 3600,
                }
            else:
                request.session['time_attempts'] += 1
                if request.session['time_attempts'] == 1:
                    result = 'incorrect'  # allow retry
                    if request.user.is_authenticated:
                        UserStat.objects.create(
                            user=request.user,
                            game="time",
                            score=0,
                            correct=0,
                            incorrect=1,
                            time_spent=0.0
                        )
                    feedback_overlay = {
                        "result": "incorrect",
                        "voice_message": "Not quite. Look closely and try again.",
                        "heading": "Try again!",
                        "subtitle": "Check both the hour and minute hands.",
                        "body": "You have another chance to match the time.",
                        "reset_on_fade": True,
                        "incorrect_delay": 2600,
                    }
                else:
                    result = 'show_answer'  # show correct answer and reset
                    request.session['time_attempts'] = 0
                    if request.user.is_authenticated:
                        UserStat.objects.create(
                            user=request.user,
                            game="time",
                            score=0,
                            correct=0,
                            incorrect=1,
                            time_spent=0.0
                        )
                    feedback_overlay = {
                        "result": "correct",
                        "voice_message": f"The correct time was {correct_time}. Let's try another clock.",
                        "heading": "Here's the answer!",
                        "subtitle": f"The clock was showing {correct_time}.",
                        "body": "We'll show you a new clock right away.",
                        "correct_delay": 4200,
                    }
        except (ValueError, TypeError):
            result = 'show_answer'
            correct_time = clock_time
            request.session['time_attempts'] = 0
            if request.user.is_authenticated:
                UserStat.objects.create(
                    user=request.user,
                    game="time",
                    score=0,
                    correct=0,
                    incorrect=1,
                    time_spent=0.0
                )
            if clock_time:
                feedback_overlay = {
                    "result": "correct",
                    "voice_message": f"The correct time was {clock_time}. Let's try another clock.",
                    "heading": "Here's the answer!",
                    "subtitle": f"The clock was showing {clock_time}.",
                    "body": "We'll try a different time next.",
                    "correct_delay": 4200,
                }

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

    # If anonymous and no user_name in session, show name entry form
    if not request.user.is_authenticated and not request.session.get('user_name'):
        # If POST with a name, store the escaped name and reload
        if request.method == 'POST' and request.POST.get('name'):
            request.session['user_name'] = escape(request.POST.get('name').strip())
            return redirect('quiz:what_time')
        return render(request, 'quiz/time_name_entry.html')

    if request.user.is_authenticated:
        user_name = getattr(getattr(request.user, 'profile', None), 'first_name', request.user.username)
    else:
        user_name = request.session.get('user_name', 'Player')

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
            "user_name": user_name,
            "choices": choices,
            "feedback_overlay": feedback_overlay,
        },
    )
import logging
logger = logging.getLogger(__name__)
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
    # Guest play limit logic
    if not request.user.is_authenticated:
        guest_plays = request.session.get('guest_plays', 0)
        if guest_plays >= 3:
            return render(request, "quiz/guest_limit.html")
        request.session['guest_plays'] = guest_plays + 1
    animal_dict = {a[0]: a for a in animals}
    user_name = None
    if request.user.is_authenticated:
        user_name = getattr(getattr(request.user, 'profile', None), 'first_name', request.user.username)
    if request.method == "POST":
        correct_animal = request.session.get("current_animal_name")
        answer = request.POST.get("answer")
        result = (answer == correct_animal)
        if request.user.is_authenticated:
            UserStat.objects.create(
                user=request.user,
                game="animals",
                score=int(result),
                correct=1 if result else 0,
                incorrect=0 if result else 1,
                time_spent=0.0
            )
        if result:
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
                "user_name": user_name,
            })
        else:
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
                "user_name": user_name,
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
        "user_name": user_name,
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
    # Guest play limit logic
    if not request.user.is_authenticated:
        guest_plays = request.session.get('guest_plays', 0)
        if guest_plays >= 3:
            return render(request, "quiz/guest_limit.html")
        request.session['guest_plays'] = guest_plays + 1
    fruit_dict = {f[0]: f for f in fruits}
    user_name = None
    if request.user.is_authenticated:
        user_name = getattr(getattr(request.user, 'profile', None), 'first_name', request.user.username)
    if request.method == "POST":
        correct_fruit = request.session.get("current_fruit_name")
        answer = request.POST.get("answer")
        result = (answer == correct_fruit)
        if request.user.is_authenticated:
            UserStat.objects.create(
                user=request.user,
                game="fruits",
                score=int(result),
                correct=1 if result else 0,
                incorrect=0 if result else 1,
                time_spent=0.0
            )
        if result:
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
                "user_name": user_name,
            })
        else:
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
                "user_name": user_name,
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
            "user_name": user_name,
        })
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core import signing
from django.utils import timezone
from django.utils.html import escape
from django.urls import reverse

def contact(request):
    sent = False
    if request.method == "POST":
        email = request.POST.get("email")
        reason = request.POST.get("reason")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        full_message = f"From: {email}\nReason: {reason}\nSubject: {subject}\nMessage:\n{message}"
        # Send to site admin
        send_mail(
            f"Contact Form: {subject} [{reason}]",
            full_message,
            settings.DEFAULT_FROM_EMAIL,
            ["ntumngiar@gmail.com"],
            fail_silently=False,
        )
        # Send confirmation to user
        try:
            send_mail(
                subject="Thank you for contacting Kids Quiz Game!",
                message=(
                    "Hi,\n\n"
                    "Thank you for reaching out to us at Kids Quiz Game. We have received your message and one of our team members will get back to you soon at this email address.\n\n"
                    f"Reason: {reason}\n"
                    f"Your message: {message}\n\n"
                    "In the meantime, please continue enjoying our learning games and features!\n\n"
                    "If you have any more questions or need help, just reply to this email or use the Contact Us page again.\n\n"
                    "Best wishes,\nThe Kids Quiz Game Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"Contact confirmation email sent to {email}.")
        except Exception as e:
            logger.error(f"Failed to send contact confirmation email to {email}: {e}")
        sent = True
    return render(request, "quiz/contact.html", {"sent": sent})

def about_us(request):
    return render(request, "quiz/about.html")

def login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, "Account not verified yet. Please check your email or resend verification.")
            else:
                auth_login(request, user)
                messages.success(request, "Logged in successfully.")
                nxt = request.GET.get("next") or request.POST.get("next") or "quiz:home"
                return redirect(nxt)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "quiz/login.html")


EMAIL_VERIFICATION_MAX_AGE = 60 * 60 * 48  # 48 hours

def _build_verification_token(user: User) -> str:
    signer = signing.TimestampSigner()
    return signer.sign(user.pk)

def _verify_token(token: str):
    signer = signing.TimestampSigner()
    try:
        unsigned = signer.unsign(token, max_age=EMAIL_VERIFICATION_MAX_AGE)
        return int(unsigned)
    except (signing.BadSignature, ValueError, signing.SignatureExpired):
        return None


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        age_raw = request.POST.get("age", "").strip()
        city = request.POST.get("city", "").strip()
        country = request.POST.get("country", "").strip()
        age = None
        if age_raw:
            try:
                age = int(age_raw)
                if age < 0 or age > 120:
                    messages.error(request, "Age must be between 0 and 120.")
                    return render(request, "quiz/signup.html")
            except ValueError:
                messages.error(request, "Age must be a number.")
                return render(request, "quiz/signup.html")
        import re
        if not (username and password1 and password2 and email and first_name):
            messages.error(request, "Username, password, email, and first name are required.")
        elif password1 != password2:
            messages.error(request, "Passwords do not match.")
        elif len(password1) < 8 or not re.search(r'[A-Za-z]', password1) or not re.search(r'\d', password1):
            messages.error(request, "Password must be at least 8 characters long and contain both letters and numbers.")
        elif User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already taken. Please sign in or choose another.")
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already in use. Please sign in or use a different email.")
        else:
            user = User.objects.create_user(username=username, password=password1, email=email)
            user.is_active = False  # Require email verification
            user.save(update_fields=["is_active"])
            from .models import UserProfile
            UserProfile.objects.create(user=user, first_name=first_name, last_name=last_name, age=age, city=city, country=country)
            # Send verification email (returns verify_url)
            verify_url = _send_verification_email(request, user, first_name or username)
            # Send confirmation email with username
            from django.core.mail import send_mail
            try:
                contact_url = request.build_absolute_uri(reverse("quiz:contact"))
                context = {"display_name": (first_name or username), "username": username, "contact_url": contact_url, "verify_url": verify_url}
                text_body = render_to_string("quiz/emails/welcome_email.txt", context)
                html_body = render_to_string("quiz/emails/welcome_email.html", context)
                msg = EmailMultiAlternatives("Welcome to Kids Quiz Game!", text_body, settings.DEFAULT_FROM_EMAIL, [email])
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)
                logger.info(f"Confirmation email sent to {email} for user {username}.")
            except Exception as e:
                logger.error(f"Failed to send confirmation email to {email}: {e}")
            # Send admin notification
            try:
                from django.conf import settings
                admin_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
                if admin_email:
                    send_mail(
                        subject="New User Signup Notification",
                        message=f"A new user has signed up.\n\nUsername: {username}\nName: {first_name} {last_name}\nEmail: {email}",
                        from_email=None,
                        recipient_list=[admin_email],
                        fail_silently=False,
                    )
                    logger.info(f"Admin notified of new signup: {username} ({email})")
            except Exception as e:
                logger.error(f"Failed to send admin signup notification: {e}")
            messages.success(request, "Account created. Check your email to verify and activate your account.")
            return render(request, "quiz/verification_sent.html", {"email": email})
    return render(request, "quiz/signup.html")


def verify_email(request, token: str):
    user_id = _verify_token(token)
    if not user_id:
        return render(request, "quiz/verification_invalid.html")
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return render(request, "quiz/verification_invalid.html")
    if user.is_active:
        messages.info(request, "Account already verified.")
        return redirect("quiz:login")
    user.is_active = True
    user.save(update_fields=["is_active"])
    # Send confirmation email after verification
    from django.core.mail import send_mail
    profile_name = getattr(getattr(user, 'profile', None), 'name', user.username)
    try:
        # re-use welcome templates but with a verified message
        subject = "Your account is now verified!"
        context = {"display_name": profile_name, "username": user.username, "contact_url": request.build_absolute_uri(reverse('quiz:contact'))}
        text_body = f"Hi {profile_name},\n\nYour email has been verified and your account is now active. You can now log in and enjoy all features!"
        html_body = render_to_string("quiz/emails/welcome_email.html", context)
        msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Confirmation email sent to {user.email} after verification.")
    except Exception as e:
        logger.error(f"Failed to send confirmation email after verification to {user.email}: {e}")
    messages.success(request, "Email verified. You can now log in.")
    return render(request, "quiz/verification_success.html")


def _send_verification_email(request, user: User, display_name: str):
    token = _build_verification_token(user)
    verify_url = request.build_absolute_uri(reverse("quiz:verify_email", args=[token]))
    subject = "Welcome to Kids Quiz Game! Confirm your signup"
    contact_url = request.build_absolute_uri(reverse("quiz:contact"))
    context = {
        "display_name": display_name,
        "verify_url": verify_url,
        "contact_url": contact_url,
    }
    text_body = render_to_string("quiz/emails/verification_email.txt", context)
    html_body = render_to_string("quiz/emails/verification_email.html", context)
    try:
        msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Verification email sent to {user.email} for user {user.username}.")
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
    return verify_url


def resend_verification(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if not email:
            messages.error(request, "Email is required.")
            return render(request, "quiz/resend_verification.html")
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Avoid HTML in messages; let template append a signup link when requested.
            messages.error(request, "No account found with that email.")
            return render(request, "quiz/resend_verification.html", {"show_signup_link": True})
        if user.is_active:
            messages.info(request, "Account already verified. You can log in.")
            return redirect("quiz:login")
        profile_name = getattr(getattr(user, 'profile', None), 'name', user.username)
        _send_verification_email(request, user, profile_name)
        messages.success(request, "Verification email resent. Please check your inbox.")
        return render(request, "quiz/verification_sent.html", {"email": email, "resent": True})
    return render(request, "quiz/resend_verification.html")


def logout(request):
    if request.method == "POST":
        auth_logout(request)
        messages.info(request, "Logged out.")
        return redirect("quiz:home")
    # For safety, redirect on GET too (no stateful action)
    return redirect("quiz:home")

def profile(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    return render(request, "quiz/profile.html", {
        "user": user,
        "profile": profile,
    })

def update_account(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    message = None
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        age = request.POST.get("age", None)
        city = request.POST.get("city", "").strip()
        country = request.POST.get("country", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        profile_picture = request.FILES.get("profile_picture")

        # Update user fields
        if email and email != user.email:
            user.email = email
        if first_name:
            profile.first_name = first_name
        if last_name is not None:
            profile.last_name = last_name
        if age:
            try:
                profile.age = int(age)
            except ValueError:
                message = "Age must be a number."
        if city is not None:
            profile.city = city
        if country is not None:
            profile.country = country
        if profile_picture:
            profile.profile_picture = profile_picture
        if password1 or password2:
            if password1 != password2:
                message = "Passwords do not match."
            elif len(password1) < 8:
                message = "Password must be at least 8 characters."
            else:
                user.set_password(password1)
        if not message:
            user.save()
            profile.save()
            message = "Account updated successfully."
    return render(request, "quiz/update_account.html", {
        "user": user,
        "profile": profile,
        "message": message,
    })

def settings_view(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    message = None
    if request.method == "POST":
        # Profile setup
        first_name = request.POST.get("first_name", "").strip()
        age_group = request.POST.get("age_group", "")
        # Theme
        theme = request.POST.get("theme", "light")
        # Sound
        sound_music = request.POST.get("sound_music") == "on"
        sound_voice = request.POST.get("sound_voice") == "on"
        # Language
        language = request.POST.get("language", "en")

        if first_name:
            profile.first_name = first_name
        if age_group:
            profile.age_group = age_group
        profile.theme = theme
        profile.sound_music = sound_music
        profile.sound_voice = sound_voice
        profile.language = language
        profile.save()
        # Update session for immediate theme switch
        request.session['theme'] = theme
        message = "Preferences updated."

    # Use theme from profile or session for immediate effect
    theme = getattr(profile, 'theme', 'light')
    if 'theme' in request.session:
        theme = request.session['theme']
    return render(request, "quiz/settings.html", {
        "profile": profile,
        "message": message,
        "theme": theme,
        "LANGUAGES": [
            ("en", "English"), ("fr", "French"), ("es", "Spanish"), ("de", "German"),
            ("it", "Italian"), ("pt", "Portuguese"), ("ru", "Russian"), ("zh-hans", "Chinese (Simplified)"),
            ("ar", "Arabic"), ("sw", "Swahili"), ("yo", "Yoruba"), ("ig", "Igbo"), ("ha", "Hausa")
        ],
    })

import random
from django.shortcuts import redirect, render

def colors_shapes(request):
    user_name = None
    if request.user.is_authenticated:
        user_name = getattr(getattr(request.user, 'profile', None), 'first_name', request.user.username)
        # Always record stats when user visits this page (GET or POST)
        if not UserStat.objects.filter(user=request.user, game="colors_shapes").exists():
            UserStat.objects.create(
                user=request.user,
                game="colors_shapes",
                score=1,
                correct=1,
                incorrect=0,
                time_spent=0.0
            )
    return render(request, "quiz/colors_shapes.html", {"user_name": user_name})

from .models import QuizSession, UserStat

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

MISSPELLED_WORDS = [
    {"incorrect": "becuase", "correct": "because", "hint": "We use it to explain a reason."},
    {"incorrect": "frend", "correct": "friend", "hint": "Someone you like to play with."},
    {"incorrect": "famaly", "correct": "family", "hint": "People who live with you."},
    {"incorrect": "sckool", "correct": "school", "hint": "A place where you learn."},
    {"incorrect": "yello", "correct": "yellow", "hint": "A bright color like the sun."},
    {"incorrect": "animel", "correct": "animal", "hint": "A living creature like a dog or cat."},
    {"incorrect": "happie", "correct": "happy", "hint": "The way you feel when you smile."},
    {"incorrect": "brekfast", "correct": "breakfast", "hint": "The meal you eat in the morning."},
    {"incorrect": "tomorow", "correct": "tomorrow", "hint": "The day after today."},
    {"incorrect": "writting", "correct": "writing", "hint": "What you do with a pencil when making letters."},
]

REARRANGE_WORDS = [
    {"word": "pencil", "hint": "You use it to write."},
    {"word": "garden", "hint": "A place where flowers grow."},
    {"word": "planet", "hint": "Earth is one of these."},
    {"word": "turtle", "hint": "A slow animal with a shell."},
    {"word": "rocket", "hint": "It blasts off into space."},
    {"word": "bucket", "hint": "You can carry water with it."},
    {"word": "forest", "hint": "Many trees standing together."},
    {"word": "puzzle", "hint": "Pieces you fit together for fun."},
    {"word": "castle", "hint": "A big home for a king or queen."},
    {"word": "circus", "hint": "A fun show with clowns and acrobats."},
]


def spelling_game(request):
    # Guest play limit logic
    if not request.user.is_authenticated:
        guest_plays = request.session.get('guest_plays', 0)
        if guest_plays >= 3:
            return render(request, "quiz/guest_limit.html")
        request.session['guest_plays'] = guest_plays + 1
    user_name = None
    if request.user.is_authenticated:
        user_name = getattr(getattr(request.user, 'profile', None), 'first_name', request.user.username)
    feedback_overlay = None
    if request.method == "POST":
        word = request.session.get("current_spelling_word", "").lower()
        user_spelling = request.POST.get("spelling", "").strip().lower()
        result = user_spelling == word
        if request.user.is_authenticated:
            UserStat.objects.create(
                user=request.user,
                game="spelling",
                score=int(result),
                correct=1 if result else 0,
                incorrect=0 if result else 1,
                time_spent=0.0  # Could add timing logic if desired
            )
        attempt_label = user_spelling or "that try"
        typed_value = user_spelling or "(no answer)"
        if result:
            feedback_overlay = {
                "result": "correct",
                "voice_message": f"Wonderful! {word} is spelled correctly.",
                "heading": "Correct!",
                "subtitle": f"{word.title()} is spelled perfectly.",
                "body": "Get ready for a brand new word!",
            }
        else:
            feedback_overlay = {
                "result": "incorrect",
                "voice_message": f"Not quite. {attempt_label} doesn't spell {word} yet.",
                "heading": "Incorrect",
                "subtitle": f"The correct spelling is {word}.",
                "body": f"You typed {typed_value}. Look closely at each letter and try again!",
                "reset_on_fade": True,
            }
        return render(
            request,
            "quiz/spelling.html",
            {
                "word": word,
                "result": result,
                "user_name": user_name,
                "user_answer": user_spelling,
                "feedback_overlay": feedback_overlay,
            },
        )

    word = random.choice(SPELLING_WORDS)
    request.session["current_spelling_word"] = word
    return render(
        request,
        "quiz/spelling.html",
        {"word": word, "user_name": user_name, "feedback_overlay": None},
    )


def _choose_new_correct_spelling_entry(exclude_word=None):
    choices = [w for w in MISSPELLED_WORDS if w["incorrect"] != exclude_word]
    if not choices:
        choices = MISSPELLED_WORDS
    return dict(random.choice(choices))


def correct_spelling_game(request):
    if not request.user.is_authenticated:
        guest_plays = request.session.get('guest_plays', 0)
        if guest_plays >= 3:
            return render(request, "quiz/guest_limit.html")
        request.session['guest_plays'] = guest_plays + 1

    user_name = None
    if request.user.is_authenticated:
        user_name = getattr(getattr(request.user, 'profile', None), 'first_name', request.user.username)

    stored_entry = request.session.get("correct_spelling_entry")
    if stored_entry:
        current_entry = dict(stored_entry)
    else:
        current_entry = _choose_new_correct_spelling_entry()

    feedback_overlay = None
    if request.method == "POST":
        user_answer = request.POST.get("correct_spelling", "").strip()
        expected = current_entry["correct"]
        result = user_answer.lower() == expected.lower()
        if request.user.is_authenticated:
            UserStat.objects.create(
                user=request.user,
                game="correct_spelling",
                score=int(result),
                correct=1 if result else 0,
                incorrect=0 if result else 1,
                time_spent=0.0,
            )
        incorrect_word = current_entry["incorrect"]
        if result:
            feedback_overlay = {
                "result": "correct",
                "voice_message": f"Excellent! You fixed {incorrect_word} to {expected}.",
                "heading": "Correct!",
                "subtitle": f"{expected.title()} is the correct spelling.",
                "body": "A fresh word is on the way—keep it up!",
            }
        else:
            typed_value = user_answer or "(no answer)"
            feedback_overlay = {
                "result": "incorrect",
                "voice_message": f"Not yet. The correct spelling of {incorrect_word} is {expected}.",
                "heading": "Incorrect",
                "subtitle": f"{expected.title()} is the correct spelling.",
                "body": f"You typed {typed_value}. Check each letter and try again.",
                "reset_on_fade": True,
            }
        if result:
            current_entry = _choose_new_correct_spelling_entry(current_entry["incorrect"])
            request.session["correct_spelling_entry"] = current_entry
        else:
            request.session["correct_spelling_entry"] = current_entry
    else:
        request.session["correct_spelling_entry"] = current_entry

    return render(
        request,
        "quiz/correct_spelling.html",
        {
            "incorrect_word": current_entry["incorrect"],
            "hint": current_entry.get("hint"),
            "result": None if feedback_overlay is None else (feedback_overlay["result"] == "correct"),
            "user_name": user_name,
            "feedback_overlay": feedback_overlay,
        },
    )


def _build_rearrange_entry(exclude_word=None):
    choices = [w for w in REARRANGE_WORDS if w["word"] != exclude_word]
    if not choices:
        choices = REARRANGE_WORDS
    base = dict(random.choice(choices))
    word = base["word"]
    if len(word) > 1:
        scrambled = ''.join(random.sample(word, len(word)))
        while scrambled.lower() == word.lower():
            scrambled = ''.join(random.sample(word, len(word)))
    else:
        scrambled = word
    base["scrambled"] = scrambled
    return base


def rearrange_spelling_game(request):
    if not request.user.is_authenticated:
        guest_plays = request.session.get('guest_plays', 0)
        if guest_plays >= 3:
            return render(request, "quiz/guest_limit.html")
        request.session['guest_plays'] = guest_plays + 1

    user_name = None
    if request.user.is_authenticated:
        user_name = getattr(getattr(request.user, 'profile', None), 'first_name', request.user.username)

    stored_entry = request.session.get("rearrange_spelling_entry")
    if stored_entry:
        current_entry = dict(stored_entry)
        if "scrambled" not in current_entry:
            current_entry = _build_rearrange_entry(current_entry["word"])
    else:
        current_entry = _build_rearrange_entry()

    feedback_overlay = None
    if request.method == "POST":
        user_answer = request.POST.get("rearranged_word", "").strip()
        expected = current_entry["word"]
        result = user_answer.lower() == expected.lower()
        if request.user.is_authenticated:
            UserStat.objects.create(
                user=request.user,
                game="rearrange_spelling",
                score=int(result),
                correct=1 if result else 0,
                incorrect=0 if result else 1,
                time_spent=0.0,
            )
        scrambled_word = current_entry["scrambled"]
        if result:
            feedback_overlay = {
                "result": "correct",
                "voice_message": f"Awesome! You rearranged {scrambled_word} into {expected}.",
                "heading": "Correct!",
                "subtitle": f"{expected.title()} is the correct word.",
                "body": "Get ready for a brand-new puzzle!",
            }
        else:
            typed_value = user_answer or "(no answer)"
            feedback_overlay = {
                "result": "incorrect",
                "voice_message": f"Not quite. The correct word was {expected}.",
                "heading": "Incorrect",
                "subtitle": f"The correct word was {expected.title()}.",
                "body": f"You entered {typed_value}. Peek at the letters and try again!",
                "reset_on_fade": True,
            }
        if result:
            current_entry = _build_rearrange_entry(current_entry["word"])
            request.session["rearrange_spelling_entry"] = current_entry
        else:
            request.session["rearrange_spelling_entry"] = current_entry
    else:
        request.session["rearrange_spelling_entry"] = current_entry

    return render(
        request,
        "quiz/rearrange_spelling.html",
        {
            "scrambled_word": current_entry["scrambled"],
            "hint": current_entry.get("hint"),
            "result": None if feedback_overlay is None else (feedback_overlay["result"] == "correct"),
            "user_name": user_name,
            "feedback_overlay": feedback_overlay,
        },
    )


def home(request):
    return render(
        request,
        "quiz/home.html",
    )


def start_quiz(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        mode = request.POST.get("mode", "mixed")
        difficulty = request.POST.get("difficulty", "easy")
        # For guest users require a name
        if not request.user.is_authenticated and not name:
            return render(request, "quiz/start.html", {"error": "Please fill out all fields"})
        if not mode or not difficulty:
            return render(request, "quiz/start.html", {"error": "Please fill out all fields"})
        session = QuizSession.objects.create(
            user=request.user if request.user.is_authenticated else None
        )
        request.session["quiz_session_id"] = session.id
        request.session["game_mode"] = mode
        request.session["difficulty"] = difficulty
        request.session["played_math_intro"] = False
        request.session["played_mixed_intro"] = False
        request.session["played_difficulty_audio"] = False
        request.session["correct_streak"] = 0
        # Store the provided name in session for guest flows and tests
        # Escape the name to prevent XSS when rendering from session later
        if name:
            request.session['user_name'] = escape(name)
        return redirect("quiz:question")
    user_name = None
    if request.user.is_authenticated:
        user_name = getattr(getattr(request.user, 'profile', None), 'first_name', request.user.username)
    return render(request, "quiz/start.html", {"user_name": user_name})


def question(request):
    # Guest play limit logic
    if not request.user.is_authenticated:
        guest_plays = request.session.get('guest_plays', 0)
        if guest_plays >= 3:
            return render(request, "quiz/guest_limit.html")
        request.session['guest_plays'] = guest_plays + 1
    session_id = request.session.get("quiz_session_id")
    if not session_id:
        return redirect("quiz:start")
    
    try:
        session = QuizSession.objects.get(id=session_id)
    except QuizSession.DoesNotExist:
        return redirect("quiz:start")
        
    mode = request.session.get("game_mode", "mixed")
    if request.user.is_authenticated:
        user_name = getattr(getattr(request.user, 'profile', None), 'first_name', request.user.username)
    else:
        user_name = "Player"
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

    # Determine which intro/difficulty audios to play (only once per session)
    intro_audios = []
    if mode == "mixed":
        if not request.session.get("played_mixed_intro", False):
            intro_audios.append("mixed_game_intro.mp3")
            request.session["played_mixed_intro"] = True
    else:
        # Any specific math mode (add/sub/mul/div)
        if not request.session.get("played_math_intro", False):
            intro_audios.append("math_intro.mp3")
            request.session["played_math_intro"] = True
    if not request.session.get("played_difficulty_audio", False):
        diff_audio_map = {
            "easy": "easy_mode.mp3",
            "medium": "medium_mode.mp3",
            "hard": "hard_mode.mp3",
        }
        intro_audios.append(diff_audio_map.get(difficulty, "easy_mode.mp3"))
        request.session["played_difficulty_audio"] = True

    return render(
        request,
        "quiz/question.html",
        {
            "question": qtext,
            "user_name": user_name,
            "difficulty": difficulty,
            "time_limit": time_limit,
            "intro_audios": intro_audios,
        },
    )


def submit_answer(request):
    if request.method == "POST":
        timeout = request.POST.get("timeout", "false") == "true"
        correct_answer = request.session.get("current_answer")
        if timeout:
            # Reset streak and provide timeout voice audio
            request.session["correct_streak"] = 0
            return render(request, "quiz/result.html", {"result": "timeout", "correct_answer": correct_answer, "feedback_audio": "timeout_voice.mp3", "user_name": request.session.get("user_name", "Player")})

        answer_str = request.POST.get("answer", None)
        try:
            user_answer = int(answer_str)
            result = user_answer == correct_answer
        except (TypeError, ValueError):
            result = False
        
        if result:
            # Increment streak and decide on encouragement
            streak = request.session.get("correct_streak", 0) + 1
            request.session["correct_streak"] = streak
            encouragement = None
            if streak == 3:
                encouragement = "keep_going.mp3"
            elif streak == 5:
                encouragement = "excellent_work.mp3"
            elif streak == 7:
                encouragement = "almost_done.mp3"
            # Stats tracking for math/mixed quiz
            if request.user.is_authenticated:
                game_mode = request.session.get("game_mode", "math")
                stat_game = "mixed" if game_mode == "mixed" else "math"
                UserStat.objects.create(
                    user=request.user,
                    game=stat_game,
                    score=1,
                    correct=1,
                    incorrect=0,
                    time_spent=0.0
                )
            return render(
                request,
                "quiz/result.html",
                {
                    "result": result,
                    "correct_answer": correct_answer,
                    "feedback_audio": "correct_voice.mp3",
                    "encouragement_audio": encouragement,
                    "user_name": request.session.get("user_name", "Player"),
                },
            )
        else:
            # Wrong answer - stay on question page with feedback
            session_id = request.session.get("quiz_session_id")
            if not session_id:
                return redirect("quiz:start")
                
            try:
                session = QuizSession.objects.get(id=session_id)
            except QuizSession.DoesNotExist:
                return redirect("quiz:start")
                
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
            # Stats tracking for math/mixed quiz (incorrect)
            if request.user.is_authenticated:
                game_mode = request.session.get("game_mode", "math")
                stat_game = "mixed" if game_mode == "mixed" else "math"
                UserStat.objects.create(
                    user=request.user,
                    game=stat_game,
                    score=0,
                    correct=0,
                    incorrect=1,
                    time_spent=0.0
                )
            # Get current question from session
            current_question = request.session.get("current_question", "")
            # Reset streak
            request.session["correct_streak"] = 0
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
        # No longer request name; always use profile or username
        return redirect("quiz:what_time")

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
        # Handle name submission logic here if needed
        pass

    questions = [
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
        if request.user.is_authenticated:
            UserStat.objects.create(
                user=request.user,
                game="basic_questions",
                score=1,
                correct=1,
                incorrect=0,
                time_spent=0.0
            )
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

def general_knowledge_game(request):
    from .general_knowledge_questions import GENERAL_KNOWLEDGE_QUESTIONS
    import random, os
    from .models import UserStat

    if not request.user.is_authenticated:
        guest_plays = request.session.get('guest_plays', 0)
        if guest_plays >= 3:
            return render(request, "quiz/guest_limit.html")
        request.session['guest_plays'] = guest_plays + 1

    user_name = None
    if request.user.is_authenticated:
        user_name = getattr(getattr(request.user, 'profile', None), 'first_name', request.user.username)

    if request.method == "POST":
        q_idx = int(request.POST.get("q_idx", 0))
        answer = request.POST.get("answer")
        question = GENERAL_KNOWLEDGE_QUESTIONS[q_idx]
        correct = (answer == question["answer"])
        if request.user.is_authenticated:
            UserStat.objects.create(
                user=request.user,
                game="general_knowledge",
                score=int(correct),
                correct=1 if correct else 0,
                incorrect=0 if correct else 1,
                time_spent=0.0
            )
        return render(request, "quiz/general_knowledge_game.html", {
            "question": question["question"],
            "options": question["options"],
            "image": f"/static/quiz/images/general_knowledge/{question['image']}",
            "result": correct,
            "correct_answer": question["answer"],
            "user_answer": answer,
            "user_name": user_name,
            "q_idx": q_idx,
            "show_next": True
        })
    # GET: show random question
    q_idx = random.randint(0, len(GENERAL_KNOWLEDGE_QUESTIONS)-1)
    question = GENERAL_KNOWLEDGE_QUESTIONS[q_idx]
    return render(request, "quiz/general_knowledge_game.html", {
        "question": question["question"],
        "options": question["options"],
        "image": f"/static/quiz/images/general_knowledge/{question['image']}",
        "result": None,
        "user_name": user_name,
        "q_idx": q_idx
    })
