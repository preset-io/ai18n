import argparse
import os

from transpo.openai import OpenAIMessageTranslator
from transpo.translator import Translator

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TRANSLATION_YAML_FILE = "./translations.yaml"


def main() -> None:
    parser = argparse.ArgumentParser(description="Superset Translation Tool")
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

    # Report subcommand
    report_parser = subparsers.add_parser(  # NOQA
        "report", help="Generate a report of translation statistics"
    )

    path_to_po_files = os.path.join(
        os.path.dirname(__file__), "../../superset/translations/"
    )
    args = parser.parse_args()

    translator = Translator(path_to_po_files)
    translator.randomize_messages()
    translator.to_yaml(TRANSLATION_YAML_FILE)
    print(args.command)

    if args.command == "translate":
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
        # Implement your reporting logic here
        translator.print_report()


if __name__ == "__main__":
    main()
