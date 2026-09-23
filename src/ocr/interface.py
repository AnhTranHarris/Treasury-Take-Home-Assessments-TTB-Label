from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class OCRLine:
    text: str
    score: float
    box: tuple[int, int, int, int] | None = None


class OCRProvider(Protocol):
    def recognize(self, image_bytes: bytes) -> Sequence[OCRLine]:
        """Return recognized text lines in reading order."""
        ...
