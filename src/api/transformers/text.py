from typing import List, Union

import re

from src.api.base.transformer import BaseTransformer



class TextClear(BaseTransformer):
    """
    Очистка текста от символов, согласно описанному формату по правилам RegExp
    """

    def __init__(self, options:list):
        self._options = options
        self._regex = re.compile(fr"{options[0]}")


    def transform(self, value:Union[str, None])->Union[str, None]:
        if not value:
            return None
        else:
            return re.sub(self._regex, self._options[1], value)

class TextTrim(BaseTransformer):
    """
     Обрезка лишних символов, согласно описанному формату по правилам RegExp
    """

    def __init__(self, options:list):
        """
        Инициализация с аргументами
        Args:
            options (list): список содержащий правила обработки текста 
                            Пример: ["\\s{2,}", " "], где 0 элемент является компилируемым регулярным выражением,
                                                          1 элемент явялется аргументом для функции re.sub(patter, repl)
        """
        self._options = options
        self._regex = re.compile(fr"{options[0]}")

    def transform(self, value:Union[str, None]) -> Union[str, None]:
        """
        Метод форматирования строки

        Args:
            value (Union[str, None]): входные данные, в случае, если передается null, то возвращается соответствующий тип.
                                      В случае передачи строки происходит форматирование данных согласно правилам

        Returns:
            Union[str, None]:
        """
        if not value:
            return None
        else:
            return re.sub(self._regex, self._options[1] if len(self._options) >1 else ' ', value)


class TextSplit(BaseTransformer):

    def __init__(self, options:list):
        self._options = options
        self._regex = re.compile(fr"{options[0]}")

    def transform(self, value:Union[str, None])->Union[None, List[str]]:
        if not value:
            return None
        else:
           return re.split(self._regex, value)