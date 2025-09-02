import sys
from gtts import gTTS
from pydub import AudioSegment

# --- Handle command-line arguments ---
# Usage: python make_intro.py [pitch] [speed] [text]
# Example: python make_intro.py 1.5 0.8 "Welcome to the game!"
pitch = float(sys.argv[1]) if len(sys.argv) > 1 else 1.3  # default pitch = 1.3
speed = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9  # default speed = 0.9
text = sys.argv[3] if len(sys.argv) > 3 else "Please spell the word: "

# --- Generate speech with gTTS (normal version) ---
tts = gTTS(text=text, lang="en", tld="com")
tts.save("spell_word_intro.mp3")
print("Normal MP3 generated: spell_word_intro.mp3")

# --- Load audio ---
sound = AudioSegment.from_file("spell_word_intro.mp3")

# --- Apply pitch + speed for kid-like voice ---
kids_voice = sound._spawn(sound.raw_data, overrides={
    "frame_rate": int(sound.frame_rate * pitch)
}).set_frame_rate(sound.frame_rate)

kids_voice = kids_voice._spawn(kids_voice.raw_data, overrides={
    "frame_rate": int(kids_voice.frame_rate * speed)
}).set_frame_rate(kids_voice.frame_rate)

kids_voice.export("spell_word_intro_kids.mp3", format="mp3")
print(f"Kid-like MP3 generated with pitch={pitch}, speed={speed}: spell_word_intro_kids.mp3")



# python make_intro.py 1.3 0.9   # higher pitch + a little slower
# python make_intro.py 1.3 1.1   # higher pitch + faster
# python make_intro.py 1.0 0.8   # normal pitch + slower
# python make_intro.py 1.2 0.9   # slightly higher pitch
# python make_intro.py 1.5 0.9   # much higher pitch (squeaky)

# The first number (1.5) is pitch
# The second number (0.8) is speed

