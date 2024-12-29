from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from deneme.tools.custom_tool import ElevenLabsTool
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

# Todo: .env altına değişkenleri.
elevenlabs = ElevenLabsTool(
		prompt="Naber",
        voice_id="KbaseEXyT9EE0CQLEfbB",
		model_id="eleven_multilingual_v2",
        stability=0.7,
        similarity_boost=0.8,
    )


@CrewBase
class TexttoSpeech():
	"""TTS crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def text_to_speech_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['text_to_speech_agent'],
			llm=llm(),
			tools=[elevenlabs]
		)

	@task
	def text_to_speech_task(self) -> Task:
		return Task(
			config=self.tasks_config['text_to_speech_task']
		)

	@crew
	def crew(self) -> Crew:
		return Crew(
			agents=self.agents,  # Automatically created by the @agent decorator
			tasks=self.tasks,  # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,

	)