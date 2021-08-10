import os
import sys
import bz2
import zlib
import base64
import marshal
import py_compile

RUNPY: str = b"#!/usr/bin/python3"

ENCRYPTION: list = [
    "binary",
    "bz2",
    "zlib",
    "marshal",
    "pyc",
    "layers",
]
BASE64: list = [
    "base64",
    "base16",
    "base32",
    "base85"
]

class PyPrivate:
    
    def __init__(self, path: str, model: str) -> None:
        self.tmp = path
        if os.path.isdir(path):
            for p, d, f in os.walk(path):
                for file in f:
                    if file.endswith('.py'):
                        self.tmp = os.path.join(p, file)
                        with open(self.tmp, "rb") as f:
                            self.source = f.read()
                        print(f'\x1b[0;36m# encode \x1b[0;33m{self.tmp}')
                        code = RUNPY + b'\n' + self.getattribute(model)()
                        if model == "compile": continue
                        with open(self.tmp, "wb") as f:
                            f.write(code)
                        
            return
        with open(path, "rb") as f:
            self.source = f.read()
        print(f'\x1b[0;36m# encode \x1b[0;33m{self.tmp}')
        code = RUNPY + b'\n' + self.getattribute(model)()
        if model == "compile": return
        with open(path, "wb") as f:
            f.write(code)


    def getattribute(self, attr: str) -> "Function":
        
        if attr in BASE64:
            return self.base64(attr)
        elif attr in ENCRYPTION:
            return eval(f"self.{attr}")
        else:
            raise AttributeError
        
        
    def base64(self, model: str) -> "Function":
        def converter() -> bytes:
            en = eval(f"base64.b{model[-2:]}encode")(self.source)
            return f"import base64\nexec(compile(base64.b{model[-2:]}decode({en[::-1]}[::-1]),'string', 'exec'))".encode()
        return converter
        
        
    def bz2(self) -> bytes:
        en = bz2.compress(self.source)
        return f"x = lambda t, m: eval(f\"__import__('{{m}}'){{t}}press\")({en[::-1]}[::-1])\nexec(compile(x(\".decom\", \"bz2\"),\"string\", \"exec\"))".encode()
    
    
    def zlib(self) -> bytes:
        en = zlib.compress(self.source)
        return f"x = lambda t, m: eval(f\"__import__('{{m}}'){{t}}press\")({en[::-1]}[::-1])\nexec(compile(x(\".decom\", \"zlib\"),\"string\", \"exec\"))".encode()
        
    def marshal(self) -> bytes:
        en = marshal.dumps(compile(self.source, "string", "exec"))
        return f"import marshal as m\nexec(m.loads({en[::-1]}[::-1]))".encode()
    
    def compile(self) -> None:
        try:
            en = py_compile.compile(self.tmp, self.tmp+'c', doraise=True)
        except py_compile.PyCompileError as e:
            msg = f"{e.exc_type_name}: {e.exc_value}"
            raise SyntaxError(msg)
        raise TypeError(en)
            
        
    def layers(self) -> bytes:
        for model in BASE64 + ENCRYPTION[:-2]:
            self.source = self.getattribute(model)()
            print(f"\x1b[0;34m# Layers \x1b[0;32m{model}")
        return self.source

    def binary(self) -> bytes:
        en = list(map(lambda t: int(bin(ord(t))[2:]), self.source.decode()))
        return f"data = lambda : ({en}, lambda t: chr(int(f'0b{{t}}', 2)))[::-1]\nexec(compile(''.join(map(*data())), 'string', 'exec'))".encode()

    def pyc(self) -> bytes:
        try:
            py_compile.compile(self.tmp, f"{self.tmp}c", doraise=True)
        except py_compile.PyCompileError as e:
            raise SyntaxError(f"{e.exc_value}")
        return b""
        


if __name__ == "__main__":
    argv = sys.argv[1:]
    optional = '\n'.join(f"\x1b[0;36m    {x}" for x in (BASE64 + ENCRYPTION))
    error = f"\x1b[0;31m# Not File or Model!\n\x1b[0;33mexample:\n    \x1b[0m$ \x1b[0;36mpyprivate \x1b[0;33mmyfile.py \x1b[0;32mmarshal\n    \x1b[0;31mor\n    \x1b[0m$ \x1b[0;36mpyprivate \x1b[0;34m/path/to/mytool \x1b[0;32mmarshal\n\x1b[0;33mencryption:\n{optional}"
    if len(argv) >= 2:
        path, model = argv[:2]
    elif len(argv) < 2:
        exit(error)
    if path in BASE64 + ENCRYPTION:
        path, model = argv[:2][::-1]    
        exit(error)
    try:
        PyPrivate(path, model)    
        print("\x1b[0;34m# Done")
    except AttributeError:
        exit(error)
    except Exception as e:
        print(f"\x1b[0;31m# {e.__class__.__name__}:\x1b[0m {e}")
    



        
        
