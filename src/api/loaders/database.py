from typing import List, Dict, Any

import asyncio

from src.api.base.objects import Attribute, Object

from src.database.helpers import compare_records, chainmap_with_unique_keys, model_to_dict
from src.database.models.erot import Base, Updates

from tortoise.models import Model
from pypika.terms import Array


class DatabaseLoader:

    def _set_attr_value(self, attribute: Attribute) -> Dict[str, Any]:
        """
        Возвращает словарь со значениями для передачи в экземпляр ORM

        Args:
            object (Object): документ
            model_name (str): наименование модели ORM

        Returns:
            Dict[str, Any]: значения в формате k:v для передачи в инициализацию модели
        """
        # отфилбтровать и убрать None(NULL) значения
        if isinstance(attribute.value,list):
            vals = [v for v in attribute.value if v]
            # если массив со значениями, то присвоить его как значение объекта
            if vals:
                attribute.value = vals
            # если после фильтрации массив пуст, то присвоить нулевое значение
            else:
                attribute.value = None
        output = {attribute.database.attribute: attribute.value}
        # дополнительное значение для создания записи в БД
        if attribute.database.additional_param and attribute.database.additional_attribute:
            additional_attribute = attribute.database.additional_attribute
            additional_value = attribute.__getattribute__(
                attribute.database.additional_param)
            if isinstance(additional_value,list):
                vals = [v for v in additional_value if v]
                # если массив со значениями, то присвоить его как значение объекта
                if vals:
                    additional_value = vals
                # если после фильтрации массив пуст, то присвоить нулевое значение
                else:
                    additional_value = None
            output.update(
            {additional_attribute: additional_value})
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
        _load_parent

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
        values = self._get_orm_values(attributes)
        if len(values) > 1:
            raise ValueError('Количество значений превышает 1')
        record, _ = await Base.get_or_create(**values[0])
        return record

    async def _load_child(self, object: Object, model: Model, parent: Base):
        attributes = [
            attr for attr in object.attributes if attr.database._model == model
        ]
        values = self._get_orm_values(attributes)
        for val in values:
            val.update({'req_guid_id': parent.req_guid})
            record = await model.get_or_none(**val)
            if record:
                record_values = model_to_dict(record)
                diffs = compare_records(record_values, val)
                if diffs:
                    if isinstance(record, list):
                        for rec in record:
                            await rec.update_from_dict(val).save()
                    else:
                        await record.update_from_dict(val).save()
                    await Updates.bulk_create([
                        Updates(**diff, req_uid=parent.req_guid)
                        for diff in diffs
                    ])
            else:
                await model.create(**val)
            

    async def load(self, object: Object):
        await object.map()
        parent = await self._load_parent(object)
        children = tuple(
            set([
                attr.database._model for attr in object.attributes
                if attr.database._model != Base
            ]))
        await asyncio.gather(
            *[self._load_child(object, child, parent) for child in children])
