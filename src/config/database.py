import os 

CONFIG = {
    "connections": {
        "erot": {
            "engine":"tortoise.backends.asyncpg",
            "credentials": {
                "user": 'backend',
                "password": os.environ['DB_PASSWORD'],
                "host":os.environ['DB_HOST'],
                "port":os.environ['DB_PORT'],
                "database": "erot",
                "schema":"public",
                "ssl":False
            }
        }
    },
    "apps": {
        "erot":{
            "models": ["src.database.models.erot"],
            "default_connection":"erot"
        }
    },
    "use_tz": False,
    "timezone": "Europe/Moscow"
    }