import pickle
from data_export.base_export import BaseExport
from typing import List, Dict


class PickleExport(BaseExport):

    __version__ = "0.1"

    def __init__(self, data: List[Dict], website: str, name: str = None, path: str = None):
        """version = 0.1"""
        super().__init__(data, website, name, path)
        self._extension = ".pickle"
        self.file_name = f"{self.path}/{self.name}{self.extension}"

    @property
    def extension(self) -> str:
        """Расширение файла - pickle
        version = 0.1
        """
        return self._extension

    def export_data(self) -> None:
        """Функция экспорта данных
        version = 0.1
        """
        with open(self.file_name, 'wb') as f:
            pickle.dump(self.data, f)
