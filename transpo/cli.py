import argparse
import os

from transpo.openai import OpenAIMessageTranslator
from transpo.translator import Translator

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
        "po_files_folder",
        type=str,
        nargs="?",
        default=os.getcwd(),
        help="Folder where .po files are located (default: current directory)"
    )

    # Report subcommand
    report_parser = subparsers.add_parser(
        "report", help="Generate a report of translation statistics"
    )
    report_parser.add_argument(
        "po_files_folder",
        type=str,
        nargs="?",
        default=os.getcwd(),
        help="Folder where .po files are located (default: current directory)"
    )

    args = parser.parse_args()

    # If no command is provided, print help
    if args.command is None:
        parser.print_help()
        return

    # Use the provided folder path or default to the current directory
    path_to_po_files = args.po_files_folder
    print(f"Using PO files from: {path_to_po_files}")

    translator = Translator(path_to_po_files)
    translator.randomize_messages()

    if args.command == "translate":
        translator.to_yaml(TRANSLATION_YAML_FILE)
        if not OPENAI_API_KEY:
            print("Error: OPENAI_API_KEY environment variable is not set.")
            return
        openai_translator = OpenAIMessageTranslator(
            api_key=OPENAI_API_KEY, model=args.model
        )

        for _, message in translator.messages.items():
            openai_translator.translate_and_update(message)

        translator.push_all_po_files()

    elif args.command == "report":
        translator.print_report()


if __name__ == "__main__":
    main()

