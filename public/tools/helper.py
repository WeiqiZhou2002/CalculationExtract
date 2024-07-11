from typing import List, Dict


def exists(obj, fields: List):
    temp = obj
    for field in fields:
        if isinstance(field, str):
            if isinstance(temp, Dict) and field in temp:
                temp = temp[field]
            else:
                return False
        elif isinstance(field, int):
            if isinstance(temp, List):
                if 0 <= field < len(temp):
                    temp = temp[field]
                elif field < 0 and abs(field) <= len(temp):
                    temp = temp[field]
                else:
                    return False
            else:
                return False
    return True


def findValue(obj, paths):
    if exists(obj, paths):
        temp = obj
        for path in paths:
            temp = temp[path]
        return temp
    else:
        return None


def parseVarray(elem):
    if elem.get("type", None) == "logical":
        m = [[i == "T" for i in v.text.split()] for v in elem]
    else:
        m = [[float(i) if '*' not in i else None for i in v.text.split()] for v in elem]
    return m
