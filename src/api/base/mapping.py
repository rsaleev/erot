import asyncio
from abc import ABC
from typing import Any, Union, Tuple
import os

from aiohttp import ClientSession
from src.api.base.schema import Mapping


class BaseMapper(ABC):

    @classmethod
    async def _get(cls, mapping:Mapping, value:Any) ->Any:
            """
            Получение соответствующего значения из источника
            Args:
                map (schema.Mapping): [description]
                arg (str): [description]

            Returns:
                [type]: [description]
            """

            if value:
                # загрузка URL из переменных окружения
                url = os.environ[f'{mapping.source.upper()}_URL']             
                async with ClientSession(raise_for_status=True) as session:
                    try:
                        async with session.get(
                                url=f"{url}{mapping.link}/{value}") as response:
                                # чтение результата
                                response_data = await response.json()
                                # получение значения dict по ключу
                                return response_data[mapping.output]
                    except:
                        return 
            return 

    @classmethod
    async def fetch(cls, mapping:Mapping, value:Any) ->Union[Tuple[Any, ...], Any]:    
        if isinstance(value, list):
            return await asyncio.gather(*[cls._get(mapping,val) for val in value])
        else:
            return await cls._get(mapping, value)
