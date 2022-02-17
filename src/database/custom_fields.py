import json
from typing import Optional, List, Union, Type, Any

from tortoise.models import Model
from tortoise.fields import Field
##############################################
# массивы PG array для описания полей Tortoise
##############################################

class TextArrayField(Field, list):
    """TextArrayField
       Тип поля: массив значений типа строка. Соответствует типу PG text[]
    """
    # объявление типа SQL
    SQL_TYPE = 'TEXT[]'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # перевод в формат БД
    def to_db_value(
        self, value: Union[List[Union[str, None]], None], instance: "Union[Type[Model], Model]"
    ):
        if value:
            return [str(x) for x in value if not x is None]
        else:
            return None

    # перевод в формат Python3
    def to_python_value(self, value: Any) -> Union[List[str], Any]:
        table = value.maketrans({'{': '', '}': '', '"': ''})
        output = [elem for elem in value.translate(table).split(',')]
        return output


class NumericArrayField(Field, list):
    """NumericArrayField

    Тип поля: массив значений типа целое число. Соответствует типу PG numeric[]
    """
    # объявление типа SQL
    SQL_TYPE = 'NUMERIC[]'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # перевод в формат БД
    def to_db_value(self, value: List[Union[float, None]],
                    instance: "Union[Type[Model], Model]") -> Optional[List[Union[float, None]]]:
        return [x for x in value if not x is None]

    # перевод в формат Python3
    def to_python_value(self, value: Any) -> Union[List[float], list]:
        table = value.maketrans({'{': '', '}': '', '"': ''})
        output = []
        try:
            output = [float(elem)
                      for elem in value.translate(table).split(',')]
        except (ValueError, AttributeError):
            pass
        return output
