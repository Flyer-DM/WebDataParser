from data_export.base_export import BaseExport
from typing import List, Dict


class TXTExport(BaseExport):

    __version__ = "0.1"

    def set_base_name(self):
        """Получение имени файла по умолчанию, если пользователь не указал его явно, а именно название вебсайта, по
        которому производился парсинг и дата и время сохранения файла
        version = 0.1
        """
        return super().set_base_name()

    def set_base_path(self):
        """Получение пути для сохранения файла по умолчанию, если пользователь не указал его явно, а именно папка
        Загрузки
        version = 0.1
        """
        return super().set_base_path()

    def set_nullable_values(self):
        """Установка имени файла и пути для его сохранения по умолчанию, если они не введены
        version = 0.1
        """
        return super().set_nullable_values()

    def __init__(self, data: List[Dict], website: str, name: str = None, path: str = None):
        """version = 0.1"""
        super().__init__(data, website, name, path)
        self._extension = ".txt"

    @property
    def extension(self):
        """Расширение файла - txt
        version = 0.1
        """
        return self._extension

    def export_data(self):
        """Функция экспорта данных
        version = 0.1
        """
        self.set_nullable_values()
        file_name = f"{self.path}/{self.name}{self.extension}"
        with open(file_name, 'w') as f:
            print(self.data, file=f)
