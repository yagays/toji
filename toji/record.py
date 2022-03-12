import hashlib
import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class Record:
    manuscript_index: int
    text: str
    wav_dir_path: Path

    @property
    def file_id(self):
        return hashlib.md5((self.text + str(self.manuscript_index)).encode()).hexdigest()

    @property
    def output_wav_name(self):
        return f"{self.file_id}.wav"

    @property
    def wav_file_path(self):
        return self.wav_dir_path / self.output_wav_name

    @property
    def record_info(self):
        return {"text": self.text, "file_name": self.output_wav_name}


@dataclass
class RecordStrage:
    all_manuscripts: List[str] = field(default_factory=list)
    id2record: Dict[int, Record] = field(default_factory=dict)

    @property
    def num_wav_files(self):
        return len(self.id2record)

    def export_record_info_as_json(self, record_info_path) -> None:
        with record_info_path.open("w") as f:
            json.dump(
                [record.record_info for _, record in self.id2record.items()],
                f,
                ensure_ascii=False,
                indent=4,
            )

    def compress_wav_files_into_zip(self, archive_filename, wav_dir_path):
        with zipfile.ZipFile(archive_filename, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for file_path in wav_dir_path.rglob("*"):
                archive.write(file_path, arcname=file_path.relative_to(wav_dir_path))
