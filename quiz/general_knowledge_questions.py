# General Knowledge Questions for Kids Quiz Game
# Categories: Professions, Community Places, Weather & Nature, Seasons, Planets & Space
import random
# Each question includes: question, options, correct answer, image (to be added to static/quiz/images/general_knowledge/)

_RAW_GENERAL_KNOWLEDGE_QUESTIONS = [
    # Professions / Jobs
    {
        "question": "A doctor works in a...",
        "options": ["School", "Airport", "Hospital", "Library"],
        "answer": "Hospital",
        "image": "doctor.png"
    },
    {
        "question": "A teacher works in a...",
        "options": ["Fire Station", "School", "Park", "Hospital"],
        "answer": "School",
        "image": "teacher.png"
    },
    {
        "question": "A firefighter works in a...",
        "options": ["Fire Station", "Library", "Grocery Store", "Airport"],
        "answer": "Fire Station",
        "image": "firefighter.png"
    },
    {
        "question": "A chef works in a...",
        "options": ["Restaurant", "School", "Park", "Hospital"],
        "answer": "Restaurant",
        "image": "chef.png"
    },
    {
        "question": "A police officer works in a...",
        "options": ["Police Station", "Library", "Park", "Hospital"],
        "answer": "Police Station",
        "image": "police.png"
    },
    {
        "question": "A farmer works on a...",
        "options": ["Farm", "Spaceship", "School", "Fire Station"],
        "answer": "Farm",
        "image": "farmer.png"
    },
    # Community Places
    {
        "question": "We buy our fruits and veggies from the...",
        "options": ["Grocery Store", "Library", "Fire Station", "School"],
        "answer": "Grocery Store",
        "image": "grocery_store.png"
    },
    {
        "question": "You borrow books from the...",
        "options": ["Library", "Hospital", "Park", "Restaurant"],
        "answer": "Library",
        "image": "library.png"
    },
    {
        "question": "Children play in the...",
        "options": ["Park", "Hospital", "Fire Station", "School"],
        "answer": "Park",
        "image": "park.png"
    },
    # Weather & Nature
    {
        "question": "It snows in the...",
        "options": ["Winter", "Summer", "Spring", "Fall"],
        "answer": "Winter",
        "image": "snow.png"
    },
    {
        "question": "The sun is...",
        "options": ["Hot", "Cold", "Wet", "Dark"],
        "answer": "Hot",
        "image": "sun.png"
    },
    {
        "question": "A rainbow appears after...",
        "options": ["Rain", "Snow", "Wind", "Fog"],
        "answer": "Rain",
        "image": "rainbow.png"
    },
    # Seasons
    {
        "question": "Leaves fall in...",
        "options": ["Autumn", "Spring", "Summer", "Winter"],
        "answer": "Autumn",
        "image": "autumn.png"
    },
    {
        "question": "Flowers bloom in...",
        "options": ["Spring", "Winter", "Autumn", "Summer"],
        "answer": "Spring",
        "image": "spring.png"
    },
    # Planets & Space
    {
        "question": "We live on planet...",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "answer": "Earth",
        "image": "earth.png"
    },
    {
        "question": "Astronauts travel in a...",
        "options": ["Spaceship", "Car", "Boat", "Train"],
        "answer": "Spaceship",
        "image": "spaceship.png"
    },
    {
        "question": "The moon shines at...",
        "options": ["Night", "Morning", "Afternoon", "Noon"],
        "answer": "Night",
        "image": "moon.png"
    },
    # Food/Nature
    {
        "question": "An apple is a...",
        "options": ["Fruit", "Vegetable", "Animal", "Bird"],
        "answer": "Fruit",
        "image": "apple.png"
    },

        # Professions / Jobs
    {
        "question": "Who uses a fire hose to put out fires?",
        "options": ["Firefighter", "Teacher", "Chef", "Doctor"],
        "answer": "Firefighter",
        "image": "firefighter.png"
    },
    {
        "question": "Who takes care of sick animals?",
        "options": ["Veterinarian", "Farmer", "Zookeeper", "Police Officer"],
        "answer": "Veterinarian",
        "image": "veterinarian.png"
    },
    {
        "question": "Who drives a big truck to deliver things?",
        "options": ["Truck Driver", "Pilot", "Bus Driver", "Captain"],
        "answer": "Truck Driver",
        "image": "truck_driver.png"
    },

    # Community Places
    {
        "question": "Where do you go to mail a letter?",
        "options": ["Post Office", "Library", "Grocery Store", "School"],
        "answer": "Post Office",
        "image": "post_office.png"
    },
    {
        "question": "Where do you go to see a doctor for a check-up?",
        "options": ["Clinic", "Hospital", "School", "Park"],
        "answer": "Clinic",
        "image": "clinic.png"
    },
    {
        "question": "Where can you go to swim and play in the water?",
        "options": ["Swimming Pool", "Park", "Library", "Playground"],
        "answer": "Swimming Pool",
        "image": "swimming_pool.png"
    },

    # Weather & Nature
    {
        "question": "What falls from the sky when it rains?",
        "options": ["Raindrops", "Leaves", "Snowflakes", "Feathers"],
        "answer": "Raindrops",
        "image": "rain.png"
    },
    {
        "question": "What do you need to hold over your head to stay dry in the rain?",
        "options": ["Umbrella", "Pillow", "Book", "Plate"],
        "answer": "Umbrella",
        "image": "umbrella.png"
    },
    {
        "question": "What shiny thing in the sky can you sometimes see after it rains?",
        "options": ["Rainbow", "Airplane", "Star", "Moon"],
        "answer": "Rainbow",
        "image": "rainbow.png"
    },

    # Seasons
    {
        "question": "In which season do you build a snowman?",
        "options": ["Winter", "Summer", "Spring", "Fall"],
        "answer": "Winter",
        "image": "snowman.png"
    },
    {
        "question": "In which season do you wear shorts and go to the beach?",
        "options": ["Summer", "Winter", "Spring", "Fall"],
        "answer": "Summer",
        "image": "beach.png"
    },

    # Planets & Space
    {
        "question": "What big, bright thing can you see in the sky during the day?",
        "options": ["The Sun", "The Moon", "A Star", "A Planet"],
        "answer": "The Sun",
        "image": "sun.png"
    },
    {
        "question": "What do you call the vehicle that takes astronauts to space?",
        "options": ["Rocket", "Airplane", "Car", "Boat"],
        "answer": "Rocket",
        "image": "rocket.png"
    },

    # Animals
    {
        "question": "Which animal has a long trunk?",
        "options": ["Elephant", "Giraffe", "Lion", "Monkey"],
        "answer": "Elephant",
        "image": "elephant.png"
    },
    {
        "question": "Which animal hops and has a pouch?",
        "options": ["Kangaroo", "Rabbit", "Frog", "Bear"],
        "answer": "Kangaroo",
        "image": "kangaroo.png"
    },
    {
        "question": "Which animal says 'Moo'?",
        "options": ["Cow", "Sheep", "Pig", "Duck"],
        "answer": "Cow",
        "image": "cow.png"
    },

    # Food
    {
        "question": "What orange vegetable do rabbits love to eat?",
        "options": ["Carrot", "Broccoli", "Cucumber", "Potato"],
        "answer": "Carrot",
        "image": "carrot.png"
    },
    {
        "question": "What frozen treat is sweet and cold on a hot day?",
        "options": ["Ice Cream", "Cake", "Cookie", "Apple"],
        "answer": "Ice Cream",
        "image": "ice_cream.png"
    },
    {
        "question": "What do you make with flour, water, and bake in an oven?",
        "options": ["Bread", "Juice", "Soup", "Salad"],
        "answer": "Bread",
        "image": "bread.png"
    },

    # Objects & Things
    {
        "question": "What do you use to cut paper?",
        "options": ["Scissors", "Spoon", "Crayon", "Glue"],
        "answer": "Scissors",
        "image": "scissors.png"
    },
    {
        "question": "What do you read to hear a bedtime story?",
        "options": ["A Book", "A Clock", "A Lamp", "A Phone"],
        "answer": "A Book",
        "image": "book.png"
    }
]

# Shuffle options for each question at import time
GENERAL_KNOWLEDGE_QUESTIONS = []
for q in _RAW_GENERAL_KNOWLEDGE_QUESTIONS:
    q_copy = q.copy()
    opts = q_copy["options"][:]
    random.shuffle(opts)
    q_copy["options"] = opts
    GENERAL_KNOWLEDGE_QUESTIONS.append(q_copy)
