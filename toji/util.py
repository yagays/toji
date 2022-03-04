from typing import Optional


class Counter:
    def __init__(self) -> None:
        self.index: int = 0
        self.total: Optional[int] = None

    def set_total(self, n):
        self.total = n

    def next(self):
        if self.total and self.index != self.total - 1:
            self.index += 1

    def previous(self):
        if self.index != 0:
            self.index -= 1

    @property
    def progress_percent(self) -> float:
        # include current item
        if self.total:
            return (self.index + 1) / self.total
        else:
            return 0.0
