from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
import os

def llm():
	env_path = os.path.join(os.path.dirname(__file__), '.env')
	load_dotenv(dotenv_path=env_path)

	return LLM(
		model=os.environ.get("AZURE_API_MODEL"),
		api_key=os.environ.get("AZURE_API_KEY"),  # Replace with KEY1 or KEY2
		base_url=os.environ.get("AZURE_API_BASE"),  # example: https://example.openai.azure.com/
		api_version=os.environ.get("AZURE_API_VERSION"),  # example: 2024-08-01-preview
	)

@CrewBase
class TextWithPhoto():
	"""Text with crew"""
	agents_config = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'CommonConfig/agents.yaml')
	tasks_config = 'config/tasks.yaml'

	@agent
	def common_elif(self) -> Agent:
		return Agent(
			config=self.agents_config['common_elif'],
			llm=llm(),
		)

	@task
	def flort_task_withphoto(self) -> Task:
		return Task(
			config=self.tasks_config['flort_task_withphoto']
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Deneme crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
		)