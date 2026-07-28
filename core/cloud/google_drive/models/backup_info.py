from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BackupInfo:
    file_id: str
    file_name: str
    size_bytes: int
    modified_at: datetime | None
    md5_checksum: str | None = None

    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)