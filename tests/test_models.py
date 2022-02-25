from tortoise.models import Model
from tortoise.fields import IntField, CharField,UUIDField

from uuid import uuid4
class User(Model):

    id = IntField(pk=True)
    firstname = CharField(max_length=255)
    lastname = CharField(max_length=255)

    #role = ForeignKeyField('models.Role')

    class Meta:
        app = 'models'

   

class Role(Model):

    id = IntField(pk=True)
    title = CharField(max_length=255)

    class Meta:
        app = 'models'

    #users = ReverseRelation['User']


    