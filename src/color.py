import typing
import pprint
import datetime as dt

import rich
import rich.pretty
from rich.style import Style
from rich.theme import Theme
from rich.console import Console

console_color = Console(
    theme=Theme({
        "json.brace": Style(bold=True),
        "json.key": Style(color="cyan"),
        "json.str": Style(color="bright_magenta"),
        "json.number": Style(color="yellow", bold=True),
        "json.bool_true": Style(color="bright_green", italic=True),
        "json.bool_false": Style(color="bright_red", italic=True),
        "json.null": Style(dim=True, italic=True)
    })
)
console_plain = Console(
    theme=Theme({
        "json.brace": Style().null(),
        "json.key": Style().null(),
        "json.str": Style().null(),
        "json.number": Style().null(),
        "json.bool_true": Style().null(),
        "json.bool_false": Style().null(),
        "json.null": Style().null()
    })
)

def ppjson(_json:typing.Union[dict,str,list]):
    try:
        _json = _json.json()
    except:
        pass
    
    try:
        console_color.print_json(data=_json)
    except:
        try:
            console_color.print_json(data=dict(_json))
        except:
            try:
                console_color.print(_json)
            except:
                console_color.print("<NO_DATA>")


class _color:
    __slots__ = tuple()
    def __init__(self) -> None:
        pass
    def bold(self,s: str):
        return f"\033[1m{s}\033[0m"
    
    def dim(self,s: str):
        return f"\033[2m{s}\033[0m"
    
    def underline(self,s: str):
        return f"\033[4m{s}\033[0m"
    
    def italic(self,s: str):
        return f"\033[3m{s}\033[0m"
    
    def yellow(self,s: str):
        return f"\033[93m{s}\033[0m"
    
    def cyan(self,s: str):
        return f"\033[96m{s}\033[0m"
    
    def magenta(self,s: str):
        return f"\033[35m{s}\033[0m"
    
    def bright_magenta(self,s: str):
        return f"\033[95m{s}\033[0m"
    
    def red(self,s: str):
        return f"\033[31m{s}\033[0m"
    
    def bright_red(self,s: str):
        return f"\033[91m{s}\033[0m"
    
    def green(self,s: str):
        return f"\033[92m{s}\033[0m"
    
    def blue(self,s: str):
        return f"\033[34m{s}\033[0m"
    
    def bright_yellow(self,s: str):
        return f"\033[93m{s}\033[0m"


class ColorPrint:
    def __init__(self,default_clr:str=None):
        if default_clr:
            self._defaultfunc = getattr(self,default_clr)
        else:
            self._defaultfunc = print
        pass
    
    def __call__(self, x, **kwargs):
        self._defaultfunc(f"{x}", **kwargs)
       
    def bold(self, s: str, i:int=None,**kwargs):
        if i is None:
            i = 0
        ts = "\t" * 0
        print(f"{ts}{color.bold(s)}")
    
    def dim(self, s: str, i:int=None,**kwargs):
        if i is None:
            i = 0
        ts = "\t" * 0
        print(f"{ts}{color.dim(s)}")
    
    def underline(self, s: str, i:int=None,**kwargs):
        if i is None:
            i = 0
        ts = "\t" * 0
        print(f"{ts}{color.underline(s)}")
    
    def italic(self, s: str, i:int=None,**kwargs):
        if i is None:
            i = 0
        ts = "\t" * 0
        print(f"{ts}{color.italic(s)}")
    
    def yellow(self, s: str, i:int=None,**kwargs):
        if i is None:
            i = 0
        ts = "\t" * 0
        print(f"{ts}{color.yellow(s)}")
    
    def cyan(self, s: str, i:int=None,**kwargs):
        if i is None:
            i = 0
        ts = "\t" * 0
        print(f"{ts}{color.cyan(s)}")
    
    def magenta(self, s: str, i:int=None,**kwargs):
        if i is None:
            i = 0
        ts = "\t" * 0
        print(f"{ts}{color.magenta(s)}")
    
    def bright_magenta(self, s: str, i:int=None,**kwargs):
        if i is None:
            i = 0
        ts = "\t" * 0
        print(f"{ts}{color.bright_magenta(s)}")
    
    def red(self, s: str, i:int=None,**kwargs):
        if i is None:
            i = 0
        ts = "\t" * 0
        print(f"{ts}{color.red(s)}")
    
    def bright_red(self, s: str, i:int=None,**kwargs):
        if i is None:
            i = 0
        ts = "\t" * 0
        print(f"{ts}{color.bright_red(s)}")
    
    def green(self, s: str, i:int=None,**kwargs):
        if i is None:
            i = 0
        ts = "\t" * 0
        print(f"{ts}{color.green(s)}")
    
    def blue(self, s: str, i:int=None,**kwargs):
        if i is None:
            i = 0
        ts = "\t" * 0
        print(f"{ts}{color.blue(s)}")
    
    def bright_yellow(self, s: str, i:int=None,**kwargs):
        if i is None:
            i = 0
        ts = "\t" * 0
        print(f"{ts}{color.bright_yellow(s)}")



color = _color()

pp = pprint.PrettyPrinter(sort_dicts=False, width=100)

def serialize_default(x:typing.Any):
    if isinstance(x, dt.time):
        return x.strftime(r"%I:%M %p")
    elif isinstance(x, dt.date):
        return x.strftime(r"%Y-%m-%d")

def pretty_print(obj:typing.Union[typing.Dict,typing.List], colorize:bool=True, json_default=None):
    """
    Print JSON in a colorized, prettified format with a 
    'rich.Console' object
    
    obj : dict, list
        json data
        
    colorize : bool (default = True)
        option to print to terminal in color
    
    """

    if json_default == None:
        json_default = serialize_default

    c = console_color if colorize == True else console_plain

    if type(obj).__name__ == "Response":
        c.print(obj)
        try:
            c.print_json(data=obj.json(), default=json_default)
        except:
            c.print(obj.text)
    
    else:
        try:
            c.print_json(data=obj, default=json_default)
        except:
            c.print(obj)

