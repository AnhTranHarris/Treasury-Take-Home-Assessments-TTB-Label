from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.sample_labels import (
    NO_SAMPLE,
    SAMPLE_LABELS,
    SAMPLE_LABEL_DIR,
    select_label_image,
)


@dataclass
class FakeUpload:
    name: str
    data: bytes

    def getvalue(self) -> bytes:
        return self.data


def test_all_seven_repository_samples_are_present_and_valid_jpegs():
    assert len(SAMPLE_LABELS) == 7
    for name, filename in SAMPLE_LABELS.items():
        path = SAMPLE_LABEL_DIR / filename
        assert path.is_file(), name
        contents = path.read_bytes()
        assert contents[:2] == b"\\xff\\xd8".decode("unicode_escape").encode("latin1")
        assert len(contents) > 100_000, name


def test_no_image_is_selected_by_default():
    assert select_label_image(NO_SAMPLE, None) is None


def test_repository_sample_can_be_selected_without_local_download():
    name = next(iter(SAMPLE_LABELS))
    result = select_label_image(name, None)
    assert result is not None
    assert result.source == "sample"
    assert result.name == name
    assert result.image_bytes[:2] == bytes([0xFF, 0xD8])
    assert result.getvalue() == result.image_bytes


def test_upload_takes_priority_over_selected_sample():
    name = next(iter(SAMPLE_LABELS))
    uploaded = FakeUpload(name="reviewer_label.png", data=b"original-upload")
    result = select_label_image(name, uploaded)
    assert result is not None
    assert result.source == "upload"
    assert result.name == "reviewer_label.png"
    assert result.getvalue() == b"original-upload"


def test_unknown_sample_is_rejected():
    with pytest.raises(ValueError, match="Unknown built-in sample"):
        select_label_image("../../secrets.txt", None)
