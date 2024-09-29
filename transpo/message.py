import datetime
from typing import Any, Dict, List, Optional


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
        self.po_translations: Dict[str, str] = po_translations or {}
        self.ai_translations: Dict[str, str] = ai_translations or {}
        self.metadata = (
            metadata if metadata else {}
        )  # Metadata (e.g., model used, last execution time)
        self.trimmed_msgid = self.normalize_message(msgid)
        self.occurances = occurances or []

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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "msgid": self.msgid,
            "trimmed_msgid": self.trimmed_msgid,
            "po_translations": self.po_translations,
            "ai_translations": self.ai_translations,
            "metadata": self.metadata,
            "occurances": self.occurances,
        }

    def merge_ai_output(self, ai_translations: Dict[str, str]) -> None:
        self.ai_translations.update(ai_translations)
