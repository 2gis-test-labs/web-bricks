from dataclasses import dataclass
from datetime import datetime
from typing import Any


class LogRecord:
    def str(self):
        raise NotImplementedError

    def __str__(self):
        return self.str()

    def __repr__(self):
        return f'LogRecord("{self.str()}")'


@dataclass
class ResolutionLog(LogRecord):
    obj: Any
    component: Any

    def str(self):
        return f'{"найден" if self.component else "не найден"} {self.obj}'


@dataclass
class ResolutionErrorLog(LogRecord):
    obj: Any
    locator: Any
    error: Any

    def str(self):
        return f'Элемент не найден: {self.locator} в {self.obj}: {self.error}'


def stdout_logger(record):
    time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f'{time}: {str(record)}')
