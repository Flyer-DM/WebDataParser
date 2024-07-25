import os
from pathlib import Path
from abc import ABC, abstractmethod
from time import gmtime, strftime
from typing import List, Dict


class BaseExport(ABC):

    __version__ = "0.1"

    @abstractmethod
    def set_base_name(self):
        """Получение имени файла по умолчанию, если пользователь не указал его явно, а именно название вебсайта, по
        которому производился парсинг и дата и время сохранения файла
        version = 0.1
        """
        export_time = strftime("%Y-%m-%d %H %M %S", gmtime())
        base_name = f"{self.website} {export_time}"
        return base_name

    @abstractmethod
    def set_base_path(self):
        """Получение пути для сохранения файла по умолчанию, если пользователь не указал его явно, а именно папка
        Загрузки
        version = 0.1
        """
        download_path = str(os.path.join(Path.home(), "Downloads"))
        return download_path

    @abstractmethod
    def set_nullable_values(self):
        """Установка имени файла и пути для его сохранения по умолчанию, если они не введены
        version = 0.1
        """
        self.name = self.set_base_name() if self.name is None else self.name
        self.path = self.set_base_path() if self.path is None else self.path

    def __init__(self, data: List[Dict], website: str, name: str = None, path: str = None):
        """version = 0.1"""
        self.website = website
        self.data = data
        self.name = name
        self.path = path

    @property
    @abstractmethod
    def extension(self):
        """Расширение файла - обязательное свойство класса
        version = 0.1
        """
        ...

    @abstractmethod
    def export_data(self):
        """Функция экспорта данных
        version = 0.1
        """
        ...
