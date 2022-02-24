from curses.ascii import isascii
from typing import Type, Dict, Any

from attr import attr

from src.api import transformers
from src.api.base.objects import Attribute, Object
from src.api.base.transformer import BaseTransformer


class DatabaseTransformer:

    @classmethod
    def transform(cls, attribute:Attribute, output:Dict[str, Any]):
        """

        Форматирование аргументов для записи в БД

        Args:
            attribute (Attribute): объект типа Attribute
            output (Dict[str, Any]): контейнер текущих значений

        Returns:
            _type_: _description_
        """
        
   