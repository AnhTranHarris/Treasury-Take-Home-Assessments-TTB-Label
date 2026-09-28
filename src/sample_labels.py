"""Local, repository-hosted demo labels for frictionless reviewer testing.

These images are AI-generated test fixtures, not regulatory reference material and
not training data for a custom machine-learning model.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol


SAMPLE_LABEL_DIR = Path(__file__).resolve().parent.parent / "assets" / "sample_labels"
NO_SAMPLE = "Select a sample label"

SAMPLE_LABELS: dict[str, str] = {
    "Kuroyama Reserve — Japanese whisky": "01_kuroyama_reserve.jpg",
    "Ember Coast — citrus gin": "02_ember_coast.jpg",
    "Copper Fox — bourbon": "03_copper_fox.jpg",
    "Iron Harbor — rye whiskey": "04_iron_harbor.jpg",
    "Blackhaven Reserve — London dry gin": "05_blackhaven.jpg",
    "Liberty Creek — damaged label stress test": "06_liberty_creek.jpg",
    "Raven Creek — damaged label stress test": "07_raven_creek.jpg",
}


class UploadedImage(Protocol):
    name: str

    def getvalue(self) -> bytes:
        ...


@dataclass(frozen=True)
class SelectedLabelImage:
    name: str
    source: Literal["sample", "upload"]
    image_bytes: bytes

    def getvalue(self) -> bytes:
        """Preserve the file-uploader interface used by both existing workflows."""
        return self.image_bytes


def select_label_image(
    sample_name: str,
    uploaded: UploadedImage | None,
) -> SelectedLabelImage | None:
    """Explicit user upload takes precedence over a simultaneously chosen sample."""
    if uploaded is not None:
        return SelectedLabelImage(
            name=uploaded.name,
            source="upload",
            image_bytes=uploaded.getvalue(),
        )

    if sample_name == NO_SAMPLE:
        return None

    filename = SAMPLE_LABELS.get(sample_name)
    if filename is None:
        raise ValueError("Unknown built-in sample label.")

    return SelectedLabelImage(
        name=sample_name,
        source="sample",
        image_bytes=(SAMPLE_LABEL_DIR / filename).read_bytes(),
    )
