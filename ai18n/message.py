import datetime
from collections import defaultdict
from typing import Any, Dict, Optional, Set

from ai18n.config import conf


class Message:
    def __init__(
        self,
        msgid: str,
        po_translations: Optional[Dict[str, str]] = None,
        ai_translations: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, str]] = None,
        occurances: Optional[Set[str]] = None,
        flags: Optional[Dict[str, Set[str]]] = None,
    ) -> None:
        self.msgid = msgid
        self.occurances: Set[str] = occurances or set()
        self.po_translations: Dict[str, str] = po_translations or {}
        self.ai_translations: Dict[str, str] = ai_translations or {}
        self.metadata = (
            metadata if metadata else {}
        )  # Metadata (e.g., model used, last execution time)
        self.trimmed_msgid = self.normalize_message(msgid)
        self.flags = defaultdict(set, flags or {})

    @classmethod
    def normalize_message(cls, message: str) -> str:
        return message.strip()

    def match_message(self, message: str) -> bool:
        return self.normalize_message(message) == self.trimmed_msgid

    def get_translation(self, lang: str, prefer_ai: bool = False) -> Optional[str]:
        msg = self.po_translations.get(lang)
        if prefer_ai:
            msg = self.ai_translations.get(lang)
        return msg

    def update_message(self, normalized_message: str) -> None:
        self.msgid = normalized_message
        self.trimmed_msgid = self.normalize_message(normalized_message)

    def update_metadata(self, model_used: str, execution_time: datetime.datetime) -> None:
        self.metadata["model_used"] = model_used
        self.metadata["last_executed"] = execution_time.isoformat()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        flags = data.get("flags", {})
        flags = {lang: set(flags[lang]) for lang in flags.keys()}
        return cls(
            msgid=data["msgid"],
            po_translations=data.get("po_translations", {}),
            ai_translations=data.get("ai_translations", {}),
            metadata=data.get("metadata", {}),
            occurances=set(data.get("occurances", [])),
            flags=flags,
        )

    def requires_translation(
        self, lang: str = None, require_ai_translation: bool = False
    ) -> bool:
        if lang:
            ai_translation = self.ai_translations.get(lang)
            po_translation = self.po_translations.get(lang)
            if require_ai_translation:
                return True if not ai_translation else False
            else:
                return True if not ai_translation and not po_translation else False
        # Otherwise, check if any of the required languages are missing
        return any(
            self.requires_translation(lang, require_ai_translation)
            for lang in conf["target_languages"]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trimmed_msgid": self.trimmed_msgid,
            "msgid": self.msgid,
            "occurances": sorted(self.occurances),
            "po_translations": self.po_translations,
            "metadata": self.metadata,
            "ai_translations": self.ai_translations,
            "flags": {
                k: sorted(self.flags[k])
                for k in sorted(self.flags.keys())
                if k and self.flags[k]
            },
        }

    def merge_ai_output(self, ai_translations: Dict[str, str]) -> None:
        for lang, translation in ai_translations.items():
            if translation:
                self.ai_translations[lang] = translation
