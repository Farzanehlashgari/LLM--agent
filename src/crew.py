"""
CrewAI multi-agent system for LLM mental health research.
"""
import os
import time
from typing import Dict, Any
import yaml
from pathlib import Path
from loguru import logger

from crewai import Agent, Crew, Task, Process, LLM
from crewai_tools import SerperDevTool

from .models import CrewExecutionResult


class MentalHealthResearchCrew:
    """
    Multi-agent crew for researching LLM applications in mental health.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the research crew.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        
        # Load configurations
        self.agents_config = self._load_yaml(self.config_dir / "agents.yaml")
        self.tasks_config = self._load_yaml(self.config_dir / "tasks.yaml")
        
        # Initialize LLM
        self.llm = self._init_llm()
        
        # Initialize tools
        self.search_tool = SerperDevTool(
            n_results=int(os.getenv("MAX_SEARCH_RESULTS", 10))
        )
        
        # Create agents
        self.agents = self._create_agents()
        
        # Create tasks
        self.tasks = self._create_tasks()
        
        # Create crew
        self.crew = self._create_crew()
        
        logger.info("MentalHealthResearchCrew initialized successfully")
    
    def _load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        try:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load {filepath}: {e}")
            raise
    
    def _init_llm(self) -> LLM:
        """Initialize the language model."""
        # Use gemini/ prefix for LiteLLM
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini/gemini-1.5-pro")
        if not model_name.startswith("gemini/"):
            model_name = f"gemini/{model_name}"
            
        return LLM(
            model=model_name,
            api_key=os.getenv("GEMINI_API_KEY")
        )
    
    def _create_agents(self) -> Dict[str, Agent]:
        """Create the research agents."""
        agents = {}
        
        # Researcher agent with search capabilities
        agents['researcher'] = Agent(
            role=self.agents_config['researcher']['role'],
            goal=self.agents_config['researcher']['goal'],
            backstory=self.agents_config['researcher']['backstory'],
            verbose=self.agents_config['researcher']['verbose'],
            allow_delegation=self.agents_config['researcher']['allow_delegation'],
            max_iter=self.agents_config['researcher']['max_iter'],
            memory=self.agents_config['researcher']['memory'],
            tools=[self.search_tool],
            llm=self.llm
        )
        
        # Analyst agent
        agents['analyst'] = Agent(
            role=self.agents_config['analyst']['role'],
            goal=self.agents_config['analyst']['goal'],
            backstory=self.agents_config['analyst']['backstory'],
            verbose=self.agents_config['analyst']['verbose'],
            allow_delegation=self.agents_config['analyst']['allow_delegation'],
            max_iter=self.agents_config['analyst']['max_iter'],
            memory=self.agents_config['analyst']['memory'],
            llm=self.llm
        )
        
        # Report writer agent
        agents['report_writer'] = Agent(
            role=self.agents_config['report_writer']['role'],
            goal=self.agents_config['report_writer']['goal'],
            backstory=self.agents_config['report_writer']['backstory'],
            verbose=self.agents_config['report_writer']['verbose'],
            allow_delegation=self.agents_config['report_writer']['allow_delegation'],
            max_iter=self.agents_config['report_writer']['max_iter'],
            memory=self.agents_config['report_writer']['memory'],
            llm=self.llm
        )
        
        return agents
    
    def _create_tasks(self) -> Dict[str, Task]:
        """Create the research tasks."""
        tasks = {}
        
        # Search task
        tasks['search'] = Task(
            description=self.tasks_config['search_research']['description'],
            expected_output=self.tasks_config['search_research']['expected_output'],
            agent=self.agents['researcher']
        )
        
        # Analysis task (depends on search)
        tasks['analyze'] = Task(
            description=self.tasks_config['analyze_findings']['description'],
            expected_output=self.tasks_config['analyze_findings']['expected_output'],
            agent=self.agents['analyst'],
            context=[tasks['search']]  # Waits for search to complete
        )
        
        # Report generation task (depends on analysis)
        tasks['report'] = Task(
            description=self.tasks_config['generate_report']['description'],
            expected_output=self.tasks_config['generate_report']['expected_output'],
            agent=self.agents['report_writer'],
            context=[tasks['search'], tasks['analyze']]  # Waits for both
        )
        
        return tasks
    
    def _create_crew(self) -> Crew:
        """Create the crew with sequential process."""
        return Crew(
            agents=list(self.agents.values()),
            tasks=list(self.tasks.values()),
            process=Process.sequential,
            verbose=True,
            memory=True,
            planning=True,  # Enable planning for better task coordination
            planning_llm=self.llm  # Explicitly use Gemini for planning
        )
    
    def execute(self) -> CrewExecutionResult:
        """
        Execute the research crew.
        
        Returns:
            CrewExecutionResult with the generated report and metadata
        """
        execution_id = f"exec_{int(time.time())}"
        start_time = time.time()
        
        logger.info(f"Starting crew execution: {execution_id}")
        
        try:
            # Kickoff the crew
            result = self.crew.kickoff()
            
            execution_time = time.time() - start_time
            
            # Extract the final report
            report = str(result)
            
            logger.info(f"Crew execution completed in {execution_time:.2f}s")
            
            return CrewExecutionResult(
                execution_id=execution_id,
                status="success",
                report=report,
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Crew execution failed: {str(e)}"
            logger.error(error_msg)
            
            return CrewExecutionResult(
                execution_id=execution_id,
                status="failure",
                report="",
                error=error_msg,
                execution_time_seconds=execution_time
            )
    
    async def execute_async(self) -> CrewExecutionResult:
        """
        Execute the research crew asynchronously.
        
        Returns:
            CrewExecutionResult with the generated report and metadata
        """
        execution_id = f"exec_{int(time.time())}"
        start_time = time.time()
        
        logger.info(f"Starting async crew execution: {execution_id}")
        
        try:
            # Kickoff the crew asynchronously
            result = await self.crew.kickoff_async()
            
            execution_time = time.time() - start_time
            
            # Extract the final report
            report = str(result)
            
            logger.info(f"Async crew execution completed in {execution_time:.2f}s")
            
            return CrewExecutionResult(
                execution_id=execution_id,
                status="success",
                report=report,
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Async crew execution failed: {str(e)}"
            logger.error(error_msg)
            
            return CrewExecutionResult(
                execution_id=execution_id,
                status="failure",
                report="",
                error=error_msg,
                execution_time_seconds=execution_time
            )
