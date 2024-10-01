import os

from Typing import Any, Dict

conf: Dict[str, Any] = {
    "template_folder": "",
    "target_languages": ["es", "fr", "it", "de"],
}

for k in conf.keys():
    v = os.getenv("AI18N_" + k.upper())
    if v:
        if k == "target_languages":
            conf[k] = [lang.strip() for lang in v.split(",")]
        else:
            conf[k] = v
