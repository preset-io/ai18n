import os
import random
import re
import sys
from typing import Any, Dict, List, Optional, Set

import yaml
from polib import POFile, pofile

from ai18n.config import conf
from ai18n.message import Message
from ai18n.openai import OpenAIMessageTranslator


class Translator:
    def __init__(
        self, api_key: str = None, model: str = None, yaml_file: str = None
    ) -> None:
        self.messages: Dict[str, Message] = {}
        self.yaml_file = yaml_file or "./translations.yaml"
        self.po_files_dict: Dict[str, POFile] = {}
        self.api_key = api_key

        if self.yaml_file:
            self.from_yaml(self.yaml_file)
        if self.api_key:
            self.openai_translator = OpenAIMessageTranslator(
                api_key=self.api_key, model=model
            )

    def from_dict(self, data: Dict[str, Any]) -> None:
        messages = data.get("messages") or []
        languages = set()
        for message_data in messages:
            message = Message.from_dict(message_data)
            self.messages[message.trimmed_msgid] = message
            languages |= set(message.po_translations.keys())
            languages |= set(message.ai_translations.keys())
        print(
            f"Loaded {len(self.messages)} messages "
            f"referencing {len(languages)} languages"
        )

    def from_yaml(self, yaml_file: Optional[str] = None) -> None:
        print(f"Loading translations from YAML file '{yaml_file}'")
        yaml_location = yaml_file or self.yaml_file
        try:
            with open(yaml_location, "r") as file:
                data = yaml.safe_load(file)
        except FileNotFoundError:
            print("YAML file not found. Creating a new one.")
            data = {"messages": {}}
        return self.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        sorted_keys = sorted(self.messages.keys())
        return {"messages": [self.messages[k].to_dict() for k in sorted_keys]}

    def to_yaml(self, yaml_file: Optional[str] = None) -> None:
        yaml_location = yaml_file or self.yaml_file
        print(f"Saving translations to YAML file '{yaml_location}'")
        data = self.to_dict()

        def export_yaml() -> None:
            with open(yaml_location, "w", encoding="utf-8") as file:
                yaml.dump(data, file, allow_unicode=True, sort_keys=False)

        try:
            export_yaml()
        except KeyboardInterrupt:
            print(
                "Export interrupted. Retrying to prevent partial file... Please hold on for a sec."
            )
            export_yaml()
            print("Export completed to '{yaml_location}', exiting now...")
            sys.exit(1)

        print(f"Export completed to '{yaml_location}'")

    def randomize_messages(self) -> None:
        keys = list(self.messages.keys())
        random.shuffle(keys)  # Shuffle the list of keys
        self.messages = {
            k: self.messages[k] for k in keys
        }  # Create a new dict with shuffled keys

    def trim_message(self, msgid: str) -> str:
        return msgid.strip()

    def flush_ai(self) -> None:
        for message in self.messages.values():
            message.ai_translations = {}

    def add_message(self, message: Message) -> None:
        trimmed_msgid = self.trim_message(message.msgid)
        self.messages[trimmed_msgid] = message

    def find_message(self, msgid: str) -> Optional[Message]:
        trimmed_msgid = self.trim_message(msgid)
        return self.messages.get(trimmed_msgid)

    def load_po_files(self, po_folder: str) -> None:
        for filepath in self.get_po_files(po_folder):
            print(f"Loading file {filepath}")
            po_file = pofile(filepath)
            lang = po_file.metadata["Language"]
            self.po_files_dict[lang] = po_file
        self.merge_all_po_files()

    def merge_po_file(self, lang: str, po_file: POFile) -> None:
        for entry in po_file:
            msgid = str(entry.msgid)
            msgstr = str(entry.msgstr)
            trimmed_msgid = self.trim_message(msgid)
            message = self.find_message(trimmed_msgid)
            occurances: Set[str] = set({o[0] for o in entry.occurrences if o})
            flags: Set[str] = set(
                [flag for flag in entry.flags if flag.startswith("ai18n")]
            )

            if not message:
                message = Message(msgid=trimmed_msgid)
                self.add_message(message)

            existing_translation = message.po_translations.get(lang)
            if msgstr and (
                not existing_translation or len(msgstr) > len(existing_translation)
            ):
                # In some cases, there may be multiple translations for the same message
                # that are trimmed in different ways. We should prefer the longer one.
                message.po_translations[lang] = msgstr
            message.occurances |= set(occurances)
            message.flags[lang] |= flags

            if lang == conf["main_language"] and not msgstr:
                # If the message is empty in the main language, use the msgid
                message.po_translations[lang] = msgid

    def merge_all_po_files(self) -> None:
        for lang, po_file in self.po_files_dict.items():
            self.merge_po_file(lang, po_file)

    def get_po_files(self, po_folder: str) -> List[str]:
        po_files = []
        for root, _, files in os.walk(po_folder):
            for file in files:
                if file.endswith(".po"):
                    po_files.append(os.path.join(root, file))
        return po_files

    def translate(
        self,
        lang: Optional[str] = None,
        dry_run: bool = False,
        checkpoint: bool = True,
        message_regex: Optional[str] = None,
        force: bool = False,
    ) -> None:
        messages_to_translate = []
        for msg in self.messages.values():
            if not message_regex or re.match(message_regex, msg.msgid):
                if msg.requires_translation(lang) or force:
                    messages_to_translate.append(msg)
        if lang:
            print(
                f"Identified {len(messages_to_translate)} messages to translate to {lang}"
            )
        else:
            print(f"Identified {len(messages_to_translate)} messages to translate")
        for i, msg in enumerate(messages_to_translate):
            print(f"Translating message ({i}/{len(messages_to_translate)})")
            self.openai_translator.translate_message(msg, dry_run=dry_run, force=force)
            if checkpoint:
                self.to_yaml()
        print(f"Translation complete, processed {len(messages_to_translate)} messages")

    def push_po_file(
        self,
        lang: str,
        po_file: POFile,
        prefer_ai: bool = False,
        occurrence_regex: Optional[str] = None,
    ) -> None:
        msg_count = 0
        for message in self.messages.values():
            entry = po_file.find(message.msgid)
            if entry and message.ai_translations:
                if occurrence_regex and not any(
                    re.match(occurrence_regex, o[0]) for o in entry.occurrences
                ):
                    continue
                po_translation = message.po_translations.get(lang, entry.msgstr)
                ai_translation = message.ai_translations.get(lang, entry.msgstr)
                if prefer_ai:
                    # If there is a ai18n-force flag, force the po translation
                    if "ai18n-force" in (message.flags.get(lang) or []):
                        translation = po_translation
                    else:
                        translation = ai_translation or po_translation
                else:
                    translation = po_translation or ai_translation
                entry.msgstr = translation
                msg_count += 1
        print(f"Exporting {msg_count} messages to {lang}.po")
        po_file.save()

    def push_all_po_files(
        self, prefer_ai: bool = False, occurrence_regex: Optional[str] = None
    ) -> None:
        for lang, po_file in self.po_files_dict.items():
            self.push_po_file(lang, po_file, prefer_ai, occurrence_regex)

    @staticmethod
    def count_words(text: str) -> int:
        """Helper function to count words in a string."""
        words = re.findall(r"\b\w+\b", text)  # Find word-like sequences
        return len(words)

    def compute_translation_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Compute percentage of strings and words translated for each language."""
        # Initialize statistics data structure
        stats = {
            lang: {
                "po_translated_strings": 0,
                "ai_translated_strings": 0,
                "total_strings": 0,
                "po_translated_words": 0,
                "ai_translated_words": 0,
                "total_words": 0,
                "orphaned": 0,
            }
            for lang in conf["target_languages"]
        }

        for msgid, message in self.messages.items():
            # Assume English text for counting words
            english_word_count = self.count_words(msgid)

            for lang in conf["target_languages"]:
                po_translation = message.po_translations.get(lang)
                ai_translation = message.ai_translations.get(lang) or po_translation
                stats[lang]["total_strings"] += 1
                stats[lang]["total_words"] += english_word_count

                # Check if the translation is orphaned (missing occurrences)
                if len(message.occurances) == 0:
                    stats[lang]["orphaned"] += 1

                # If the message is translated (non-empty)
                if po_translation:
                    stats[lang]["po_translated_strings"] += 1
                    stats[lang]["po_translated_words"] += english_word_count
                # If the message is translated (non-empty)
                if ai_translation:
                    stats[lang]["ai_translated_strings"] += 1
                    stats[lang]["ai_translated_words"] += english_word_count

        return stats

    def print_report(self) -> None:
        """Print a report showing translation statistics for each language."""
        stats = self.compute_translation_statistics()

        print("Translation Statistics Report:")
        print(f"{'Language':<10} | {'PO %':<20} | {'Orphaned':<10} | {'PO+AI %':<10}")
        print("=" * 60)

        for lang, data in stats.items():
            total_strings = data["total_strings"]
            # total_words = data["total_words"]
            po_translated_strings = data["po_translated_strings"]
            # po_translated_words = data["po_translated_words"]
            ai_translated_strings = data["ai_translated_strings"]
            # ai_translated_words = data["ai_translated_words"]
            orphaned = data["orphaned"]

            # Calculate percentage of translated strings and words
            string_po_translation_percentage = (
                (po_translated_strings / total_strings) * 100 if total_strings > 0 else 0
            )
            # Calculate percentage of translated strings and words
            string_ai_translation_percentage = (
                (ai_translated_strings / total_strings) * 100 if total_strings > 0 else 0
            )

            # Print the report row
            print(
                f"{lang:<10} | {string_po_translation_percentage:>19.2f}% | {orphaned:<10} | {string_ai_translation_percentage:>8.2f}%"
            )
