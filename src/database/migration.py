from aerich import Command

from src.config.database import CONFIG

import asyncio

import sys

async def run_migration_task(title:str):
    command = Command(tortoise_config=CONFIG)
    await command.init()
    await command.migrate(title)

if __name__ == '__main__':
    migration_name = str(sys.argv[1])
    print(migration_name)
    asyncio.run(run_migration_task(migration_name))