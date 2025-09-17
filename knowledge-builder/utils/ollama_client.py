import requests
from ..config import settings


class OllamaClient:
    def __init__(self, host=settings.OLLAMA_HOST, model=settings.OLLAMA_MODEL):
        self.host = host
        self.model = model

    def generate(self, prompt: str) -> str:
        """使用Ollama生成文本"""
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Ollama请求失败: {e}")
            return None