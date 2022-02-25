import asyncio

import uvloop

import celery 

import asyncio

import logging

import time

from tortoise import Tortoise

from src.config import database

from src.api.extractors.excel import ExcelExtractor 
from src.api.loaders.database import DatabaseLoader
from src.api.transformers.excel import ExcelTransformer



from .celery import app

logger = logging.getLogger(__name__)

class Application:

    def __init__(self, filename:str, extractor = ExcelExtractor, loader = DatabaseLoader):
        self.extractor = extractor()
        self.loader = loader()
        self.filename = filename

    async def process(self, filename:str):
        """
        Основная логика чтения документа, валидации, выгрузки значений, трансформации и загрузки в БД

        Args:
            filename (str): [description]

        Raises:
            e: [description]
        """
        if not self.extractor:
            raise AttributeError
        
        # подключиться к базе данных
        await Tortoise.init(config=database.CONFIG)
        await Tortoise.generate_schemas()
        await self.extractor.extract(filename, self.loader.load)
        # закрыть соединение с БД
        await Tortoise.close_connections()

    def run(self):
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.process(self.filename))
        loop.close()
        return


@app.task(bind=True)
def etl(filename, extractor=ExcelExtractor, loader=DatabaseLoader):
    app = Application(filename, extractor=extractor, loader=loader)
    return app.run()
