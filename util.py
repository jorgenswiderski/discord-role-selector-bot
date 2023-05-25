import json


def copy(obj):
    return json.loads(json.dumps(obj))
