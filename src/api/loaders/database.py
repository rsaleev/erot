from audioop import add
from typing import List, Dict, Any, Type

import asyncio

from importlib import import_module

from tortoise.functions import Max

from functools import lru_cache


from src.api.base.objects import Attribute
from src.api.transformers.database import DatabaseTransformer
from src.api.base.objects import Attribute, Object
from src.database.helpers import chainmap_with_unique_keys
from src.database import models
from src.database.models.erot import ErotModel, Base, Sanction
from src.api.mappings.catalogues import CataloguesMapping

class DatabaseLoader:

    def _set_attr_database(self, attribute:Attribute):
        """
        Загрузка модулей для атрибута 'database'


        Args:
            attr_schema (schema.SchemaColumn): схема/описание объекта
        """
        model: ErotModel = getattr(models, attribute.database.orm)
        attribute.database.model = model

    
    def _set_attr_value(self, attribute: Attribute) -> Dict[str, Any]:
        """
        Возвращает словарь со значениями для передачи в экземпляр ORM

        Args:
            object (Object): документ
            model_name (str): наименование модели ORM

        Returns:
            Dict[str, Any]: значения в формате k:v для передачи в инициализацию модели
        """
        # отфильтровать и убрать None(NULL) значения
        if isinstance(attribute.value, list):
            vals = [v for v in attribute.value if v]
            # если массив со значениями, то присвоить его как значение объекта
            if vals:
                attribute.value = vals
            # если после фильтрации массив пуст, то присвоить нулевое значение
            else:
                attribute.value = None
        output = dict()
        for k, v in attribute.database.param.items():
            output.update({k: attribute.__getattribute__(v)})
        DatabaseTransformer.transform(attribute, output)
        return output

    def _get_orm_values(self,
                        attributes: List[Attribute]) -> List[Dict[str, Any]]:
        """
        Выгрузка всех значений атрибутов сгрупированных согласно названию модели ORM 

        Args:
            object (Object): объект
            model (ORMModel): модель ORM

        Returns:
            Dict[str, Any]: словарь со значениями, где ключ это имя атрибута модели
        """
        values_list = [self._set_attr_value(attr) for attr in attributes]
        return chainmap_with_unique_keys(values_list)

    async def _load_parent(self, object: Object) -> Base:
        """

        Загрузка базовой записи в БД

        Модель Base

        Args:
            object (Object): _description_

        Raises:
            ValueError: _description_

        Returns:
            Base: запись в БД 
        """
        attributes = [
            attr for attr in object.attributes if attr.database._model == Base
        ]
        value,  = self._get_orm_values(attributes)
        record, _ = await Base.get_or_create(**value)
        return record

    async def _load_child(self, object: Object, model: ErotModel,
                          parent: Base):
        """
        Загрузка зависимой модели

        Используется дополнительный метод create_or_update(**kwargs)

        Метод расширяет функционал tortoise.models.Model

        """
        attributes = [
            attr for attr in object.attributes if attr.database._model == model
        ]
        value, *additional = self._get_orm_values(attributes)
        value.update({'req_guid_id': parent.req_guid})
        await model.create_or_update(**value)
        if additional:
            for value in additional:
                value, *additional = self._get_orm_values(attributes)
                value.update({'req_guid_id': parent.req_guid})


    async def load(self, object: Object):
        """
        Основной процесс загрузки

        1. В атрибутах объекта меняются значения на соответствующие типы для БД

        Args:
            object (Object): _description_
        """
        await CataloguesMapping.map(object)
        [self._set_attr_database(attr) for attr in object.attributes]
        parent = await self._load_parent(object)
        children = tuple(
            set([
                attr.database._model for attr in object.attributes
                if attr.database._model != Base
                and attr.database._model == Sanction
            ]))
        await asyncio.gather(
            *[self._load_child(object, child, parent) for child in children])
