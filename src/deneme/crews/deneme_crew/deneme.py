from sys import api_version

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from dotenv import load_dotenv
import os

# Uncomment the following line to use an example of a custom tool
# from deneme_crew.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool

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
class Deneme():
	"""Deneme crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	// Todo: Kullanılmayan pull_data_example vs. alanları kaldır. Ayrıca crew adını değiştir diğerleriyle uyumlu yap. Birde hepsini underscore formatında isimlendir. Örneğin: "photo_decision_crew" gibi.

	@before_kickoff # Optional hook to be executed before the crew starts
	def pull_data_example(self, inputs):
		# Todo: bu alanlar kullanılmıyor kaldır.
		# Example of pulling data from an external API, dynamically changing the inputs
		inputs['extra_data'] = "This is extra data"
		return inputs

	@after_kickoff # Optional hook to be executed after the crew has finished
	def log_results(self, output):
		# Example of logging results, dynamically changing the output
		print(f"Results: {output}")
		return output

	@agent
	def flort_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['flort_agent'],
			llm=llm(),
		)

	@task
	def flort_task(self) -> Task:
		return Task(
			config=self.tasks_config['flort_task']
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Deneme crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,

			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)