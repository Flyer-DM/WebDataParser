import os
import json
import pickle
import unittest
import pandas as pd
from pathlib import Path

from data_export import ExportData
from data_export.txt_export import TXTExport
from data_export.csv_export import CSVExport
from data_export.json_export import JSONExport
from data_export.pickle_export import PickleExport
from data_export.parquet_export import ParquetExport
from data_export.xlsx_export import ExcelExport


class TestExport(unittest.TestCase):

    def setUp(self) -> None:
        self.export_type = "txt"
        self.data = [{"key1": "value1", "key2": "value2"}, {"key1": "value3", "key2": "value4"}]
        self.test_website = "website"
        self.test_name = "mydata"
        self.test_path = "path/"
        self.real_path = str(Path.home())
        self.default_download_path = str(os.path.join(Path.home(), "Downloads"))

    def test_exporter(self):
        exporter = ExportData(self.export_type, self.data, self.test_website, self.test_name, self.test_path)
        self.assertIsInstance(exporter.exporter, TXTExport)

    def test_export_txt_default_path(self):
        exporter = ExportData(self.export_type, self.data, self.test_website, self.test_name)
        exporter.export()
        files = os.listdir(self.default_download_path)
        self.assertIn(self.test_name + '.txt', files)

    def test_export_txt_default_name(self):
        exporter = ExportData(self.export_type, self.data, self.test_website, path=self.real_path)
        exporter.export()
        files = os.listdir(self.real_path)
        files = list(filter(lambda f: f.endswith('.txt'), files))
        self.assertNotEqual([], files)

    def test_default_values(self):
        exporter = ExportData(self.export_type, self.data, self.test_website)
        exporter.export()
        files = os.listdir(self.default_download_path)
        files = list(filter(lambda f: f.endswith('.txt'), files))
        self.assertNotEqual([], files)

    def test_export_csv(self):
        exporter = ExportData('csv', self.data, self.test_website)
        exporter.export()
        self.assertIsInstance(exporter.exporter, CSVExport)
        files = os.listdir(self.default_download_path)
        files = list(filter(lambda f: f.endswith('.csv'), files))
        self.assertNotEqual([], files)
        data = pd.read_csv(exporter.exporter.file_name)
        self.assertListEqual(self.data, list(data.T.to_dict().values()))

    def test_export_json(self):
        exporter = ExportData('json', self.data, self.test_website)
        exporter.export()
        self.assertIsInstance(exporter.exporter, JSONExport)
        files = os.listdir(self.default_download_path)
        files = list(filter(lambda f: f.endswith('.json'), files))
        self.assertNotEqual([], files)
        with open(exporter.exporter.file_name, 'r') as file:
            data = json.load(file)
            self.assertListEqual(self.data, data)

    def test_export_pickle(self):
        exporter = ExportData('pickle', self.data, self.test_website)
        exporter.export()
        self.assertIsInstance(exporter.exporter, PickleExport)
        files = os.listdir(self.default_download_path)
        files = list(filter(lambda f: f.endswith('.pickle'), files))
        self.assertNotEqual([], files)
        with open(exporter.exporter.file_name, 'rb') as file:
            data = pickle.load(file)
            self.assertListEqual(self.data, data)

    def test_export_parquet(self):
        exporter = ExportData('parquet', self.data, self.test_website)
        exporter.export()
        self.assertIsInstance(exporter.exporter, ParquetExport)
        files = os.listdir(self.default_download_path)
        files = list(filter(lambda f: f.endswith('.parquet'), files))
        self.assertNotEqual([], files)
        data = pd.read_parquet(exporter.exporter.file_name)
        self.assertListEqual(self.data, list(data.T.to_dict().values()))

    def test_export_excel(self):
        exporter = ExportData('xlsx', self.data, self.test_website)
        exporter.export()
        self.assertIsInstance(exporter.exporter, ExcelExport)
        files = os.listdir(self.default_download_path)
        files = list(filter(lambda f: f.endswith('.xlsx'), files))
        self.assertNotEqual([], files)
        data = pd.read_excel(exporter.exporter.file_name, index_col=0)
        self.assertListEqual(self.data, list(data.T.to_dict().values()))


if __name__ == "__main__":
    unittest.main()
