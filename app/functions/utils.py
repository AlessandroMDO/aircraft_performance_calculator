from functools import wraps
import logging
from logging.config import dictConfig
from functools import lru_cache


def deep_freeze(thing):
    from collections.abc import Collection, Mapping, Hashable
    from frozendict import frozendict
    if thing is None or isinstance(thing, str):
        return thing
    elif isinstance(thing, Mapping):
        return frozendict({k: deep_freeze(v) for k, v in thing.items()})
    elif isinstance(thing, Collection):
        return tuple(deep_freeze(i) for i in thing)
    elif not isinstance(thing, Hashable):
        raise TypeError(f"unfreezable type: '{type(thing)}'")
    else:
        return thing


def deep_freeze_args(func):

    @wraps(func)
    def wrapped(*args, **kwargs):
        return func(*deep_freeze(args), **deep_freeze(kwargs))
    return wrapped

def print_formatted_string(input_string=None, total_length=50, how=None):
    if how == "center":
        formatted_string = f"| {input_string:^{total_length - 4}} |"
    elif how == "left":
        formatted_string = f"| {input_string:<{total_length - 4}} |"
    elif how == "top":
        formatted_string = f"|{r'*' * (total_length - 2)}|\n|{'-' * (total_length - 2)}|"
    elif how == "bottom":
        formatted_string = f"|{'-' * (total_length - 2)}|\n|{r'*' * (total_length - 2)}|"
    else:
        formatted_string = f"|{'-' * (total_length - 2)}|"
    print(formatted_string)

def hash_dict(func):
    """Transform mutable dictionnary
    Into immutable
    Useful to be compatible with cache
    """
    class HDict(dict):
        def __hash__(self):
            return hash(frozenset(self.items()))

    @wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple([HDict(arg) if isinstance(arg, dict) else arg for arg in args])
        kwargs = {k: HDict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)
    return wrapped


@lru_cache()
def get_logger():
    logging_config = dict(
        version=1,
        formatters={
            'f': {'format': '%(asctime)s | %(name)-4s | %(levelname)-4s | %(message)s'}},
        handlers={
            'h': {'class': 'logging.StreamHandler',
                  'formatter': 'f',
                  'level': logging.DEBUG}
        },
        root={
            'handlers': ['h'],
            'level': logging.DEBUG,
        },
    )

    dictConfig(logging_config)

    logger = logging.getLogger()

    return logger


def default_graph_colors():

    colors = {
        "blue": "#1D3D7B",
        "black": "#000000",
        "red":  "#E63946",
        "medium_blue": "#457B9D",
        "light_blue": "#A8DADC",
        "light_white": "F1FAEE",
        "green": "#43aa8b",
        "dark_green": "#1b4332"
    }

    return colors
def linspace(a, b, n=100):
    if n < 2:
        return b
    diff = (float(b) - a)/(n - 1)
    return [diff * i + a  for i in range(n)]