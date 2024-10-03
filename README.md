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

From an operational standpoint, we recommend that you commit the `ai18n.yml` file along
with your po files. It contains the latest state of everything `ai18n`-related, including
what's in your .po files, AI-generated translations from previous runs, and all sorts
of relevant metadata.


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

```bash
# Set your OPENAI_API_KEY so that ai18n can use it
export OPENAI_API_KEY=<your-openai-api-key>

# Populate/sync the latest translations from PO files into the YAML file
ai18n po-pull

# Run this command to use OpenAI for filling in missing translations:
ai18n translate

# Show a report of translations coverage for each locale
ai18n report

# Push translations from the YAML back into PO files while prioritizing AI
# over original translations (default is to prefer original PO translations)
ai18n po-push --prefer-ai

# start clear - flush all existing AI-generated translation out of your yaml file
ai18n flush-ai
```

### Force a po-translation
Depending on your environment, in cases where you have a translation in your PO file as
well as one contributed by AI, you'll have to decide on your precedence rule when pushing
translations back into your PO files. By default, `ai18n po-push` will prefer the PO translation
over the AI one. If you prefer using the AI translations (where available) you can simply
`ai18n po-push --prefer-ai`, which we believe people will want to use as AI translations get
better. Now, if you want to prefer the AI translations, there may be particular strings where
AI simply cannot do a great job, and you may want to set certain strings to force a
PO file string over the AI-contributed one. For this, you simply have to add the `ai18n-force`
flag into your PO file, as such:

```
#, ai18n-force
msgid "Dataset Name"
msgstr "Nom de l’ensemble de données"
```
This PO file comment will be extracted from your PO, and will force this string to be used,
even while running `ai18n po-push --prefer-ai`.

### Common workflow

While PO files are used as an interface in and out of `ai18n`, we recommend that you
1. check/commit the `ai18n.yaml` as a companion file in your code repository. Yes it is large
   and yes, it duplicates some i18n information in your repository, this is how the state
   and precious AI-generated translations get persisted and version-controlled as part of your app
1. keep your PO files intact in your repository, at least while figuring out your i18n workflows,
   this enables contributors to interface and contribute new strings where required
1. add a `ai18n po pull && ai18n translate` to your release workflows, filling in gaps in your
   po files
1. add a `ai18n po-push` somewhere in your release pipeline, so that your software can use
   these "merged" po files to feed your app with translations

Eventually, and as you validate this approach, and as you mature your i18n workflow to take
`ai18n` into account, you can decide to either:

- push the merged AI translated strings back into your app's PO files, and into your repository,
  this would enable humans working with PO files to iterate on the latest/greatest/merged
  translations, either to review translations or alter the bad ones using their favorite
  PO file editor. Translators should be instructed to use the `#, ai18n-force` flag where
  they'd want to override AI-generated translations
- OR, potentially, if you don't need to interface with PO files for data entry, get rid
  of PO files in your repository altogether, and pivot to using the yaml file as the
  source-of-truth for all your translations. To merge new strings into the yaml file, you would, as part
  of your release process, run the PO file extraction, run `ai18n po-pull` to augment it
  with newly discovered/altered strings, and NOT persist PO files in your code repository. In
  this scenario, PO files are simply used as an ephemeral construct to interface between your
  app and the `ai18n` framework during your release process.

## Example/default prompt

To better understand what's happening behind the scene, here's the prompt that we dynamically
build and send to the openai API. Note that you can alter/customize this template to better
fit your need.

```
Translate the following text for the UI of a software application using the GNU gettext framework.
This is in the context of a .po file, so please follow the appropriate formatting for pluralization if needed.

Other language translations are provided as a reference where available, but they may need improvement or correction.
Ensure the translation is appropriate for a technical audience and aligns with common UI/UX terminology.

Instructions:
- Provide the output in JSON format (no markdown) with the language code as a key and the translated string as the value.
- Provide translations for the following locales: ar, de, es, fr, it, ja, ko, nl, pt, pt_BR, ru, sk, sl, tr, uk, zh, zh_TW
- Follow the pluralization rules for the target language if applicable.
- Only pass the key to overwrite if your translation is significantly better than the existing one.

Original string to translate: 'A comma separated list of columns that should be parsed as dates'

Existing translations for reference:
ar: 'قائمة مفصولة بفواصل من الأعمدة التي يجب تحليلها كتواريخ'
de: 'Eine durch Kommas getrennte Liste von Spalten, die als Datumsangaben interpretiert werden sollen'
es: 'Una lista separada por comas de columnas que deben ser parseadas como fechas.'
fr: 'Une liste de colonnes séparées par des virgules qui doivent être analysées comme des dates.'
ja: '日付として解析する必要がある列のカンマ区切りのリスト'
nl: 'Een door komma's gescheiden lijst van kolommen die als datums moeten worden geïnterpreteerd'
pt_BR: 'Uma lista separada por vírgulas de colunas que devem ser analisadas como datas'
ru: 'Разделенный запятыми список столбцов, которые должны быть интерпретированы как даты.'
sl_SI: 'Z vejico ločen seznam stolpcev, v katerih bodo prepoznani datumi'
uk: 'Кома -розділений список стовпців, які слід проаналізувати як дати'
zh: '应作为日期解析的列的逗号分隔列表。'
zh_TW: '應作為日期解析的列的逗號分隔列表。'
```

Example response from openai
```json
{
  "ar": "قائمة مفصولة بفواصل من المخططات التي يسمح للملفات بالتحميل إليها.",
  "de": "Eine durch Kommas getrennte Liste von Schemata, in die Dateien hochgeladen werden dürfen.",
  "es": "Una lista separada por comas de esquemas que permiten la subida de archivos.",
  "fr": "Une liste de schémas séparés par des virgules autorisés pour le téléversement.",
  "it": "Un elenco di schemi separati da virgole a cui è consentito caricare file.",
  "ja": "ファイルのアップロードを許可するスキーマのカンマ区切りのリスト。",
  "ko": "파일 업로드가 허용되는 스키마의 쉼표로 구분된 목록입니다.",
  "nl": "Een komma gescheiden lijst van schema's waar bestanden naar mogen uploaden.",
  "pt": "Uma lista separada por vírgulas de esquemas para os quais é permitido fazer upload de arquivos.",
  "pt_BR": "Uma lista separada por vírgulas de esquemas para os quais os arquivos têm permissão para fazer upload.",
  "ru": "Разделенный запятыми список схем, в которые можно загружать файлы.",
  "sk": "Zoznam schém oddelených čiarkami, do ktorých je povolené nahrávanie súborov.",
  "sl": "Seznam shem, ločenih z vejicami, na katere je dovoljeno nalagati datoteke.",
  "tr": "Dosyaların yüklenebileceği virgülle ayrılmış şema listesi.",
  "uk": "Список схем, відокремлений комами, до яких файли дозволяють завантажувати.",
  "zh": "允许文件上传的逗号分隔的模式列表。",
  "zh_TW": "允許文件上傳的逗號分隔的模式列表。"
}
```

Sample of the `ai18n.yml`
```yaml
messages:
- trimmed_msgid: '!= (Is not equal)'
  msgid: '!= (Is not equal)'
  occurances: []
  po_translations:
    ar: '!= (ﻎﻳﺭ ﻢﺘﺳﺍﻭ)'
    de: '!= (Ist nicht gleich)'
    es: '!= (No es igual)'
    fr: '!= (N''est pas égal)'
    it: ''
    ja: '!= (等しくない)'
    ko: ''
    nl: '!= (Is niet gelijk)'
    pt: ''
    pt_BR: '!= (diferente)'
    ru: '!= (не равно)'
    sk: ''
    sl_SI: '!= (ni enako)'
    tr: ''
    uk: '! = (Не рівний)'
    zh: 不等于（!=）
    zh_TW: 不等於（!=）
    en: '!= (Is not equal)'
  ai_translations:
    ar: '!= (ﻎﻳﺭ ﻢﺘﺳﺍﻭ)'
    de: '!= (Ist nicht gleich)'
    es: '!= (No es igual)'
    fr: '!= (N''est pas égal)'
    it: '!= (Non è uguale)'
    ja: '!= (等しくない)'
    ko: '!= (같지 않음)'
    nl: '!= (Is niet gelijk)'
    pt: '!= (não é igual)'
    pt_BR: '!= (diferente)'
    ru: '!= (не равно)'
    sk: '!= (nie je rovné)'
    sl: '!= (ni enako)'
    tr: '!= (eşit değil)'
    uk: '!= (Не рівний)'
    zh: 不等于（!=）
    zh_TW: 不等於（!=）
  metadata:
    model_used: gpt-4-turbo
    last_executed: '2024-09-30T18:07:14.542663'
```

## Development Setup & Contributing

Clone the repository and install dependencies for both runtime and development:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

Run unit tests
```
pytest tests/
```

## Author

Maxime Beauchemin is the original creator of [Apache Superset](https://superset.apache.org),
[Apache Airflow](https://airflow.apache.org) and the founder and CEO of [Preset](https://preset.io).
