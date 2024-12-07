from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from dotenv import load_dotenv
from crewai_tools import DallETool
import os

dalle = DallETool(
		model="dall-e-3",
		prompt="{fiziksel özellikler}",
		size="1024x1024",
		quality="standard",
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