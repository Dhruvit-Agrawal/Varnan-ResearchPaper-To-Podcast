# Varnan - Research Paper to Podcast Generator 🎙️

![Varnan Logo](assets/varnan_logo.png)

**Varnan** is an intelligent pipeline that transforms research papers into high-quality, conversational podcast audio.  
It simplifies academic research consumption by summarizing dense papers, creating a multi-speaker podcast script, and converting it into professional audio.

## ✨ Features

- 📄 Upload a research paper (PDF)
- 🧠 AI Agents summarize and rewrite the research into a podcast script
- 🎙️ Multi-speaker podcast generation using Text-to-Speech (TTS)
- 🖥️ Clean Streamlit Web Interface
- 📥 Listen or download the generated `.mp3` podcast

## ⚙️ Flow

1. **Upload PDF**: Upload a research paper via the Streamlit app.
2. **PDF Processing**: Extract text from the paper using PyMuPDF.
3. **CrewAI Agents**:
   - **Research Agent**: Extracts key facts.
   - **Summary Agent**: Creates a concise, structured summary.
   - **Script Writer Agent**: Crafts a friendly, podcast-style script.
   - **Script Analyzer Agent**: Refines the final podcast script.
4. **Podcast Generation**:
   - Parse the script into dialogue for host, expert, and learner roles.
   - Convert dialogues to speech using Edge TTS voices.
   - Combine all parts into a final podcast `.mp3` file.
5. **Output**:
   - Listen to the podcast on the web app.
   - Download the audio file for offline use.


## 🛠️ Tech Stack

- **Python 3.11**
- **Streamlit** — Web Interface
- **CrewAI** — Multi-Agent System
- **LiteLLM** — LLM Management
- **Edge TTS** — Text-to-Speech Engine
- **PyMuPDF** — PDF Text Extraction
- **pydub** — Audio File Merging
- **dotenv** — Environment Variable Management
- **agentops** — Optional Agent Monitoring

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/varnan.git
cd varnan
2. Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
3. Configure environment variables
Create a .env file in the root directory:

env
Copy
Edit
OPENAI_API_KEY=your_openai_key
SERPER_API_KEY=your_serper_key
AGENTOPS_API_KEY=your_agentops_key
4. Run the Streamlit app
bash
Copy
Edit
streamlit run app.py
Upload a research paper and get your podcast! 🎧

🧠 Future Improvements
🗣️ Support custom voices and accents

🌍 Multilingual podcast generation

📝 Smarter summarization for highly technical papers

☁️ Cloud deployment for public access

🤝 Contributing
Contributions are welcome!
Please open an issue first to discuss your idea or improvement.
