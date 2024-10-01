
# ai18n - AI-Powered PO Translation Tool

**ai18n** is a versatile tool for managing translations in PO files. Originally developed for Apache Superset, it leverages OpenAI to automate translation tasks, merging traditional PO workflows with AI enhancements. With built-in support for YAML-based translation memory, ai18n makes it easy to keep translations consistent and up-to-date across multiple languages.

## Key Features

- **AI-Powered Translations**: Automatically fill in missing translations using OpenAI models like `gpt-4`.
- **PO/YAML Syncing**: Manage translations centrally in a YAML file while keeping traditional PO files in sync.
- **Custom Reports**: Generate reports showing translation coverage across languages.
- **CLI Interface**: Easy-to-use command-line interface for translating, syncing, and reporting on translations.

## Installation

1. Clone the repository and install dependencies for both runtime and development:

    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    pip install -e .
    ```

2. Set your OpenAI API key:

    ```bash
    export OPENAI_API_KEY=<your-openai-api-key>
    ```

## Usage

### Configuration
```bash
export AI18N_TARGET_LANGUAGES=ar,de,es,fr,it,ja,ko,nl,pt,pt_BR,ru,sk,sl,tr,uk,zh,zh_TW
export AI18N_PO_FOLDER_ROOT="./translations/"
export AI18N_PROMPT_EXTRA_CONTEXT="These translation are part of Apache Superset, a Business Intelligence data exploration, visualization and dashboard open source application"
export AI18N_TEMPLATE_FOLDER="./templates/"
export AI18N_YAML_FILE=$AI18N_PO_FOLDER_ROOT/ai18n.yml
```

### General Commands

1. **Translate Missing Strings**:
    Run this command to use OpenAI for filling in missing translations:

    ```bash
    ai18n translate --po-files-folder <path-to-po-files> --batch-size 10 --temperature 0.5
    ```

2. **Generate a Translation Report**:
    Get insights into how many strings and words are translated:

    ```bash
    ai18n report --po-files-folder <path-to-po-files>
    ```

3. **PO/YAML Management**:
    - **Pull**: Load translations from PO files into the YAML memory.

      ```bash
      ai18n po-pull --po-files-folder <path-to-po-files>
      ```

    - **Push**: Push translations from the YAML back into PO files.

      ```bash
      ai18n po-push --po-files-folder <path-to-po-files>
      ```

4. **Flush AI Translations**:
    Clear all AI-generated translations from the YAML file:

    ```bash
    ai18n flush-ai
    ```

## Development Workflow

1. **Clone the repository**:

    ```bash
    git clone <repository-url>
    ```

2. **Install dependencies** for development:

    ```bash
    pip install -r requirements-dev.txt
    pip install -e .
    ```

3. **Run tests**:

    ```bash
    pytest
    ```

## License

ai18n is currently all-rights reserved to Preset, but could eventually be open source if it
turns out to not be much of a differentiator.

## Author

Built by the team behind Apache Superset, originally tailored for its multilingual support needs, but adaptable to any project that uses PO files for translations.


## Example/default prompt
```
Translate the following text for the UI of Apache Superset, a web-based business intelligence software.
This is in the context of a .po file, so please follow the appropriate formatting for pluralization if needed.
Other language translations are provided as a reference where available, but they may need improvement or correction.
Ensure the translation is appropriate for a technical audience and aligns with common UI/UX terminology.

Instructions:
- Provide the output in JSON format (no markdown) with the language code as a key and the translated string as the value.
- Provide translations for the following languages: ['sl', 'sk', 'pt_BR', 'ja', 'it', 'zh_TW', 'ru', 'pt', 'zh', 'uk', 'ar', 'nl', 'de', 'ko', 'fr', 'es', 'tr']
- Follow the pluralization rules for the target language if applicable.
- Only pass the key to overwrite if your translation is significantly better than the existing one.

Original string to translate: 'Could not fetch all saved charts'

Existing translations for reference:
sl: 'Vseh shranjenih grafikonov ni bilo mogoče pridobiti'
pt_BR: 'Não foi possível obter todos os gráficos salvos'
ja: '保存したすべてのチャートを取得できませんでした'
it: 'Non posso connettermi al server'
nl: 'Kon niet alle opgeslagen grafieken ophalen'
de: 'Nicht alle gespeicherten Diagramme konnten abgerufen werden'
fr: 'Impossible de récupérer tous les graphiques sauvegardés'
es: 'No se pudieron cargar todos los gráficos guardados'
tr: 'Tüm kayıtlı grafikler getirilemedi'
```

## TODO
- generic/custom template jinja
- language linting
