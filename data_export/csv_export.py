import pandas as pd
from data_export.base_export import BaseExport
from typing import List, Dict


class CSVExport(BaseExport):

    __version__ = "0.1.2"

    def __init__(self, data: List[Dict], website: str, name: str = None, path: str = None):
        """version = 0.2"""
        super().__init__(data, website, name, path)
        self._extension = ".csv"
        self.file_name = f"{self.path}/{self.name}{self.extension}"

    @property
    def extension(self) -> str:
        """Расширение файла - csv
        version = 0.1
        """
        return self._extension

    def export_data(self) -> None:
        """Функция экспорта данных
        version = 0.2.1
        """
        data = pd.DataFrame(self.data)
        data.to_csv(self.file_name, index=False, encoding='utf-8')
