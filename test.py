from openai_utils import OpenAI_Chat
from agent import BaseAgent
from key import gpt_key

gpt = OpenAI_Chat(config={"model": "gpt-4o-mini", "api_key": gpt_key})
agent = BaseAgent(llm=gpt, system_prompt="You are a helpful assistant.")
query = "Hello"
response = agent.generate(query)
print(response)