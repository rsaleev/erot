from typing import Type, Dict, Any

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
        
        if formatting:=attribute.database.format:
            for f in formatting:
                # получениe класса из модуля
                Formatter:Type[BaseTransformer] = getattr(transformers, f.formatter)
                value = Formatter.transform(output[f.attribute])
                if f.output:
                    if not f.attribute in tuple(f.output.keys()):
                        output.pop(f.attribute)
                    for k, v in f.output.items():
                        val = None
                        if value:
                            val = value[v]
                        output.update({k: val})
                else:
                    output[f.attribute]
                

   