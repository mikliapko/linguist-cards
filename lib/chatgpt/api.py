from config import CHATGPT_MAX_TOKEN, CHATGPT_MODEL
from lib.api_client import ApiClientBase


class ChatGPTApiBase(ApiClientBase):
    api_path_prefix = "v1/chat/"
    auth_type = "bearer_token"

    def ask(self, data: dict) -> str:
        endpoint = "completions"
        response = self.request("POST", endpoint, json_body=data)
        return response['choices'][0]['message']['content']


class ChatGPTApiHelper(ChatGPTApiBase):
    def __init__(self, base_url, token, language, check_validity=True):
        super().__init__(base_url=base_url, token=token)
        self.language = language
        self.check_validity = check_validity

    # ruff: noqa: E501
    def ask_for_translation(self, word: str) -> str:
        data = {
            "model": CHATGPT_MODEL,
            "messages": [
                {"role": "system", "content": f"You are a helpful {self.language} language assistant."},
                {"role": "user", "content": (f"For the word or phrase '{word}' in {self.language}, check validity"
                                             f"(no grammar or lexical mistakes). If it is correct, please provide:\n"
                                             "A - A brief explanation (<100 symbols) in the same language (only explanation, without `word is ...`).\n"
                                             "B - An example sentence using the word/phrase in that language.\n"
                                             "C - Word/phrase translation into Russian with the reference to the meaning in A and B.\n"
                                             "D - Transcription.\n"
                                             "E - One synonym\n\n"
                                             "The response format should be:\n"
                                             "explanation: A\nexample: B\ntranslation: C\ntranscription: D\nsynonym: E\n\n"
                                             "If the word/phrase is incorrect, return one word 'False' in reply")},
            ],
            "max_tokens": CHATGPT_MAX_TOKEN
        }
        reply = self.ask(data)

        if self.check_validity and reply.strip().lower() == "false":
            raise ValueError(f"The word or phrase {word} is incorrect")

        return reply
