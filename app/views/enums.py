from enum import Enum

class Routes(Enum):
    get = 'GET'
    delete = 'DELETE'
    post = 'POST'
    patch = 'PATCH'
    put = 'PUT'
    index = 'INDEX'
    delete = 'DELETE'
    undelete = 'UNDELETE'
    head = 'HEAD'