# ---------------------------------------- #

# Classe para chamada de agentes

# ---------------------------------------- #

import os
from openai import OpenAI

class Agent:
    """
    Base para a chamada do agente de IA
    Métodos:
        get_llm_client
        call_llm
    """

    def __init__(self,
                 model_name: str,
                 temperature: float):
        self.model_name = model_name
        self.temperature = temperature


    def get_llm_client(self):
        """
        Faz a chamada do agente de IA
        return:
            instância do agente de IA
        """
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=os.environ["HF_TOKEN"],
        )
        return client

    def call_llm(self, client, prompt: str, temperature: float):
        """
        Passa comando para o agente de IA.
        parametros:
            prompt: prompt a ser passado para IA.
            temperature: temperatura da IA.
        return:
            resposta do agente de IA
        """
        messages = [
            {
                "role": "system",
                "content": "Você é um assistente para extrair links pertinentes de textos."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        response_search = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=temperature
        )
        return response_search.choices[0].message.content
