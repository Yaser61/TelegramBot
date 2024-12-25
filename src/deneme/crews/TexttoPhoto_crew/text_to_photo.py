from openai import AzureOpenAI

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from dotenv import load_dotenv
from crewai_tools import DallETool
import os

def llm():
	env_path = r"C:\Users\trabz\Desktop\PyCharm\deneme\src\deneme\.env" #os.path.join(os.path.dirname(__file__), '.env')
	load_dotenv(dotenv_path=env_path)

	return LLM(
		model=os.environ.get("AZURE_API_MODEL"),
		api_key=os.environ.get("AZURE_API_KEY"),  # Replace with KEY1 or KEY2
		base_url=os.environ.get("AZURE_API_BASE"),  # example: https://example.openai.azure.com/
		api_version=os.environ.get("AZURE_API_VERSION"),  # example: 2024-08-01-preview
	)

dalle = DallETool(
		model="dall-e-3-1",
		prompt="A naturally beautiful woman",
		size="1024x1024",
		quality="standard",
		n=1
		)

@CrewBase
class TexttoPhoto():
	"""TTP crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@before_kickoff  # Optional hook to be executed before the crew starts
	def pull_data_example(self, inputs):
		# Example of pulling data from an external API, dynamically changing the inputs
		inputs['extra_data'] = "This is extra data"
		return inputs

	@after_kickoff  # Optional hook to be executed after the crew has finished
	def log_results(self, output):
		# Example of logging results, dynamically changing the output
		print(f"Results: {output}")
		return output

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