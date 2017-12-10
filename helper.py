# -*- coding: utf-8 -*
import json

def tupleUserToDict(data):
    try:
        result = {
            'idUser': data[0],
            'addres': data[1],
            'name': data[2],
            'birthday': data[3],
            'isExpert': data[4],
            'openKey': data[5],
            'organization': data[6]
        }
        return result
    except Exception as e:
        print(e)