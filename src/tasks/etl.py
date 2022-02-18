import asyncio

import uvloop

import celery 

import logging

from tortoise import Tortoise

from src.config import database


from src.api.extractors.excel import ExcelExtractor 
from src.api.loaders.database import DatabaseLoader


from .celery import app

logger = logging.getLogger(__name__)

class Application(celery.Task):

    def __init__(self):
        self.extractor = ExcelExtractor()
        self.loader = DatabaseLoader()

    async def extract_transform_load(self, filename:str):
        """
        Основная логика чтения документа, валидации, выгрузки значений, трансформации и загрузки в БД

        Args:
            filename (str): [description]

        Raises:
            e: [description]
        """
        self.extractor.read(filename)
        try:
            await self.extractor.validate()
        except Exception as e:
            raise e 
        else:
            # подключиться к базе данных
            await Tortoise.init(config=database.CONFIG)
            await Tortoise.generate_schemas()
            try:
                obj = self.extractor.extract()
            except StopIteration:
                raise StopIteration
            else:
                await obj.transform()
                await self.loader.load(obj)
        # закрыть соединение с БД
        await Tortoise.close_connections()

    def run(self, filename:str):
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.extract_transform_load(filename))
        except Exception as e:
            return str(e)
        else:
            return 


@app.task(bind=True, base=Application)
def etl(filename):
    return etl.run(filename)

