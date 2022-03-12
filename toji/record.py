import hashlib
from dataclasses import dataclass
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
class AudioStrage:
    id2audios: Dict[str, List[Record]]
