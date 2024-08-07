import pandas as pd
from data_export.base_export import BaseExport
from typing import List, Dict


class ParquetExport(BaseExport):

    __version__ = "0.1.1"

    def __init__(self, data: List[Dict], website: str, name: str = None, path: str = None):
        """version = 0.2"""
        super().__init__(data, website, "parquet", name, path)

    def export_data(self) -> None:
        """Функция экспорта данных
        version = 0.1
        """
        data = pd.DataFrame(self.data)
        data.to_parquet(self.file_name)
