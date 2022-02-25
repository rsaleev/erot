from typing import List, Dict, Any

import asyncio

from importlib import import_module
from attr import attr

from tortoise.functions import Max
from src.api.base.mapping import BaseMapper


from src.api.base.objects import Attribute
from src.api.base.objects import Attribute, Object
from src.database.helpers import chainmap_with_unique_keys
from src.database import models
from src.database.models.erot import ErotModel, Base

class DatabaseLoader:

    def _set_attr_database(self, orm:str):
        """
        Загрузка модулей для атрибута 'database'


        Args:
            attr_schema (schema.SchemaColumn): схема/описание объекта
        """
        
        model: ErotModel = getattr(models, orm)
        return model
    
    async def _get_mapped_value(self, attribute:Attribute, output:dict, key:str, value:Any):
        if attribute.mapping:
            if rule:=next((m for m in attribute.mapping if m.input == value),None):
                result = await BaseMapper.fetch(rule, attribute.__getattribute__(rule.input))
                output.update({key:result})
            else:
                output.update({key:attribute.__getattribute__(value)})
        else:
            output.update({key: attribute.__getattribute__(value)})

    async def _set_attr_value(self, attribute: Attribute):
        """
        Возвращает словарь со значениями для передачи в экземпляр ORM

        Args:
            object (Object): документ
            model_name (str): наименование модели ORM

        Returns:
            Dict[str, Any]: значения в формате k:v для передачи в инициализацию модели
        """
        output = dict()
        if not attribute.database or not attribute.database.params:
            raise AttributeError
        await asyncio.gather(*[self._get_mapped_value(attribute, output, key, value) for key, value in attribute.database.params.items()])            
        return output

    async def _get_orm_values(self,
                        attributes: List[Attribute]) -> List[Dict[str, Any]]:
        """
        Выгрузка всех значений атрибутов сгрупированных согласно названию модели ORM 

        Args:
            object (Object): объект
            model (ORMModel): модель ORM

        Returns:
            Dict[str, Any]: словарь со значениями, где ключ это имя атрибута модели
        """
        values_list = await asyncio.gather(*[self._set_attr_value(attr) for attr in attributes])
        orm_values = chainmap_with_unique_keys(values_list)
        return orm_values


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
            attr for attr in object.attributes if attr.database.__getattribute__('orm') == 'Base'
        ]
        values, *additional = await self._get_orm_values(attributes)
        record = await Base.get_or_none(req_guid=values['req_guid'])
        if not record:
            record = await Base.create(**values)
        return record
        
    async def _load_child(self, object: Object, model_name: str,
                          parent: Base):
        """
        Загрузка зависимой модели

        Используется дополнительный метод create_or_update(**kwargs)

        Метод расширяет функционал tortoise.models.Model

        """
        attributes = [
            attr for attr in object.attributes if attr.database.__getattribute__('orm') == model_name
        ]
        model = next(m for m in models.erot.__models__ if m.__name__ == model_name)
        values, *additional = await self._get_orm_values(attributes)
        await model.create_or_update(**values, parent=parent)
        for v_add in additional:
            await model.create_or_update(**v_add,parent=parent)




    async def load(self, object: Object):
        """
        Основной процесс загрузки

        1. В атрибутах объекта меняются значения на соответствующие типы для БД

        Args:
            object (Object): _description_
        """
        object.attributes = [attr for attr in object.attributes if attr.database]
        parent = await self._load_parent(object)
        children = tuple(
            set([
                attr.database.__getattribute__('orm') for attr in object.attributes
                if attr.database.__getattribute__('orm') != 'Base'
            ]))
        await asyncio.gather(
            *[self._load_child(object, child, parent) for child in children])
