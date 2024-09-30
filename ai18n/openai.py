import datetime
import json
import textwrap
from typing import Dict, List

from openai import OpenAI

from ai18n.constants import DEFAULT_LANGUAGES
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

    def build_prompt(self, message: Message) -> str:
        """Create a translation prompt for the OpenAI API."""
        occurances_str = ""
        if message.occurances:
            occurances_str = (
                "For context here are the files that the string appears in:\n"
            )
            occurances_str += "\n".join([f"- {s}" for s in message.occurances])
        prompt = textwrap.dedent(f"""
            Translate the following text for the UI of Apache Superset, a web-based business intelligence software.
            This is in the context of a .po file, so please follow the appropriate formatting for pluralization if needed.
            Other language translations are provided as a reference where available, but they may need improvement or correction.
            Ensure the translation is appropriate for a technical audience and aligns with common UI/UX terminology.

            Instructions:
            - Provide the output in JSON format (no markdown) with the language code as a key and the translated string as the value.
            - Provide translations for the following languages: {DEFAULT_LANGUAGES}
            - Follow the pluralization rules for the target language if applicable.
            - Only pass the key to overwrite if your translation is significantly better than the existing one.

            {occurances_str}

            Original string to translate: '{message.msgid}'
        """)
        # TODO: add occurances to the prompt

        # Add existing translations as a reference
        other_languages = "\n".join(
            f"{lang}: '{translation}'"
            for lang, translation in message.po_translations.items()
            if translation
        )
        if other_languages:
            prompt += f"\nExisting translations for reference:\n{other_languages}\n"
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