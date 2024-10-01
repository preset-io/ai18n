import datetime
import json
import os
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader
from openai import OpenAI

from ai18n.config import conf
from ai18n.message import Message

MAX_TOKEN = 4096


class OpenAIMessageTranslator:
    def __init__(
        self, api_key: str, model: str = "gpt-4", temperature: float = 0.3
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(
            api_key=api_key
        )  # Instantiate client once in the constructor
        module_dir = os.path.dirname(os.path.abspath(__file__))

        # Set the template directory relative to the current module
        template_dir = os.path.join(module_dir, "templates")
        # Looking for a custom template folder in the configuration
        if template_folder := conf.get("template_folder"):
            template_dir = template_folder

        self.env = Environment(loader=FileSystemLoader(template_dir))

    def build_prompt(self, message: Message) -> str:
        """Create a translation prompt for the OpenAI API using Jinja2."""
        template = self.env.get_template("prompt.jinja")

        # Prepare the context for rendering the template
        context = {
            "languages": conf["target_languages"],
            "msgid": message.msgid,
            "occurances": message.occurances or [],
            "extra_context": conf.get("prompt_extra_context"),
            "other_languages": {
                lang: translation
                for lang, translation in message.po_translations.items()
                if translation
            },
        }

        # Render the template with the provided context
        prompt = template.render(context) or ""

        # Output the generated prompt for debugging purposes
        print("-=-" * 20)
        print(prompt)
        print("-=-" * 20)

        return prompt

    def execute_prompt(self, message: Message) -> Dict[str, str]:
        prompt = self.build_prompt(message)

        # Use the chat completion endpoint for the chat models
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator proficient in multiple languages.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=MAX_TOKEN,
            temperature=self.temperature,
        )

        response_text = response.choices[0].message.content.strip()
        print(response_text)
        print("-=-" * 20)
        translations = {}
        try:
            translations = json.loads(response_text)  # Expect the response in JSON format
        except json.JSONDecodeError:
            print("Error: Unable to parse JSON from OpenAI response.")
        except Exception as e:
            print(f"Error: {e}")
        return translations

    def translate_message(self, message: Message, force: bool = False) -> None:
        if message.requires_translation() or force:
            translations = self.execute_prompt(message)
            if translations:
                message.merge_ai_output(translations)
                message.update_metadata(self.model, datetime.datetime.now())

    def translate(self, messages: List[Message], force: bool = False) -> None:
        for message in messages:
            self.translate_message(message, force=force)
