import datetime
from typing import Any, Dict, List, Optional

from ai18n.config import conf


class Message:
    def __init__(
        self,
        msgid: str,
        po_translations: Optional[Dict[str, str]] = None,
        ai_translations: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, str]] = None,
        occurances: Optional[List[str]] = None,
    ) -> None:
        self.msgid = msgid
        self.occurances = occurances or []
        self.po_translations: Dict[str, str] = po_translations or {}
        self.ai_translations: Dict[str, str] = ai_translations or {}
        self.metadata = (
            metadata if metadata else {}
        )  # Metadata (e.g., model used, last execution time)
        self.trimmed_msgid = self.normalize_message(msgid)

    @classmethod
    def normalize_message(cls, message: str) -> str:
        return message.strip()

    def match_message(self, message: str) -> bool:
        return self.normalize_message(message) == self.trimmed_msgid

    def update_message(self, normalized_message: str) -> None:
        self.msgid = normalized_message
        self.trimmed_msgid = self.normalize_message(normalized_message)

    def update_metadata(self, model_used: str, execution_time: datetime.datetime) -> None:
        self.metadata["model_used"] = model_used
        self.metadata["last_executed"] = execution_time.isoformat()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            msgid=data["msgid"],
            po_translations=data.get("po_translations", {}),
            ai_translations=data.get("ai_translations", {}),
            metadata=data.get("metadata", {}),
            occurances=sorted(set(data.get("occurances", []))),
        )

    def requires_translation(self) -> bool:
        return not self.ai_translations or not (
            all([self.ai_translations.get(lang) for lang in conf["target_languages"]])
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trimmed_msgid": self.trimmed_msgid,
            "msgid": self.msgid,
            "occurances": self.occurances,
            "po_translations": self.po_translations,
            "metadata": self.metadata,
            "ai_translations": self.ai_translations,
        }

    def merge_ai_output(self, ai_translations: Dict[str, str]) -> None:
        for lang, translation in ai_translations.items():
            if translation:
                self.ai_translations[lang] = translation
