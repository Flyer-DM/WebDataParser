import pickle
from data_export.base_export import BaseExport
from typing import List, Dict


class PickleExport(BaseExport):

    __version__ = "0.1.1"

    def __init__(self, data: List[Dict], website: str, name: str = None, path: str = None):
        """version = 0.2"""
        super().__init__(data, website, "pickle", name, path)

    def export_data(self) -> None:
        """Функция экспорта данных
        version = 0.1
        """
        with open(self.file_name, 'wb') as f:
            pickle.dump(self.data, f)
