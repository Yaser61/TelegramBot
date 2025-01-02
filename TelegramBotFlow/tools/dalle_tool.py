import json
import os
from typing import Type
from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel

from crewai_tools.tools.base_tool import BaseTool

class ImagePromptSchema(BaseModel):
    """Input for Dall-E Tool."""

class DallETool(BaseTool):
    name: str = "Dall-E Tool"
    description: str = "Generates images using OpenAI's Dall-E model."
    args_schema: Type[BaseModel] = ImagePromptSchema

    model: str = "dall-e-3"
    prompt: str = "kedi"
    size: str = "1024x1024"
    quality: str = "standard"
    n: int = 1

    def _run(self, **kwargs) -> str:

        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(dotenv_path=env_path)

        client = AzureOpenAI(
            api_version=os.environ.get("API_VERSION"),
            azure_endpoint=os.environ.get("AZURE_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        )

        response = client.images.generate(
            model=self.model,
            prompt=self.prompt,
            size=self.size,
            quality=self.quality,
            n=self.n,
        )

        image_data = json.loads(response.model_dump_json())['data'][0]['url']

        return image_data
