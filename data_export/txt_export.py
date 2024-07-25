from data_export.base_export import BaseExport
from typing import List, Dict


class TXTExport(BaseExport):

    __version__ = "0.2"

    def __init__(self, data: List[Dict], website: str, name: str = None, path: str = None):
        """version = 0.1"""
        super().__init__(data, website, name, path)
        self._extension = ".txt"
        self.file_name = f"{self.path}/{self.name}{self.extension}"

    @property
    def extension(self) -> str:
        """Расширение файла - txt
        version = 0.1.1
        """
        return self._extension

    def export_data(self) -> None:
        """Функция экспорта данных
        version = 0.1.1
        """
        with open(self.file_name, 'w') as f:
            print(self.data, file=f)
