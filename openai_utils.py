import os
import json
import re
from openai import OpenAI

class OpenAI_Chat():
    def __init__(self, client=None, config=None, allow_log=False):
        self.allow_log = allow_log
        self.config = config
        # default parameters - can be overrided using config
        self.temperature = 0.7

        if "temperature" in config:
            self.temperature = config["temperature"]

        if "api_type" in config:
            raise Exception(
                "Passing api_type is now deprecated. Please pass an OpenAI client instead."
            )

        if "api_base" in config:
            raise Exception(
                "Passing api_base is now deprecated. Please pass an OpenAI client instead."
            )

        if "api_version" in config:
            raise Exception(
                "Passing api_version is now deprecated. Please pass an OpenAI client instead."
            )

        if client is not None:
            self.client = client
            return

        if config is None and client is None:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            return

        if "api_key" in config:
            self.client = OpenAI(api_key=config["api_key"])

    def system_message(self, message: str) -> any:
        return {"role": "system", "content": message}

    def user_message(self, message: str) -> any:
        return {"role": "user", "content": message}

    def assistant_message(self, message: str) -> any:
        return {"role": "assistant", "content": message}

    def extract_sql(self, llm_response):
        """
        Extracts the first SQL statement after the word 'select', ignoring case,
        matches until the first semicolon, three backticks, or the end of the string,
        and removes three backticks if they exist in the extracted string.

        Args:
        - llm_response (str): The string to search within for an SQL statement.

        Returns:
        - str: The first SQL statement found, with three backticks removed, or an empty string if no match is found.
        """
        # Remove ollama-generated extra characters
        llm_response = llm_response.replace("\\_", "_")
        llm_response = llm_response.replace("\\", "")

        # Regular expression to find ```sql' and capture until '```'
        sql = re.search(r"```sql\n((.|\n)*?)(?=;|\[|```)", llm_response, re.DOTALL)
        # Regular expression to find 'select, with (ignoring case) and capture until ';', [ (this happens in case of mistral) or end of string
        select_with = re.search(r'(select|(with.*?as \())(.*?)(?=;|\[|```)',
                                llm_response,
                                re.IGNORECASE | re.DOTALL)
        if sql:
            if self.allow_log:
                self.log(
                f"Output from LLM: {llm_response} \nExtracted SQL: {sql.group(1)}")
            return sql.group(1).replace("```", "")
        elif select_with:
            if self.allow_log:
                self.log(
                f"Output from LLM: {llm_response} \nExtracted SQL: {select_with.group(0)}")
            return select_with.group(0)
        else:
            return llm_response
        
    def submit_prompt(self, prompt, **kwargs) -> str:
        if prompt is None:
            raise Exception("Prompt is None")

        if len(prompt) == 0:
            raise Exception("Prompt is empty")

        # Count the number of tokens in the message log
        # Use 4 as an approximation for the number of characters per token
        num_tokens = 0
        for message in prompt:
            num_tokens += len(message["content"]) / 4

        if kwargs.get("model", None) is not None:
            model = kwargs.get("model", None)
            print(
                f"Using model {model} for {num_tokens} tokens (approx)"
            )
            response = self.client.chat.completions.create(
                model=model,
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )
        elif kwargs.get("engine", None) is not None:
            engine = kwargs.get("engine", None)
            print(
                f"Using model {engine} for {num_tokens} tokens (approx)"
            )
            response = self.client.chat.completions.create(
                engine=engine,
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )
        elif self.config is not None and "engine" in self.config:
            print(
                f"Using engine {self.config['engine']} for {num_tokens} tokens (approx)"
            )
            response = self.client.chat.completions.create(
                engine=self.config["engine"],
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )
        elif self.config is not None and "model" in self.config:
            print(
                f"Using model {self.config['model']} for {num_tokens} tokens (approx)"
            )
            if "json_schema" in self.config:
                if self.config["json_schema"]:
                    response = self.client.chat.completions.parse(
                        model=self.config["model"],
                        messages=prompt,
                        stop=None,
                        temperature=self.temperature,
                        response_format=self.config["json_schema"]
                    )
                    return response.choices[0].message.parsed
                else:
                    response = self.client.chat.completions.create(
                        model=self.config["model"],
                        messages=prompt,
                        stop=None,
                        temperature=self.temperature,
                    )
            else:
                response = self.client.chat.completions.create(
                    model=self.config["model"],
                    messages=prompt,
                    stop=None,
                    temperature=self.temperature,
                )

        else:
            if num_tokens > 3500:
                model = "gpt-3.5-turbo-16k"
            else:
                model = "gpt-3.5-turbo"

            print(f"Using model {model} for {num_tokens} tokens (approx)")
            response = self.client.chat.completions.create(
                model=model,
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )

        # Find the first response from the chatbot that has text in it (some responses may not have text)
        for choice in response.choices:
            if "text" in choice:
                return choice.text

        # If no response with text is found, return the first response's content (which may be empty)
        return response.choices[0].message.content