from data_export.base_export import BaseExport
from data_export.txt_export import TXTExport
from data_export.csv_export import CSVExport
from data_export.json_export import JSONExport
from data_export.pickle_export import PickleExport
from data_export.parquet_export import ParquetExport
from data_export.xlsx_export import ExcelExport
from typing import List, Dict


class ExportData:

    __version__ = "0.6"
    exporters = {
        "txt": TXTExport,
        "csv": CSVExport,
        "json": JSONExport,
        "pickle": PickleExport,
        "parquet": ParquetExport,
        "xlsx": ExcelExport
    }

    @classmethod
    def set_exporter(cls, export_type: str, data: List[Dict], website: str, name: str = None, path: str = None) -> BaseExport:
        """Выбор расширения для экспорта файла из введённого текстового значения
        version = 0.1
        """
        return cls.exporters[export_type](data, website, name, path)

    def __init__(self, export_type: str, data: List[Dict], website: str, name: str = None, path: str = None):
        """version = 0.1"""
        self.exporter: BaseExport = ExportData.set_exporter(export_type, data, website, name, path)

    def export(self) -> None:
        """Функция экспорта данных
        version = 0.1
        """
        self.exporter.export_data()
