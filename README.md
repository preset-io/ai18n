# transpo

transpo is simple utility to translate PO files using the openai API.

It will:
- dig out all .po files from a folder, bring them in-memory
- for each string that need translation, formulate a prompt asking openai with
  the context of existing translations, to provide a new/better translation and fill in
  the gaps. If for instance 6 out 12 translations are present, the prompt ask to translate
  the original english string, but will provide all 6 other language translations for reference
- save everything relevant in a yaml file (po content, newly translated strings, metadata, ...)
- push back new/improved translated strings to the po files

## Example prompt
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
