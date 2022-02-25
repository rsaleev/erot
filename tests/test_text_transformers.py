import re


def test_split_transformer():
    regex = "\\s*;\\s*|\\s*/.s*|\n"
    value = "Осуществляемая деятельность, в отношении которой устанавливаются обязательные требования"
   
    output = re.split(regex, value)
    print(output)