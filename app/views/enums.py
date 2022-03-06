from enum import Enum

class Routes(Enum):
    get = 'GET'
    delete = 'DELETE'
    post = 'POST'
    patch = 'PATCH'
    put = 'PUT'
    index = 'INDEX'
    undelete = 'UNDELETE'
    head = 'HEAD'