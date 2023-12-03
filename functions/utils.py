from functools import wraps
import logging
from logging.config import dictConfig
from functools import lru_cache

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
