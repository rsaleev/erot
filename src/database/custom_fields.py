import json
from typing import Optional, List, Union, Type, Any

from tortoise.models import Model
from tortoise.fields import Field

from pypika.terms import Term
from pypika.terms import Array
from pypika import functions
from pypika.enums import SqlTypes
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

    def function_cast(self, term:Term):
        return functions.Cast(term, Array)


    # перевод в формат БД
    def to_db_value(
        self, value: Union[List[Union[str, None]], None], instance: "Union[Type[Model], Model]"
    ):
        if value:
            return [str(x) for x in value if not x is None]
        return value

    # перевод в формат Python3
    def to_python_value(self, value: Any) -> Union[List[str], Any]:
        return value


class NumericArrayField(Field, list):
    """NumericArrayField

    Тип поля: массив значений типа целое число. Соответствует типу PG numeric[]
    """
    # объявление типа SQL
    SQL_TYPE = 'INT[]'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_db_value(
        self, value: List[int], instance: "Union[Type[Model], Model]"
    ) -> Optional[List[int]]:
        return value

    def to_python_value(self, value: Any) -> Optional[List[int]]:
        if value:
            array = json.loads(value.replace("'", '"'))
            return [int(x) for x in array]
        return value

