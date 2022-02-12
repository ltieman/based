import enum

class RoleEnum(enum.Enum):
    OPEN = 0
    LOGIN = 10
    READ = 25
    POST = 50
    ADMIN = 100
