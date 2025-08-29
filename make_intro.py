from gtts import gTTS

# Text for the voice
# text = "Awsome!!!! You got it right."
# text = "Welcome my friends, let's have some fun. Please select a game to play."
text = "Lets practice telling time. Look at the clock and select what time it shows."

# Generate speech
tts = gTTS(text=text, lang="en", tld="com")

# Save as MP3
tts.save("time_intro.mp3")

print("MP3 file generated: time_intro.mp3")

# run this to execute script 
# python make_intro.py
