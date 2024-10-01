import os

from ai18n.translator import Translator

current_dir = os.path.dirname(os.path.abspath(__file__))


def test_load_po_file() -> None:
    # Get the directory of the current module

    # Build the path to the fixtures folder relative to the current module
    po_files_folder = os.path.join(current_dir, "fixtures", "po")
    yaml_file = os.path.join(current_dir, "test.yml")

    translator = Translator(yaml_file)
    translator.load_po_files(po_files_folder)

    assert len(translator.messages["Goodbye"].po_translations) == 2

    # Check that messages are loaded correctly
    assert translator.messages["Hello"].msgid == "Hello"

    # Check that translations are loaded correctly
    assert translator.messages["Goodbye"].po_translations["sp"] == "Adiós"
    assert translator.messages["Goodbye"].po_translations["en"] == "BeBye"
    assert translator.messages["Hello"].po_translations["en"] == "Hi"
