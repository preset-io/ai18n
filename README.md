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

```
