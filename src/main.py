from src.tasks.etl import Application

import asyncio

app = Application()


asyncio.run(app.extract_transform_load('/home/rost/Development/GIS_OK/erot/tests/Реестр_обязательных_требований_21.xlsx'),debug=True)
