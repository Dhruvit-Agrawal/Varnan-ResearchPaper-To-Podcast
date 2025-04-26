#!/usr/bin/env python
import asyncio
import sys
import warnings
import agentops
from datetime import datetime
from tts import read_script_from_file, create_podcast_audio
from fetch_pdf_content import fetch_pdf_content


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
from pydantic import BaseModel
import os
import traceback
from crewai.flow import Flow, listen, start
from crew import ScriptGeneratorCrew


def run():
    """
    Run the crew.
    """
    pdf_name= r"research_paper.pdf"

    print("got pdf")
    inputs = {
            'pdf_path': pdf_name
        }
    print(inputs)
    print("kicking off crew")
    
    try:
        crew_session= agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))

        print("initating crew instance")
        # Add this temporarily to main.py before crew initialization
        print(f"PDF exists: {os.path.exists(pdf_name)}")
        crew_instance=ScriptGeneratorCrew()
        print("crew instance initiated")
        pdf_content=fetch_pdf_content(pdf_path=pdf_name)
        #pdf_content=crew_instance.fetch_pdf_path(pdf_path=pdf_name)
        print(f"pdf processed with the processing result: \n {pdf_content}")
        print("starting crew")
        crew_instance.crew().kickoff(inputs={"pdf_content":pdf_content})
        print("crew started and worked")


        crew_session.end_session()
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


if __name__=="__main__":
    from dotenv import load_dotenv
    import os



    load_dotenv()

    run()
    print("Podcast Script generated successfully!!")
    print("Now we will be Converting the text script to audio file",'\n')
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

    
    # Check if we have script content
    if not 'script_text' in locals() or not script_text.strip():
        print("No script content found. Exiting.")
        exit(1)
        
    print("Converting podcast script to audio...")
    asyncio.run(create_podcast_audio(script_text))

    
