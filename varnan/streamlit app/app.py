import streamlit as st
import os
import tempfile
import subprocess
import base64
import shutil
import sys
from pathlib import Path

def run_conversion_script(pdf_path):
    """Run the existing conversion script with the uploaded PDF path."""
    # Get the directory where this streamlit app is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to main.py should be in the same directory
    main_script_path = os.path.join(current_dir, "main.py")
    
    if not os.path.exists(main_script_path):
        st.error(f"Cannot find main.py script at {main_script_path}")
        return False
    
    # Create research_paper.pdf in the same directory as main.py
    research_paper_path = os.path.join(current_dir, "research_paper.pdf")
    
    # Copy the uploaded PDF to research_paper.pdf
    try:
        if os.path.exists(research_paper_path):
            os.remove(research_paper_path)
        shutil.copy2(pdf_path, research_paper_path)
    except Exception as e:
        st.error(f"Error copying PDF file: {e}")
        return False
    
    try:
        # Change to the directory containing main.py before running it
        original_dir = os.getcwd()
        os.chdir(current_dir)
        
        # Run the conversion script
        result = subprocess.run([sys.executable, main_script_path], 
                                capture_output=True, 
                                text=True, 
                                check=True)
        st.text("Process output:")
        #st.text(result.stdout)
        
        # Path to the expected podcast.mp3 file
        podcast_path = os.path.join(current_dir, "crewai_podcast_output.mp3")
        
        # Return success if the podcast.mp3 file was created
        return os.path.exists(podcast_path)
    except subprocess.CalledProcessError as e:
        st.error(f"Error running conversion script: {e}")
        st.text("Error output:")
        st.text(e.stdout)
        st.text(e.stderr)
        return False
    finally:
        # Clean up
        if os.path.exists(research_paper_path):
            try:
                os.remove(research_paper_path)
            except:
                pass
        
        # Restore original directory
        os.chdir(original_dir)

def get_download_link(file_path, file_name):
    """Generate a download link for the given file."""
    with open(file_path, "rb") as file:
        data = file.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{file_name}">Download {file_name}</a>'
    return href

def main():
    st.set_page_config(page_title="Varnan - Research Paper to Podcast Converter")

    # Custom CSS to change background color of main content and sidebar
    st.markdown(
        """
        <style>
        /* Background */
        .stApp {
            background-color: #fbfbdf;
            color: black !important;
        }

        /* Text elements */
        h1, h2, h3, h4, h5, h6
        {
            color: black !important;
        }

        /* Streamlit feedback boxes (success, info, error) */
        .stAlert {
            background-color: #e6ffe6 !important;  /* light green */
            color: black !important;
        }

        .stAlert > div {
            color: black !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Centered, large logo at the top
    st.image("assets/varnan_logo.png", width=300)  # Adjust width as needed

    st.subheader("Convert Research Papers to Audio Podcasts")
    
    # File upload widget
    uploaded_file = st.file_uploader("Upload a research paper (PDF)", type="pdf")
    
    if uploaded_file is not None:
        # Create a temporary file to save the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.read())
            pdf_path = tmp_file.name
        
        st.info(f"PDF uploaded: {uploaded_file.name}")
        
        # Button to start conversion
        if st.button("Convert to Podcast"):
            with st.spinner("Converting PDF to podcast audio... This may take a while."):
                success = run_conversion_script(pdf_path)
            
            if success:
                # Get the directory where this streamlit app is located
                current_dir = os.path.dirname(os.path.abspath(__file__))
                podcast_path = os.path.join(current_dir, "crewai_podcast_output.mp3")
                
                st.success("Podcast created successfully!")
                
                # Audio player
                st.subheader("Listen to Your Podcast")
                st.audio(podcast_path)
                
                # Download button
                st.subheader("Download the Podcast")
                download_filename = f"Varnan_{uploaded_file.name.split('.')[0]}.mp3"
                st.markdown(get_download_link(podcast_path, download_filename), unsafe_allow_html=True)
            else:
                st.error("Failed to create podcast. Check the error logs above.")
        
        # Clean up the temporary file
        os.unlink(pdf_path)

if __name__ == "__main__":
    main()