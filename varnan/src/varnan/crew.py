from crewai import Agent, Crew, Knowledge, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, FileReadTool, FileWriterTool
from dotenv import load_dotenv
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
import pymupdf as fitz  # Import fitz from PyMuPDF
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
import os
import litellm
from fetch_pdf_content import fetch_pdf_content
#litellm._turn_on_debug()
#load api keys
load_dotenv()

@CrewBase
class ScriptGeneratorCrew():
    """Script Generator Crew"""

    def __init__(self):
        # Initialize tools
        self.serper_dev_tool = SerperDevTool()
        self.file_read_tool = FileReadTool()
        self.file_writer_tool = FileWriterTool()
        self.pdf_path = ""  
        self.pdf_content=''
        self.string_knowledge_source = StringKnowledgeSource(
                content="empty knowledge source") 


    def fetch_pdf_path(self, pdf_path: str):
        """Fetch the path of a PDF file from the knowledge source."""
        self.pdf_path=pdf_path

        # Verify PDF exists before processing
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")


        # PDF processing with error handling
        try:
            #pdf_content=fetch_pdf_content(self.pdf_path)
            doc = fitz.open(self.pdf_path)
            pdf_content = "\n".join([page.get_text("text") for page in doc])
            self.string_knowledge_source = StringKnowledgeSource(
                content=pdf_content,
                language="en",
                embedder={"provider": "openai", "config":{"model": "text-embedding-3-small"}} #nomic-embed-text
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to process PDF: {str(e)}") from e
        
        # Add debug prints in crew.py __init__
        print(f"Initializing crew with PDF: {pdf_path}")
        print(f"Knowledge source type: {type(self.string_knowledge_source)}")






    script_llm = LLM(
        model=""
        "gpt-4o-mini-2024-07-18",
        #base_url="http://localhost:11434",
        temperature=0.0
    )

    research_llm = LLM(
        model="gpt-4o-mini-2024-07-18",
        temperature=0.2
        #base_url="http://localhost:11434"
    )

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"


    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["research_agent"],
            tools=[self.serper_dev_tool],
            llm=self.research_llm,
            #knowledge=self.string_knowledge_source,
            max_iter=1,
            max_tokens=2000,
            max_rpm=1

        )    

    @agent
    def summary_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["summary_agent"],
            tools= [self.file_writer_tool],
            llm=self.research_llm,
            #knowledge=self.string_knowledge_source,
            max_iter=2,
            max_tokens=9000,
            max_rpm=2
        )

    @agent
    def script_writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["script_writer_agent"],
            llm=self.script_llm,
            tools=[self.file_writer_tool],
            #knowledge=self.string_knowledge_source,
            max_iter=2,
            max_tokens=9000,
            max_rpm=2
        )
    @agent
    def script_analyser_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["script_analyser_agent"],
            tools=[self.file_writer_tool],
            llm=self.script_llm,
            #knowledge=self.string_knowledge_source,
            max_iter=1,
            max_tokens=9000,
            max_rpm=2
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            output_file= r"outputs/research_facts.txt",
            max_retries=1
            
        )
    
    @task
    def summary_task(self) -> Task:
        return Task(
            config=self.tasks_config["summary_task"],
            output_file= r"outputs/summary.txt",
            max_retries=2
        )

    @task
    def script_writing_task(self) -> Task:
        return Task(
            config=self.tasks_config["script_writing_task"],
            tools= [self.file_writer_tool],
            output_file= r"outputs/script_flow.txt",
            max_retries=2
            
        )
    @task
    def script_analyser_task(self) -> Task:
        return Task(
            config=self.tasks_config["script_analyser_task"],
            tools=[self.file_writer_tool],
            output_file= r"outputs/final_script.txt",
            max_retries=1
        )
    
    

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            knowledge_sources=[self.string_knowledge_source],
            
            
            verbose=True
            
        )
    