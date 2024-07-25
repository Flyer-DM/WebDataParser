import os
import unittest
from pathlib import Path
from data_export import ExportData
from data_export.txt_export import TXTExport


class TestExport(unittest.TestCase):

    def setUp(self) -> None:
        self.export_type = "txt"
        self.data = [{"key1": "value1", "key2": "value2"}, {"key1": "value3", "key2": "value4"}]
        self.test_website = "website"
        self.test_name = "mydata"
        self.test_path = "path/"
        self.real_path = r"C:\Users\kondr\OneDrive\Рабочий стол"
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


if __name__ == "__main__":
    unittest.main()
