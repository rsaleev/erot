from typing import Type

from src.api import transformers
from src.api.base.objects import Attribute, Object
from src.api.base.transformer import BaseTransformer


class ExcelTransformer:

    @classmethod
    def _transform_attribute(cls, attribute: Attribute):
        if formatting := attribute.document.format:
            for f in formatting:
                # получениe класса из модуля
                Formatter: Type[BaseTransformer] = getattr(
                    transformers, f.formatter)
                attribute.value = Formatter.transform(f.options,attribute.__getattribute__('value'))

    @classmethod
    def transform(cls, object: Object):
        [cls._transform_attribute(attr) for attr in object.attributes]
