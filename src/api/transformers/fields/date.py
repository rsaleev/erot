from typing import Union, List

import re

from dateutil import parser as dtparser

from datetime import date

from src.api.exceptions import DateFormatError
from src.api.base.transformer import BaseTransformer



class DateInput(BaseTransformer):

    @classmethod
    def transform(cls, options:List[str], value: Union[str, None]) -> Union[None, date]:
        """
        Args:
            v (str): строка в формате записи даты или иной формат
        Returns:
            Union[None, date]: None - если формат н31.12.2025е отвечает требованиям, в ином случае объект date
        Raises:
            DateFormatError: формат записи не соответствует установленному правилу
        """
        if value:
            match = re.match(options[0], value)
            if not match:
                return
            if match.groupdict()['date_fmt']:
                return dtparser.parse(value).date()
            else:
                return None
        else:
            return 
class DatetimeInput(BaseTransformer):


    @classmethod
    def transform(cls, options:List[str], value: Union[str, None]) -> Union[None, date]:
        """
        Args:
            v (str): строка в формате записи даты и времени или иной формат
        Returns:
            Union[None, date]: None - если формат не отвечает требованиям, в ином случае объект date
        """
        if value:
            match = re.match(options[0], value)
            if not match:
                return
            if match.groupdict()['date_fmt']:
                return dtparser.parse(value).date()
            else:
                return
        else:
            return