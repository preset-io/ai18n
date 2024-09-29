import argparse
import os
from argparse import ArgumentParser

from ai18n.config import conf
from ai18n.openai import OpenAIMessageTranslator
from ai18n.translator import Translator

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TRANSLATION_YAML_FILE: str = conf.get("yaml_file") or "./translations.yaml"


def add_po_files_folder_arg(subparser: ArgumentParser) -> None:
    """Add --po-files-folder argument to the subparser."""
    po_folder_default = conf.get("po_folder_root") or os.path.join(os.getcwd())
    subparser.add_argument(
        "--po-files-folder",
        type=str,
        default=po_folder_default,
        help="Folder where .po files are located (default: current directory)",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Superset Translation Tool")

    # Define subcommands
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    # Translate subcommand
    translate_parser = subparsers.add_parser(
        "translate", help="Translate missing strings in .po files"
    )
    translate_parser.add_argument(
        "--target-language", type=str, help="Target language code"
    )
    translate_parser.add_argument("--batch-size", type=int, default=5, help="Batch size")
    translate_parser.add_argument("--dry-run", action="store_true", help="Dry run")
    translate_parser.add_argument(
        "--temperature", type=float, default=0.3, help="Translation temperature"
    )
    translate_parser.add_argument(
        "--model", type=str, default="gpt-4-turbo", help="OpenAI model to use"
    )
    add_po_files_folder_arg(translate_parser)

    # Report subcommand
    report_parser = subparsers.add_parser(
        "report", help="Generate a report of translation statistics"
    )
    add_po_files_folder_arg(report_parser)

    # po pull subcommand
    pull_parser = subparsers.add_parser(
        "po-pull", help="Pull translations from .po files into the YAML file"
    )
    add_po_files_folder_arg(pull_parser)

    # flush-ai subcommand
    flush_ai_parser = subparsers.add_parser(
        "flush-ai", help="Flush all translations from the YAML file"
    )
    add_po_files_folder_arg(flush_ai_parser)

    # po push subcommand
    push_parser = subparsers.add_parser(
        "po-push", help="Push translations from the YAML file to .po files"
    )
    add_po_files_folder_arg(push_parser)

    args = parser.parse_args()

    # If no command is provided, print help
    if args.command is None:
        parser.print_help()
        return

    # Use the provided folder path or default to the current directory
    translator = Translator(TRANSLATION_YAML_FILE)

    if args.command == "translate":
        translator.to_yaml()
        if not OPENAI_API_KEY:
            print("Error: OPENAI_API_KEY environment variable is not set.")
            return
        openai_translator = OpenAIMessageTranslator(
            api_key=OPENAI_API_KEY, model=args.model
        )

        for msg in translator.messages.values():
            if msg.requires_translation():
                openai_translator.translate_message(msg)
                # checkpointing after each message
                translator.to_yaml()

    elif args.command == "report":
        translator.print_report()

    elif args.command == "po-pull":
        print(args.po_files_folder)
        translator.load_po_files(args.po_files_folder)
        translator.to_yaml()

    elif args.command == "po-push":
        translator.load_po_files(args.po_files_folder)
        translator.push_all_po_files()

    elif args.command == "flush-ai":
        translator.flush_ai()
        translator.to_yaml()


if __name__ == "__main__":
    main()
