import os
from openai import OpenAI

class Agent:
    """
    Base para a chamada do agente de IA
    Métodos:
        get_llm_client
        call_llm
    """

    def __init__(self):
        pass

    def get_llm_client(self):
        """
        Faz a chamada do agente de IA via OpenRouter
        return:
            instância do agente de IA
        """
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["API_KEY_OR"],
        )
        return client

    def call_llm(self, client, texto: str, temperature: float):
        """
        Passa comando para o agente de IA.
        parametros:
            prompt: prompt a ser passado para IA.
            temperature: temperatura da IA.
        return:
            resposta do agente de IA
        """
        SCHEMA = {
            "type": "object",
            "properties": {
                "titulo": {"type": ["string", "null"]},
                "data_noticia": {"type": ["string", "null"]},
                "data_ocorrido": {"type": ["string", "null"]},

                "pessoas_citadas": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "tipo": {
                                "type": ["string", "null"],
                                "enum": ["individual", "grupo", "null"]
                            },
                            "nome": {"type": ["string", "null"]},
                            "papel": {
                                "type": ["string", "null"],
                                "enum": [
                                    "vitima",
                                    "suspeito",
                                    "policial",
                                    "ONG",
                                    "testemunha",
                                    "outros",
                                    "desconhecido",
                                    "null"
                                ]
                            },
                            "quantidade": {"type": ["integer", "null"]},
                            "descricao": {"type": ["string", "null"]}
                        }
                    }
                },

                "local": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "cidade": {"type": ["string", "null"]},
                            "estado": {"type": ["string", "null"]},
                            "pais": {"type": ["string", "null"]},
                        },
                    },
                },

                "operacao": {"type": ["string", "null"]},
                "organizacao_criminosa": {"type": ["string", "null"]},
                "modus_operandi": {"type": ["string", "null"]},

                "orgaos_envolvidos": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                },

                "n_vitimas": {"type": ["integer", "null"]},
                "n_vitimas_brasileiras": {"type": ["integer", "null"]},
                "n_mulheres": {"type": ["integer", "null"]},
                "n_homens": {"type": ["integer", "null"]},
                "n_criancas": {"type": ["integer", "null"]},

                "faixa_etaria_vitimas": {
                    "type": ["object", "null"],
                    "properties": {
                        "Crianca": {"type": ["integer", "null"]},
                        "Adolescente": {"type": ["integer", "null"]},
                        "Adulto": {"type": ["integer", "null"]},
                        "Idoso": {"type": ["integer", "null"]},
                    },
                }
            },

            "required": ["titulo", "local", "orgaos_envolvidos"],
        }
        messages = [
            {
                "role": "system",
                "content": (
                    "Voce e um assistente de extracao estruturada de noticias. "
                    "Nao invente informacoes. Se nao houver evidencia explicita, retorne null. Papéis possíveis para o campo pessoas_citadas: vitima, suspeito, policial, ONG, testemunha, outros"
                ),
            },
            {
                "role": "user",
                "content": (
                    "A partir da notícia abaixo, extraia as seguintes informações, se houver:\n\n"
                    "- titulo\n"
                    "- data_noticia\n"
                    "- pessoas_citadas (lista de objeto com o tipo, nome e papel do indivíduo, se não houver nome inclua como null)\n"
                    "- data_ocorrido\n"
                    "- local (lista de cidade, estado e país para cada local envolvido)\n"
                    "- operacao (descrição da operação policial)\n"
                    "- organizacao_criminosa\n"
                    "- modus_operandi\n"
                    "- orgaos_envolvidos\n\n"
                    "- n_vitimas (retorna o número de vítimas citadas)\n\n"
                    f"Notícia:\n{texto}"
                )
            }
        ]
        modelo_gemini = "google/gemini-2.5-flash-lite"
        completion = client.chat.completions.create(
            model=modelo_gemini,
            messages=messages,
            response_format=SCHEMA,
            temperature=temperature
        )
        return completion.choices[0].message.content