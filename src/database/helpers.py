from typing import Union, List, Any, Dict, Deque, ChainMap, Tuple

from datetime import date

from dictdiffer import diff

from collections import namedtuple, ChainMap, deque

from tortoise.models import Model

from pypika.terms import Array

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


            

def kwargs_to_pg_types(**kwargs):
    filter = {}
    for k, v in kwargs.items():
        if isinstance(v, list):
            if all(v):
                filter[k] = Array(*v)
            else:
                filter[k] = None
        else:
            filter[k] = v 
    return filter

def chainmap_with_unique_keys(arg:Tuple[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    chainmap_with_unique_keys _summary_

    Создание массива словарей с уникальными ключами из массива словарей с дублирующимися ключами


    Args:
        arg (List[Dict[str, Any]]): массив словарей с дублирующимися ключами

    Returns:
        List[Dict[str, Any]]: массив словарей с уникальными значениями
    """


    unique_keys:List[str] = [next(k for k in tuple(elem.keys())) for elem in arg]
    deque_arr:Deque = deque(arg)
    last_keys = []
    output = []
    container = []
    while deque_arr:
        key = next(k for k in tuple(deque_arr[0].keys()))
        if not key in last_keys:
            container.append(deque_arr[0])
            deque_arr.popleft()
            last_keys.append(key)
        else:
            if all([k in unique_keys for k in last_keys]):
                d = dict(ChainMap(*container))
                last_keys.clear()
                container.clear()
                output.append(d)
            else:
                continue
    else:
        d = dict(ChainMap(*container))
        last_keys.clear()
        container.clear()
        output.append(d)
    return output

def model_to_dict(arg:Model)->Dict[str, Any]:
    """
    model_to_dict

    Возврат значений модели ORM в виде dict

    Args:
        arg (Union[Model, List[Model]]): значения записи из БД

    Returns:
        Union[Dict[str, Any], List[Dict[str, Any]]]: массив значений записей из БД
    """
    output = {}
    for k, v in arg.__dict__.items():
        if not k.startswith('_'):
            output.update({k: v})
    return output


def compare_records(record_values:Dict[str, Any], input_values:Dict[str, Any]):
    DiffObj = namedtuple('DiffObject', ['column', 'new', 'old'])
    output = []
    result = list(diff(record_values, input_values))
    for res in result:
        diff_type, key, values = res
        if diff_type == 'change':
            diff_obj = DiffObj(column=key, old=values[0], new=values[1])._asdict()
            output.append(diff_obj)
    return output
   