import os
import random
import re
from typing import Any, Dict, List, Optional

import yaml
from polib import POFile, pofile

from ai18n.config import conf
from ai18n.message import Message


class Translator:
    def __init__(self, yaml_file: Optional[str]) -> None:
        self.messages: Dict[str, Message] = {}
        self.yaml_file = yaml_file or "./translations.yaml"
        self.po_files_dict: Dict[str, POFile] = {}

        if self.yaml_file:
            self.from_yaml(self.yaml_file)

    def from_dict(self, data: Dict[str, Any]) -> None:
        messages = data.get("messages") or []
        for message_data in messages:
            message = Message.from_dict(message_data)
            self.messages[message.trimmed_msgid] = message

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
        with open(yaml_location, "w", encoding="utf-8") as file:
            yaml.dump(data, file, allow_unicode=True, sort_keys=False)

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
            matched_message = self.find_message(trimmed_msgid)
            occurances: List[str] = sorted({o[0] for o in entry.occurrences})
            if matched_message:
                matched_message.po_translations[lang] = msgstr
                matched_message.occurances = occurances
            elif msgstr:
                new_message = Message(msgid=trimmed_msgid)
                new_message.po_translations[lang] = msgstr
                new_message.occurances = occurances
                self.add_message(new_message)

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

    def push_po_file(self, lang: str, po_file: POFile) -> None:
        for message in self.messages.values():
            entry = po_file.find(message.msgid)
            if entry and message.ai_translations:
                entry.msgstr = message.ai_translations.get(lang, entry.msgstr)
        po_file.save()

    def push_all_po_files(self) -> None:
        for lang, po_file in self.po_files_dict.items():
            self.push_po_file(lang, po_file)

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
        print(
            f"{'Language':<10} | {'Translated Strings %':<20} | {'Orphaned':<10} | {'Words %':<10}"
        )
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
