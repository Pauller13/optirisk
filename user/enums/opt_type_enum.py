from enum import Enum


class OTPTypeEnum(Enum):
    PASSWORD = 'PASSWORD'
    TWO_FACTOR_AUTH = 'TWO_FACTOR_AUTH'

    @classmethod
    def choices(cls):
        return [(item.name, item.value) for item in cls]

    @classmethod
    def human_readable(cls, value):
        return dict(cls.choices()).get(value, value)