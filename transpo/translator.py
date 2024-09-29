import os
import random
import re
from typing import Any, Dict, List, Optional

import yaml
from polib import POFile, pofile

from transpo.constants import DEFAULT_LANGUAGES
from transpo.message import Message


class Translator:
    def __init__(self, path_to_po_files: str) -> None:
        self.messages: Dict[str, Message] = {}
        self.path_to_po_files = path_to_po_files
        self.po_files_dict: Dict[str, POFile] = {}

        self.load_po_files()
        self.merge_all_po_files()

    @classmethod
    def from_dict(cls, data: Dict[str, Any], path_to_po_files: str) -> "Translator":
        translator = cls(path_to_po_files)
        for trimmed_msgid, message_data in data["messages"].items():
            message = Message.from_dict(message_data)
            translator.messages[trimmed_msgid] = message
        return translator

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        sorted_keys = sorted(self.messages.keys())
        return {"messages": {k: self.messages[k].to_dict() for k in sorted_keys}}

    @classmethod
    def from_yaml(cls, yaml_path: str, path_to_po_files: str) -> "Translator":
        with open(yaml_path, "r") as file:
            data = yaml.safe_load(file)
        return cls.from_dict(data, path_to_po_files)

    def to_yaml(self, yaml_path: str) -> None:
        print(f"Saving translations to YAML file...{yaml_path}")
        data = self.to_dict()
        with open(yaml_path, "w", encoding="utf-8") as file:
            yaml.dump(data, file, allow_unicode=True)

    def randomize_messages(self) -> None:
        keys = list(self.messages.keys())
        random.shuffle(keys)  # Shuffle the list of keys
        self.messages = {
            k: self.messages[k] for k in keys
        }  # Create a new dict with shuffled keys

    def trim_message(self, msgid: str) -> str:
        return msgid.strip()

    def add_message(self, message: Message) -> None:
        trimmed_msgid = self.trim_message(message.msgid)
        self.messages[trimmed_msgid] = message

    def find_message(self, msgid: str) -> Optional[Message]:
        trimmed_msgid = self.trim_message(msgid)
        return self.messages.get(trimmed_msgid)

    def load_po_files(self) -> None:
        for filepath in self.get_po_files():
            lang = filepath.split("/")[-3]
            print(f"Loading {lang} from {filepath}")
            if lang != "en":
                self.po_files_dict[lang] = pofile(filepath)

    def merge_po_file(self, lang: str, po_file: POFile) -> None:
        for entry in po_file:
            msgid = str(entry.msgid)
            msgstr = str(entry.msgstr)
            trimmed_msgid = self.trim_message(msgid)
            matched_message = self.find_message(trimmed_msgid)
            occurances = sorted({o[0] for o in entry.occurrences})
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

    def get_po_files(self) -> List[str]:
        po_files = []
        for root, _, files in os.walk(self.path_to_po_files):
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

    def compute_translation_statistics(self) -> Dict[str, Dict[str, float]]:
        """Compute percentage of strings and words translated for each language."""
        # Initialize statistics data structure
        stats = {
            lang: {
                "translated_strings": 0,
                "total_strings": 0,
                "translated_words": 0,
                "total_words": 0,
                "orphaned": 0,
            }
            for lang in DEFAULT_LANGUAGES
            if lang != "en"
        }

        for msgid, message in self.messages.items():
            # Assume English text for counting words
            english_word_count = self.count_words(msgid)

            for lang, translation in message.po_translations.items():
                stats[lang]["total_strings"] += 1
                stats[lang]["total_words"] += english_word_count

                # Check if the translation is orphaned (missing occurrences)
                if len(message.occurances) == 0:
                    stats[lang]["orphaned"] += 1

                # If the message is translated (non-empty)
                if translation:
                    stats[lang]["translated_strings"] += 1
                    stats[lang]["translated_words"] += english_word_count

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
            total_words = data["total_words"]
            translated_strings = data["translated_strings"]
            translated_words = data["translated_words"]
            orphaned = data["orphaned"]

            # Calculate percentage of translated strings and words
            string_translation_percentage = (
                (translated_strings / total_strings) * 100 if total_strings > 0 else 0
            )
            word_translation_percentage = (
                (translated_words / total_words) * 100 if total_words > 0 else 0
            )

            # Print the report row
            print(
                f"{lang:<10} | {string_translation_percentage:>19.2f}% | {orphaned:<10} | {word_translation_percentage:>8.2f}%"
            )
