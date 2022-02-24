from typing import List, Union

import re

from src.api.base.transformer import BaseTransformer



class TextClear(BaseTransformer):
    """
    Очистка текста от символов, согласно описанному формату по правилам RegExp
    """

    @classmethod
    def transform(cls, options:List[str], value:Union[str, None])->Union[str, None]:
        if not value:
            return None
        else:
            return re.sub(options[0], options[1], value)

class TextTrim(BaseTransformer):
    """
     Обрезка лишних символов, согласно описанному формату по правилам RegExp
    """

    @classmethod
    def transform(cls, options:List[str], value:Union[str, None]) -> Union[str, None]:
        if not value:
            return None
        else:
            return re.sub(options[0], options[1] if len(options) >1 else ' ', value)


class TextSplit(BaseTransformer):
    """
    Разбиение текста на массив строк по заданному правилу

    """


    @classmethod
    def transform(cls, options:List[str], value:Union[str, None]):
        if not value:
            return None
        else:
           return re.split(options[0], value)

class TextParse(BaseTransformer):
    """
    Парсинг текста с выводом результатов: группы указанные в регулярном выражении
    """


    @classmethod
    def transform(cls, options:List[str], value:Union[str, None]):
        if value:
            result = re.match(options[0], value)
            if result:
                return result.groupdict()
        return