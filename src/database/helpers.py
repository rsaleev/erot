from telnetlib import OUTMRK
from typing import Union, List, Any, Dict, Type

from datetime import date

from dictdiffer import diff

from collections import namedtuple

from pydantic import BaseModel
from tortoise.models import Model


def format_date(value:Union[date,None])->str:
    """format_date 

    Args:
        value (Union[datetime,None]): значение даты

    Returns:
        str: форматированное значение в строку или пустая строка
    """
    if not value:
        return ''
    else:
        return value.strftime('%d-%m-%Y')

def format_array(value:List[Any])->str:
    """format_array


    Args:
        value (List[Any]): массив значений (list)

    Returns:
        str: контатенированная строка
    """
    return ''.join(value)

def compare_records(record_values:Dict, input_values:Dict):
    diff_obj = namedtuple('DiffObject', ['column', 'new', 'old'])
    output = []
    result = list(diff(record_values, input_values))
    for res in result:
        diff_type, key, values = res
        if diff_type == 'change':
            diff_obj(column=key, old=values[0], new=values[1])
            output.append(diff_obj)
    return output
            

def record_to_dict(record:Any):
    output = {}
    for k,v in record.__dict__.items():
        if not k.startswith('_'):
            output.update({k:v})
    return output