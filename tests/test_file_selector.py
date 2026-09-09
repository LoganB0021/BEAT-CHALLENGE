from beat_challenge_generator.file_selector import get_random_item_from_folder


def test_random_item_selection(isolated_paths):
    category = isolated_paths["beats"] / "drum_kits"
    (category / "kit").mkdir()
    (category / "kit" / "kick.wav").write_bytes(b"kick")
    (category / "one-shot.wav").write_bytes(b"one-shot")

    selected_item = get_random_item_from_folder(str(category))

    assert selected_item in {"kit", "one-shot.wav"}


def test_random_item_selection_returns_none_for_empty_folder(isolated_paths):
    category = isolated_paths["beats"] / "fx"
    assert get_random_item_from_folder(str(category)) is None