from ai18n.translator import Translator


def test_load_po_file(po_file: str) -> None:
    translator = Translator("./test.yml")
    translator.load_po_files("./fixtures/po_files")

    # Check that messages are loaded correctly
    assert translator.messages["Hello"].msgid == ""
    assert translator.messages["Goodbye"].msgid == "Adiós"
