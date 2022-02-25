import pytest 

from tortoise.contrib.test import finalizer, initializer

from tortoise import Tortoise


import asyncio

import os

os.environ['DB_HOST']="127.0.0.1"
os.environ['DB_PORT']="17002"
os.environ['DB_USER']='postgres'
os.environ['DB_PASSWORD']='postgres'