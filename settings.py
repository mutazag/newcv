import os

def read_settings():
    list_settings = os.environ.get('list_settings', 'api_endpoint')
    ss = {}
    for s in list_settings.split(';'):
        ss[s] = os.environ.get(s, '')
    return ss
