from openai_utils import OpenAI_Chat
from key import gpt_key

class BaseAgent:
    def __init__(self, llm: OpenAI_Chat, system_prompt) -> None:
        self.system_prompt = system_prompt
        self.language = "english"
        self.llm = llm
        self.chat_history = [self.llm.system_message(self.system_prompt)]

    def generate(self, query):
        self.chat_history.append(self.llm.user_message(query))
        response = self.llm.submit_prompt(self.chat_history)
        self.chat_history.append(self.llm.assistant_message(response))
        return response
    
    