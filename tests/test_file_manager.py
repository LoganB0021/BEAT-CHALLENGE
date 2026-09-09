import hashlib
from pathlib import Path
import zipfile

import pytest

from beat_challenge_generator.file_manager import create_pack
from beat_challenge_generator.models import Pack, Sound


def test_create_pack_writes_layout_checksum_and_metadata(
    db_session, ingested_assets, sounds_by_category
):
    zip_path = create_pack(sounds_by_category, db_session, pack_date="2026-09-09")

    assert zipfile.is_zipfile(zip_path)
    with zipfile.ZipFile(zip_path) as archive:
        assert sorted(archive.namelist()) == [
            "drum_kits/Kit Alpha/kick.wav",
            "drum_kits/Kit Alpha/nested/hat.wav",
            "fx/delay.wav",
            "samples/bass.wav",
        ]
        assert archive.read("drum_kits/Kit Alpha/kick.wav") == b"kick"

    pack = db_session.query(Pack).one()
    archive_bytes = Path(zip_path).read_bytes()
    digest = hashlib.sha256(archive_bytes).hexdigest()
    assert pack.name == "pack_2026-09-09"
    assert pack.date == "2026-09-09"
    assert len(pack.seed) == 8
    assert pack.seed.isdigit()
    assert pack.size_bytes == len(archive_bytes)
    assert pack.checksum == digest
    assert pack.items == [sound.id for sound in sounds_by_category.values()]
    assert pack.status == "generated"
    assert pack.generated_by == "file_selector:daily"


def test_create_pack_rejects_missing_source_and_cleans_artifacts(
    db_session, sounds_by_category, isolated_paths
):
    missing = sounds_by_category["fx"]
    source = missing.file_path
    import os

    os.remove(source)
    with pytest.raises(FileNotFoundError):
        create_pack(sounds_by_category, db_session, pack_date="2026-09-09")

    assert db_session.query(Pack).count() == 0
    assert list(isolated_paths["packs"].glob("*.zip")) == []
    assert list(isolated_paths["packs"].glob(".pack-*.tmp")) == []


def test_create_pack_rejects_paths_outside_beats(db_session, isolated_paths, tmp_path):
    outside = tmp_path / "outside.wav"
    outside.write_bytes(b"not a beat")
    escaped = Sound(
        id=999,
        name="outside.wav",
        category="fx",
        relative_path="../../outside.wav",
        is_folder=False,
    )

    with pytest.raises(ValueError, match="outside the beats directory"):
        create_pack({"fx": escaped}, db_session, pack_date="2026-09-09")

    assert db_session.query(Pack).count() == 0
    assert list(isolated_paths["packs"].glob("*")) == []
