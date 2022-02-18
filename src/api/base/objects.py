import os
from copy import deepcopy
from importlib import import_module
from typing import Any, Iterable, List, Optional, Type, Union
import asyncio
from pydantic import BaseModel
from aiohttp.client import ClientSession
from tortoise.models import Model as ORMModel
from .schema import Mapping, SchemaColumn, Document, Database
from .orm import ModelDescription
from .transformer import BaseTransformer


class Attribute(BaseModel):
    name: str
    value: Optional[Any]
    document: Document
    database: Database
    mapping: Optional[List[Mapping]]

    def setup(self, attr_schema: SchemaColumn):
        self._set_document(attr_schema)
        self._set_database()

    def _set_document(self, attr_schema: SchemaColumn):
        """
        Загрузка модулей для атрибута 'document'

        Args:
            attr_schema (schema.SchemaColumn): схема/описание объекта
        Raises:
            e: [description]
        """
        self.document = attr_schema.document
        if self.document.format:
            for f in self.document.format:
                try:
                    # динамическая загрузка модуля
                    module = import_module("src.api.transformers")
                    # получениe класса из модуля
                    object = getattr(module, f.formatter)
                except Exception as e:
                    raise e
                    # создание экземпляра класса с передачей параметров
                else:
                    f._instance = object(f.options)
        else:
            self.document.format = []

    def _set_database(self):
        """
        Загрузка модулей для атрибута 'database'


        Args:
            attr_schema (schema.SchemaColumn): схема/описание объекта
        """
        module = import_module(f"src.database.models.erot")
        model: ORMModel = getattr(module, self.database.orm)
        self.database._model = model

    def _get_orm_description(self) -> ModelDescription:
        
        description = ModelDescription(**self.database._model.describe())  
        return description
class Object:

    def __init__(self, name: str):
        self.attributes: List[Attribute] = []
        self.name = name

    def get_copy(self):
        return deepcopy(self)

    def add_field(self, schema_column: SchemaColumn):
        """
        Создание объекта через встроенную функцию type и добавление в массив атрибутов

        Args:
            attr_schema (schema.DocumentSchemaColumn): структура объекта 
        """
        if schema_column.database:
            attribute = Attribute(**schema_column.dict())
            attribute.setup(schema_column)
            self.attributes.append(attribute)

    def del_field(self):
        raise NotImplementedError

    def upd_field(self, schema_column):
        raise NotImplementedError

    def _set_transformed_value(self, attr: Attribute):
        if attr.document and attr.document.format:
            for rule in attr.document.format:
                if isinstance(rule._instance, BaseTransformer):
                    attr.value = rule._instance.transform(attr.value)

    async def _get_mapped_value(self, map: Mapping, arg: str) -> Union[int, None]:
        """
        Получение соответствующего значения из источника
        Args:
            map (schema.Mapping): [description]
            arg (str): [description]

        Returns:
            [type]: [description]
        """
        async with ClientSession(raise_for_status=True) as session:
            try:
                async with session.get(
                        url=f"{os.environ['CATALOGUES_URL']}{map.link}/{arg}") as response:
                        # чтение результата
                        response_data = await response.json()
                        # получение значения dict по ключу
                        response_value = response_data[map.output]
                        return response_value
            except:
                return 

    async def _set_mapped_value(self, attr: Attribute):
        """
        Изменение значения в соответствие с полученным результатом при запросе в сервис


        Args:
            map (schema.Mapping): атрибут описывающий тип соответствия
            attr (Attribute): текущий атрибут
        """
        # получить значение атрибута в соответствие со схемой
        if not attr.mapping:
            return
        for m in attr.mapping:
            try:
                input_data = attr.__getattribute__(m.input)
            except AttributeError:
                return
            else:
                if not input_data:
                    return
                if isinstance(input_data, list):
                    result = await asyncio.gather(
                        *[self._get_mapped_value(m, v) for v in input_data])
                    attr.__setattr__(m.input, result)
                else:
                    result = await self._get_mapped_value(m, input_data)
                    attr.__setattr__(m.input, result)

    async def transform(self):
        [self._set_transformed_value(attr) for attr in self.attributes]

    async def map(self):
        await asyncio.gather(*[self._set_mapped_value(attr) for attr in self.attributes])
