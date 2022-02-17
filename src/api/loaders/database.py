from importlib import import_module
from typing import ChainMap, List, Type, Dict, Any, Union, Tuple

from itertools import chain
from collections import ChainMap

import asyncio

from src.api.base.objects import Attribute, Object

from src.database.helpers import compare_records, record_to_dict
from src.database.models import erot
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
        output = {attribute.database.attribute: attribute.value}
        # дополнительное значение для создания записи в БД
        if attribute.database.additional_param and attribute.database.additional_attribute:
            output.update({
                attribute.database.additional_attribute:
                attribute.__getattribute__(attribute.database.additional_param)
            })
        return output

    def _set_object_values(self, object: Object,
                          orm: str) -> Dict[str, Any]:
        """
        Выгрузка всех значений атрибутов сгрупированных согласно названию модели ORM 

        Args:
            object (Object): объект
            model (ORMModel): модель ORM

        Returns:
            Dict[str, Any]: словарь со значениями, где ключ это имя атрибута модели
        """
        attrs_filtered = [
            attr for attr in object.attributes if attr.database.orm == orm
        ]
        values_list = [self._set_attr_value(attr) for attr in attrs_filtered]
        output = dict(ChainMap(*values_list))
        return output

    async def _load_parent(self, object:Object):
        """
        Загрузка базовой записи в БД

        Модель Base

        Args:
            object (Object): _description_

        Returns:
            _type_: _description_
        """
        base_record, base_created = await erot.Base.get_or_create(**self._set_object_values(object, 'Base'))
        return base_record, base_created


    async def _load_child(self, object:Object, orm:str, parent:erot.Base):
        child_values = self._set_object_values(object, orm)
        child_model = next(m.database._model for m in object.attributes if m.database.orm==orm)
        child_values.update(parent.get_fk())
        try:
            child_record = await child_model.get_or_none(**child_values)
        except:
            print(child_model)
        else:
            if not child_record:
                await child_model.create(**child_values)
            else:
                old_values = child_record.to_dict() #type: ignore
                if changes:=compare_records(old_values, child_values):
                    await child_model.update_or_create(**child_values)
                    await erot.Updates.bulk_create([
                        erot.Updates(
                            column=ch.column,
                            new=ch.new,
                            old=ch.old
                        ) for ch in changes
                    ])
            

    
    async def load(self, object:Object):
        tasks = []
        parent_record, parent_created = await self._load_parent(object)
        children = tuple(set([attr.database.orm for attr in object.attributes if not attr.database.orm == 'Base']))
        for child in children:
            tasks.append(self._load_child(object, child, parent_record))
        await asyncio.gather(*tasks)





    