import argparse
import os

from ai18n.openai import OpenAIMessageTranslator
from ai18n.translator import Translator

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TRANSLATION_YAML_FILE = "./translations.yaml"


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
    translate_parser.add_argument(
        "--po-files-folder",
        type=str,
        default=os.getcwd(),
        help="Folder where .po files are located (default: current directory)",
    )

    # Report subcommand
    report_parser = subparsers.add_parser(
        "report", help="Generate a report of translation statistics"
    )
    report_parser.add_argument(
        "--po-files-folder",
        type=str,
        default=os.getcwd(),
        help="Folder where .po files are located (default: current directory)",
    )

    # po pull subcommand
    pull_parser = subparsers.add_parser(
        "po-pull", help="Pull translations from .po files into the YAML file"
    )
    pull_parser.add_argument(
        "--po-files-folder",
        type=str,
        default=os.getcwd(),
        help="Folder where .po files are located (default: current directory)",
    )

    # flush-ai subcommand
    flush_ai_parser = subparsers.add_parser(
        "flush-ai", help="Flush all translations from the YAML file"
    )
    flush_ai_parser.add_argument(
        "--po-files-folder",
        type=str,
        default=os.getcwd(),
        help="Folder where .po files are located (default: current directory)",
    )

    # po push subcommand
    push_parser = subparsers.add_parser(
        "po-push", help="Push translations from the YAML file to .po files"
    )
    push_parser.add_argument(
        "--po-files-folder",
        type=str,
        default=os.getcwd(),
        help="Folder where .po files are located (default: current directory)",
    )

    args = parser.parse_args()

    # If no command is provided, print help
    if args.command is None:
        parser.print_help()
        return

    # Use the provided folder path or default to the current directory
    translator = Translator(TRANSLATION_YAML_FILE)

    if args.command == "translate":
        translator.to_yaml(TRANSLATION_YAML_FILE)
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
                translator.to_yaml(TRANSLATION_YAML_FILE)

    elif args.command == "report":
        translator.print_report()

    elif args.command == "po-pull":
        translator.load_po_files(args.po_files_folder)
        translator.merge_all_po_files()
        translator.to_yaml(TRANSLATION_YAML_FILE)

    elif args.command == "po-push":
        translator.load_po_files(args.po_files_folder)
        translator.push_all_po_files()

    elif args.command == "flush-ai":
        translator.flush_ai()
        translator.to_yaml(TRANSLATION_YAML_FILE)


if __name__ == "__main__":
    main()
