import asyncio
import re
import edge_tts
import os
import time

# Define different voices for different speakers
HOST_VOICE = "en-US-ChristopherNeural"      # Male voice for Alex (Host)
EXPERT_VOICE = "en-US-GuyNeural"          # Female voice for Mia (Expert)
LEARNER_VOICE = "en-US-JennyNeural"           # Male voice for Jake (Learner)


async def text_to_speech(text, voice, output_file, rate="+0%", volume="+0%"):
    """Convert text to speech using Edge TTS and save to file"""
    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
    await communicate.save(output_file)

def parse_script(script_text):
    """Parse the script and extract lines by speaker"""
    
    # Define regex patterns to identify speakers and content

    patterns = {
        'host': r'\*\*Host.*?\*\*:\s*(.*?)(?=\n\*\*[A-Z][a-z]+.*?\*\*:|\Z)',  
        'expert': r'\*\*Expert.*?\*\*:\s*(.*?)(?=\n\*\*[A-Z][a-z]+.*?\*\*:|\Z)',
        'learner': r'\*\*Learner.*?\*\*:\s*(.*?)(?=\n\*\*[A-Z][a-z]+.*?\*\*:|\Z)',
    }
    # patterns = {
    # 'host': r'HOST:\s*(.*?)(?=\n[A-Z]+:|\Z)',
    # 'expert': r'EXPERT:\s*(.*?)(?=\n[A-Z]+:|\Z)',
    # 'learner': r'LEARNER:\s*(.*?)(?=\n[A-Z]+:|\Z)',
    # }

    # Extract all dialogue parts with their speakers
    dialogue_parts = []
    
    # Extract the title and introduction (for narrator)
    title_match = re.search(r'\*\*(.+?)\*\*', script_text)
    if title_match:
        dialogue_parts.append(('host', f"Welcome to {title_match.group(1)}"))
    
    # Extract dialogue by speaker
    for speaker, pattern in patterns.items():
        matches = re.finditer(pattern, script_text, re.DOTALL)
        for match in matches:
            content = match.group(1).strip()
            dialogue_parts.append((speaker, content))
    
    # Sort dialogue_parts based on their position in the original script
    # This requires finding the position of each match in the original text
    positioned_parts = []
    for speaker, pattern in patterns.items():
        matches = re.finditer(pattern, script_text, re.DOTALL)
        for match in matches:
            content = match.group(1).strip()
            positioned_parts.append((match.start(), speaker, content))
    
    # Sort by position
    positioned_parts.sort()
    dialogue_parts = [(speaker, content) for _, speaker, content in positioned_parts]
    
    return dialogue_parts

async def create_podcast_audio(script_text, output_file="crewai_podcast_output.mp3"):
    """Create a podcast audio file from the script text"""
    dialogue_parts = parse_script(script_text)
    
    # Generate temporary audio files for each part
    temp_files = []
    for i, (speaker, content) in enumerate(dialogue_parts):
        if not content.strip():
            continue
            
        temp_file = f"temp_{i}.mp3"
        temp_files.append(temp_file)
        
        # Select voice based on speaker
        if speaker == "host":
            voice = HOST_VOICE
        elif speaker == "expert":
            voice = EXPERT_VOICE
        elif speaker == "learner":
            voice = LEARNER_VOICE

            
        # Add pauses for narration/directions
        if speaker == "host":
            # Slow down and soften narrator voice for stage directions
            await text_to_speech(content, voice, temp_file, rate="-10%", volume="-10%")
        else:
            await text_to_speech(content, voice, temp_file)
            
        print(f"Generated audio for: {speaker} - {content[:30]}...")
    
    # Alternative method without ffmpeg for combining files
    from pydub import AudioSegment
    
    try:
        # Try using pydub to concatenate files
        print("Combining audio files...")
        combined = AudioSegment.empty()
        for temp_file in temp_files:
            audio_segment = AudioSegment.from_mp3(temp_file)
            combined += audio_segment
        
        combined.export(output_file, format="mp3")
        print(f"Combined audio using pydub.")
    except Exception as e:
        print(f"Error combining with pydub: {e}")
        print("Trying alternative method...")
        
        # Create a simple concatenated file by appending bytes
        with open(output_file, 'wb') as outfile:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    with open(temp_file, 'rb') as infile:
                        outfile.write(infile.read())
        
        print("Note: Files were combined using a simple method. Quality may be affected.")
    
    # Clean up temporary files
    for temp_file in temp_files:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"Warning: Could not remove temp file {temp_file}: {e}")
    
    print(f"Podcast audio created successfully: {output_file}")

# Read the script from a file
def read_script_from_file(filename=r"outputs\final_script.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

# Execute the script conversion
if __name__ == "__main__":
    try:
        # First, install pydub if not installed
        try:
            import pydub
        except ImportError:
            print("Installing pydub package...")
            import pip
            pip.main(['install', 'pydub'])
            print("pydub installed successfully.")
    except Exception as e:
        print(f"Warning: Could not install pydub: {e}")
        print("Will try to continue without it.")
        
    try:
        # Either read from a file or use a hardcoded script
        script_text = read_script_from_file()
        print("Script loaded from file.")
    except Exception as e:
        # If file reading fails, prompt user to create the file
        print(f"Could not find final_script.txt: {e}")
        print("Please create this file with your script content.")
        print("Alternatively, you can paste your script below (press Ctrl+D or Ctrl+Z then Enter when finished):")
        script_lines = []
        try:
            while True:
                line = input()
                script_lines.append(line)
        except (EOFError, KeyboardInterrupt):
            script_text = '\n'.join(script_lines)
        
    # Check if we have script content
    if not 'script_text' in locals() or not script_text.strip():
        print("No script content found. Exiting.")
        exit(1)
        
    print("Converting podcast script to audio...")
    asyncio.run(create_podcast_audio(script_text))

if __name__=="__main__":

    try:
        import pydub
    except ImportError:
        print("Installing pydub package...")
        import pip
        pip.main(['install', 'pydub'])
        print("pydub installed successfully.")
    except Exception as e:
        print(f"Warning: Could not install pydub: {e}")
        print("Will try to continue without it.")

    try:
        # Either read from a file or use a hardcoded script
        script_text = read_script_from_file()
        print("Script loaded from file.")
    except Exception as e:
        # If file reading fails, prompt user to create the file
        print(f"Could not find final_script.txt: {e}")

    
    # Check if we have script content
    if not 'script_text' in locals() or not script_text.strip():
        print("No script content found. Exiting.")
        exit(1)
        
    print("Converting podcast script to audio...")
    asyncio.run(create_podcast_audio(script_text))
