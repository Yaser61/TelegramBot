from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from dotenv import load_dotenv
from TelegramBot.TelegramBotFlow.tools.dalle_tool import DallETool
import os

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path=env_path)

def llm():

	return LLM(
		model=os.environ.get("AZURE_API_MODEL"),
		api_key=os.environ.get("AZURE_API_KEY"),
		base_url=os.environ.get("AZURE_API_BASE"),
		api_version=os.environ.get("AZURE_API_VERSION"),
	)

dalle = DallETool(
		model=os.environ.get("DALLE_MODEL"),
		prompt="A naturally beautiful woman",
		size=os.environ.get("SIZE"),
		quality=os.environ.get("QUALITY"),
		n=1
	)

@CrewBase
class TexttoPhoto():
	"""TTP crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def text_to_photo_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['text_to_photo_agent'],
			llm=llm(),
			tools=[dalle]
		)

	@task
	def text_to_photo_task(self) -> Task:
		return Task(
			config=self.tasks_config['text_to_photo_task']
		)

	@crew
	def crew(self) -> Crew:
		return Crew(
			agents=self.agents,  # Automatically created by the @agent decorator
			tasks=self.tasks,  # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,

	)