import pytest

import re

def get_content(arg:str, content_list):
    return 
  

def test_parse_values():
    titles = ['Административное приостановление деятельности', 'Административный штраф']
    contents = ['Административное приостановление деятельности: от 1 до 3 (в сутках)', 'Административный штраф: от 1000 до 5000 (в рублях)']
    output = []
    if isinstance(titles, list):
        for title in titles:
            data = {}
            data['snct_subject'] =1
            data['snct_title'] = title 
            content = next(c for c in contents if c.rfind(title)>-1)
            content = content.replace(title, '').replace(':', '').strip()
            data['snct_content'] = content
            output.append(data)
    print(output)