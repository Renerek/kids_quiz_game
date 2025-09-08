#!/usr/bin/env python3
"""
Enhanced Audio Generator for Kids Math Quiz Game
Generates all audio files with consistent kid-friendly pitch and quality.

Usage:
    python make_intro.py                    # Generate all audio files with default settings
    python make_intro.py --pitch 1.3       # Custom pitch only
    python make_intro.py --speed 0.9       # Custom speed only
    python make_intro.py --text "Hello"    # Generate single audio file
    python make_intro.py --list            # Show all audio files that will be generated
"""

import sys
import os
import argparse
from pathlib import Path
from gtts import gTTS
from pydub import AudioSegment

# Default audio settings optimized for kids
DEFAULT_PITCH = 1.3  # Higher pitch for kid-friendly voice
DEFAULT_SPEED = 0.9  # Slightly slower for clarity

# Audio content configuration
AUDIO_FILES = {
    # Welcome and intro audio
    'welcome.mp3': "Welcome to the Math Quiz Game! Let's have fun learning together!",
    'time_intro.mp3': "What time is it? Look at the clock and tell me the time!",
    'spell_word_intro.mp3': "Please spell the word you see on the screen!",
    
    # Feedback sounds (these use text-to-speech, not sound effects)
    'correct_voice.mp3': "Great job! That's correct! Keep going!",
    'incorrect_voice.mp3': "Oops! Try again. You can do it!",
    'timeout_voice.mp3': "Time's up! Let's try the next question!",
    
    # Game-specific intro audio
    'math_intro.mp3': "Let's solve some math problems! You're doing great!",
    'spelling_intro.mp3': "Time for spelling! Listen carefully and spell the word!",
    'fruits_intro.mp3': "Let's learn about fruits! Can you name this fruit?",
    'animals_intro.mp3': "Animal time! Do you know what animal this is?",
    'colors_shapes_intro.mp3': "Let's explore colors and shapes together!",
    'mixed_game_intro.mp3': "Mixed game time! We'll do math, spelling, and more!",
    
    # Encouragement audio
    'keep_going.mp3': "You're doing amazing! Keep going!",
    'almost_done.mp3': "You're almost done! Just a few more questions!",
    'excellent_work.mp3': "Excellent work! You're so smart!",
    'try_again.mp3': "That's okay! Let's try again together!",
    
    # Difficulty level intro
    'easy_mode.mp3': "Easy mode! Perfect for learning!",
    'medium_mode.mp3': "Medium mode! You're getting better!",
    'hard_mode.mp3': "Hard mode! You're a math superstar!",

    # Colors (for colors & shapes game)
    'color_red.mp3': "Red",
    'color_blue.mp3': "Blue",
    'color_green.mp3': "Green",
    'color_yellow.mp3': "Yellow",
    'color_purple.mp3': "Purple",
    'color_orange.mp3': "Orange",
    'color_pink.mp3': "Pink",
    'color_brown.mp3': "Brown",
    'color_gray.mp3': "Gray",
    'color_cyan.mp3': "Cyan",
    'color_gold.mp3': "Gold",
    'color_silver.mp3': "Silver",
    'color_white.mp3': "White",
    'color_black.mp3': "Black",

    # Shapes
    'shape_circle.mp3': "Circle",
    'shape_square.mp3': "Square",
    'shape_triangle.mp3': "Triangle",
    'shape_rectangle.mp3': "Rectangle",
    'shape_oval.mp3': "Oval",
    'shape_star.mp3': "Star",
}

def generate_audio_file(text, filename, pitch=DEFAULT_PITCH, speed=DEFAULT_SPEED, output_dir="quiz/static/quiz/audio"):
    """Generate a single audio file with kid-friendly voice processing."""
    
    print(f"Generating: {filename}")
    print(f"Text: {text}")
    
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate speech with gTTS
        tts = gTTS(text=text, lang="en", tld="com", slow=False)
        temp_file = f"temp_{filename}"
        tts.save(temp_file)
        
        # Load and process audio for kid-friendly voice
        sound = AudioSegment.from_file(temp_file)
        
        # Apply pitch adjustment (higher pitch for kid-like voice)
        kids_voice = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * pitch)
        }).set_frame_rate(sound.frame_rate)
        
        # Apply speed adjustment (slightly slower for clarity)
        kids_voice = kids_voice._spawn(kids_voice.raw_data, overrides={
            "frame_rate": int(kids_voice.frame_rate * speed)
        }).set_frame_rate(kids_voice.frame_rate)
        
        # Save processed audio
        output_path = os.path.join(output_dir, filename)
        kids_voice.export(output_path, format="mp3")
        
        # Clean up temp file
        os.remove(temp_file)
        
        print(f"✅ Generated: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error generating {filename}: {e}")
        return False

def generate_all_audio(pitch=DEFAULT_PITCH, speed=DEFAULT_SPEED):
    """Generate all audio files for the game."""
    
    print("=" * 60)
    print("🎵 KIDS MATH QUIZ GAME - AUDIO GENERATOR")
    print("=" * 60)
    print(f"Pitch: {pitch} (higher = more kid-like)")
    print(f"Speed: {speed} (lower = slower/clearer)")
    print(f"Total files to generate: {len(AUDIO_FILES)}")
    print("=" * 60)
    
    success_count = 0
    total_count = len(AUDIO_FILES)
    
    # Generate main audio files
    for filename, text in AUDIO_FILES.items():
        if generate_audio_file(text, filename, pitch, speed):
            success_count += 1
        print()  # Empty line for readability
    
    # Also create sounds directory versions (for feedback sounds)
    sounds_dir = "quiz/static/quiz/sounds"
    feedback_files = {
        'correct.mp3': AUDIO_FILES['correct_voice.mp3'],
        'incorrect.mp3': AUDIO_FILES['incorrect_voice.mp3'],
    }
    
    print("Generating feedback sounds...")
    for filename, text in feedback_files.items():
        if generate_audio_file(text, filename, pitch, speed, sounds_dir):
            success_count += 1
        print()
    
    total_count += len(feedback_files)
    
    print("=" * 60)
    print(f"🎉 GENERATION COMPLETE!")
    print(f"✅ Successfully generated: {success_count}/{total_count} files")
    if success_count < total_count:
        print(f"❌ Failed: {total_count - success_count} files")
    print("=" * 60)
    
    # Copy to staticfiles for deployment
    print("Copying to staticfiles directory...")
    try:
        import shutil
        
        # Copy audio files
        src_audio = Path("quiz/static/quiz/audio")
        dst_audio = Path("staticfiles/quiz/audio")
        if src_audio.exists():
            dst_audio.mkdir(parents=True, exist_ok=True)
            for file in src_audio.glob("*.mp3"):
                shutil.copy2(file, dst_audio)
                print(f"Copied: {file.name} -> staticfiles/quiz/audio/")
        
        # Copy sound files
        src_sounds = Path("quiz/static/quiz/sounds")
        dst_sounds = Path("staticfiles/quiz/sounds")
        if src_sounds.exists():
            dst_sounds.mkdir(parents=True, exist_ok=True)
            for file in src_sounds.glob("*.mp3"):
                shutil.copy2(file, dst_sounds)
                print(f"Copied: {file.name} -> staticfiles/quiz/sounds/")
                
        print("✅ Files copied to staticfiles for deployment!")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not copy to staticfiles: {e}")

def list_audio_files():
    """List all audio files that will be generated."""
    print("🎵 Audio files that will be generated:")
    print("=" * 60)
    
    print("\n📁 Main Audio Files (quiz/static/quiz/audio/):")
    for filename, text in AUDIO_FILES.items():
        print(f"  🔊 {filename}")
        print(f"     Text: {text}")
        print()
    
    print("📁 Feedback Sounds (quiz/static/quiz/sounds/):")
    print("  🔊 correct.mp3")
    print("     Text: Great job! That's correct! Keep going!")
    print("  🔊 incorrect.mp3") 
    print("     Text: Oops! Try again. You can do it!")
    
    print("=" * 60)
    print(f"Total: {len(AUDIO_FILES) + 2} audio files (including colors & shapes and feedback)")

def main():
    parser = argparse.ArgumentParser(
        description="Generate kid-friendly audio files for the Math Quiz Game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python make_intro.py                    # Generate all files with default settings
  python make_intro.py --pitch 1.4       # Higher pitch (more kid-like)
  python make_intro.py --speed 0.8       # Slower speed (clearer)
  python make_intro.py --list            # Show all files without generating
  python make_intro.py --text "Hello!"   # Generate single file
        """
    )
    
    parser.add_argument('--pitch', type=float, default=DEFAULT_PITCH,
                       help=f'Voice pitch multiplier (default: {DEFAULT_PITCH})')
    parser.add_argument('--speed', type=float, default=DEFAULT_SPEED,
                       help=f'Speed multiplier (default: {DEFAULT_SPEED})')
    parser.add_argument('--text', type=str,
                       help='Generate single audio file with custom text')
    parser.add_argument('--list', action='store_true',
                       help='List all audio files without generating')
    
    args = parser.parse_args()
    
    if args.list:
        list_audio_files()
        return
    
    if args.text:
        # Generate single file with custom text
        filename = "custom_audio.mp3"
        generate_audio_file(args.text, filename, args.pitch, args.speed)
        return
    
    # Generate all audio files
    generate_all_audio(args.pitch, args.speed)

if __name__ == "__main__":
    main()

# Legacy support for old command-line format
# python make_intro.py 1.3 0.9 "Custom text"
if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
    try:
        pitch = float(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PITCH
        speed = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_SPEED
        text = sys.argv[3] if len(sys.argv) > 3 else "Please spell the word: "
        
        print("🔄 Legacy mode detected. Use --help for new options.")
        generate_audio_file(text, "spell_word_intro.mp3", pitch, speed)
    except ValueError:
        print("❌ Invalid arguments. Use --help for usage information.")

