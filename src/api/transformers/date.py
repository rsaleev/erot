from lib2to3.pytree import Base
from typing import Union

import os

import re

from dateutil import parser as dtparser

from datetime import date

from src.api.exceptions import DateFormatError
from src.api.base.transformer import BaseTransformer



class DateInput(BaseTransformer):

    def __init__(self, options: list):
        self.options = options
        self._regex = re.compile(fr'{self.options[0]}')

    def transform(self, v: Union[str, None]) -> Union[None, date]:
        """
        Args:
            v (str): строка в формате записи даты или иной формат
        Returns:
            Union[None, date]: None - если формат н31.12.2025е отвечает требованиям, в ином случае объект date
        Raises:
            DateFormatError: формат записи не соответствует установленному правилу
        """
        if v:
            match = self._regex.match(v)
            if not match:
                raise DateFormatError("Формат записи не отвечает требования схемы")
            if match.groupdict()['date_fmt']:
                return dtparser.parse(v).date()
            else:
                return None
        else:
            return None

class DatetimeInput(BaseTransformer):

    def __init__(self, options: list):
        self.options = options
        self._regex = re.compile(fr'{self.options[0]}')

    def transform(self, v: str) -> Union[None, date]:
        """
        Args:
            v (str): строка в формате записи даты и времени или иной формат
        Returns:
            Union[None, date]: None - если формат не отвечает требованиям, в ином случае объект date
        """
        match = self._regex.match(v)
        if not match:
            raise DateFormatError("Формат записи не отвечает требования схемы")
        if match.groupdict()['date_fmt']:
            return dtparser.parse(v).date()
        else:
            return None