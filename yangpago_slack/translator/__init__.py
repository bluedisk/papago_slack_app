from . import google
from . import papago
from .common import *

TRANSLATORS = {
    'papago': papago,
    'google': google
}


def get_translator(code: str):
    return TRANSLATORS[code]
