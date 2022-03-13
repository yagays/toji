from pathlib import Path

from pydantic import BaseSettings


class TojiSettings(BaseSettings):
    wav_dir_path: Path = Path("data/")
    record_info_path: Path = wav_dir_path / "meta.json"
    unrecorded_texts_path: Path = wav_dir_path / "unrecorded.txt"
    archive_filename: str = "toji_wav_archive.zip"

    class Config:
        env_prefix = "toji_"
        case_sensitive = True
