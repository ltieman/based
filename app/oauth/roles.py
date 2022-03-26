import enum


class RoleEnum(enum.Enum):
    BANNED = -1
    OPEN = 0
    LOGIN = 10
    READ = 25
    POST = 50
    ADMIN = 100
