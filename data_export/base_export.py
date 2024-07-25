import os
from pathlib import Path
from abc import ABC, abstractmethod
from time import gmtime, strftime
from typing import List, Dict


class BaseExport(ABC):

    __version__ = "0.2"

    def __set_base_name(self) -> str:
        """Получение имени файла по умолчанию, если пользователь не указал его явно, а именно название вебсайта, по
        которому производился парсинг и дата и время сохранения файла
        version = 0.1.1
        """
        export_time = strftime("%Y-%m-%d %H %M %S", gmtime())
        base_name = f"{self.website} {export_time}"
        return base_name

    @staticmethod
    def __set_base_path() -> str:
        """Получение пути для сохранения файла по умолчанию, если пользователь не указал его явно, а именно папка
        Загрузки
        version = 0.1.1
        """
        download_path = str(os.path.join(Path.home(), "Downloads"))
        return download_path

    def __set_nullable_values(self) -> None:
        """Установка имени файла и пути для его сохранения по умолчанию, если они не введены
        version = 0.1.1
        """
        self.name = self.__set_base_name() if self.name is None else self.name
        self.path = self.__set_base_path() if self.path is None else self.path

    def __init__(self, data: List[Dict], website: str, name: str = None, path: str = None):
        """version = 0.2"""
        self.website = website
        self.data = data
        self.name = name
        self.path = path
        self.__set_nullable_values()

    @property
    @abstractmethod
    def extension(self) -> str:
        """Расширение файла - обязательное свойство класса
        version = 0.1.1
        """
        ...

    @abstractmethod
    def export_data(self) -> None:
        """Функция экспорта данных
        version = 0.1.1
        """
        ...
