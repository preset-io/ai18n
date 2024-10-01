import os
from typing import Any, Dict

conf: Dict[str, Any] = {
    "template_folder": "",
    "po_folder_root": "",
    "prompt_extra_context": "",
    "yaml_file": "",
    "main_language": "en",
    "target_languages": ["es", "fr", "it", "de"],
}

# Populating the configuration with environment variables prefixed with "AI18N_"
for k in conf.keys():
    v = os.getenv("AI18N_" + k.upper())
    if v:
        if k == "target_languages":
            conf[k] = [lang.strip() for lang in v.split(",")]
        else:
            conf[k] = v
