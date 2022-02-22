from typing import Union

from aiohttp import ClientSession

import os

import asyncio 

from src.api.base.objects import Attribute, Object
from src.api.base.schema import Mapping


class CataloguesMapping:

    URL = os.environ['CATALOGUES_URL']

    @classmethod
    async def _get_mapped_value(cls, mapping:Mapping, value:str) -> Union[int, None]:
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
                            url=f"{cls.URL}{mapping.link}/{value}") as response:
                            # чтение результата
                            response_data = await response.json()
                            # получение значения dict по ключу
                            response_value = response_data[mapping.output]
                            return response_value
                except:
                    return 

    @classmethod
    async def _set_mapped_value(cls, attr: Attribute):
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
            if not input_data:
                return
            if isinstance(input_data, list):
                result = await asyncio.gather(
                    *[cls._get_mapped_value(m, v) for v in input_data if v])
                attr.__setattr__(m.input, result)
            else:
                result = await cls._get_mapped_value(m, input_data)
                attr.__setattr__(m.input, result)
    
    @classmethod
    async def map(cls, object:Object):
        await asyncio.gather(*[cls._set_mapped_value(attr) for attr in object.attributes])