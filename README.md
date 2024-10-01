# ai18n - AI-Powered PO Translation Toolkit

<img src="https://raw.githubusercontent.com/preset-io/ai18n/main/logo.webp" width="200" alt="ai18n"/>

**ai18n** is a toolkit that enables you to tackle translations based on the [GNU gettext
framework](https://www.gnu.org/software/gettext/) while working with and
augmenting your `.po` files. It integrates with the
OpenAI API to automate translations either manually or as part of your CI/CD pipeline.

## Key Features

- **AI-Powered Translations**: Automatically generate missing translations using OpenAI
  models like `gpt-4`.
- **PO/YAML Syncing**: Manage translations centrally in a YAML file while keeping
  traditional `.po` files in sync.
- **Custom Reports**: Generate reports showing translation coverage across languages
  and files.
- **CLI Interface**: Easy-to-use command-line interface for translating, syncing, and
  reporting on translations.
- **Non-Destructive Workflow**: Original translations remain intact, with AI suggestions
  added on top, and you control the merging back into `.po` files.

## How It Works

Through a simple CLI, `ai18n` can load your existing `.po` files into memory, call the
OpenAI API to generate translations where missing or incorrect, and save the progress
into a central YAML file. You can then choose to merge these AI-generated translations
back into your `.po` files as needed.

The framework is **non-destructive**—your original translations are preserved, and
AI-generated translations are added incrementally. You have full control over merging
them into your `.po` files based on your needs.


## Usage

### Configuration

While you can pass some of these as parameters to the commands, we suggest you prepare your
environment by setting these environment variables:

```bash
# Set your target locales
export AI18N_TARGET_LANGUAGES=ar,de,es,fr,it,ja,ko,nl,pt,pt_BR,ru,sk,sl,tr,uk,zh,zh_TW

# Tell ai18n where your PO files are located
export AI18N_PO_FOLDER_ROOT="./translations/"

# This will be embedded into our prompt for extra context about your application / use cases
export AI18N_PROMPT_EXTRA_CONTEXT="These translation are part of Apache Superset, a Business Intelligence data exploration, visualization and dashboard open source application"

# If you want alter / customize the jinja template used to prompt AI
export AI18N_TEMPLATE_FOLDER="./templates/"

# Where your big yaml file with all your translations live
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
    ai18n report
    ```

3. **PO/YAML Management**:
    - **Pull**: Load translations from PO files into the YAML memory.

      ```bash
      ai18n po-pull
      ```

    - **Push**: Push translations from the YAML back into PO files.

      ```bash
      ai18n po-push
      ```

4. **Flush AI Translations**:
    Clear all AI-generated translations from the YAML file:

    ```bash
    ai18n flush-ai
    ```

## Development Setup & Contributing

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
