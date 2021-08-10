#!/usr/bin/python3
import io
import re
import os
import sys
import time
import zlib
import base64
import marshal
from pkgutil import read_code

from uncompyle6 import PYTHON_VERSION
from uncompyle6.main import decompile

ENCODEING = "utf-8"
ALGORITHOMS = (
    "zlib",
    "marshal",
    "base16",
    "base32",
    "base64",
    "base85",
    "machine-code",
    "eval-filter",
    "string-filter",
)
COPYRIGHT = """
# Decoded by HackerMode tool...
# Copyright: PSH-TEAM
# Follow us on telegram ( @psh_team )
""".lstrip()


class CodeSearchAlgorithms:
    @staticmethod
    def bytecode(string: str) -> bytes:
        pattern: str = r"""(((b|bytes\()["'])(.+)(["']))"""
        length: int = 0
        string_data: str = ""
        for string in re.findall(pattern, string):
            if len(string[3]) > length:
                length = len(string[3])
                string_data = string[3]
        if not string_data:
            raise Exception()
        return eval(f"b'{string_data}'")

    @staticmethod
    def eval_filter(string: str):
        pattern: str = r"(eval(?:[\s]+)?\()"
        if len(eval_poss := re.findall(pattern, string)) < 0:
            raise Exception()
        for eval_pos in eval_poss:
            eval_function: str = string[string.find(eval_pos):string.find(eval_pos) + len(eval_pos)]
            open_brackets: int = 1

            for _chr in string[string.find(eval_pos) + len(eval_pos):]:
                if _chr == "(":
                    open_brackets += 1
                elif _chr == ")":
                    open_brackets -= 1
                eval_function += _chr
                if open_brackets == 0:
                    break
            string = string[string.find(eval_function) + len(eval_function):]
            yield eval_function

    @staticmethod
    def string_filter(string: str):
        pattern = r"""(["'](?:\\[\w0-9]+)+["'])"""
        if len(strings := re.findall(pattern, string)) < 0:
            raise Exception()
        for _str in strings:
            yield _str


class DecodingAlgorithms:
    def __init__(self, file_data, save_file):
        self.file_data = file_data
        print("Finding the best algorithm:")
        for algogithom in ALGORITHOMS:
            try:
                self.file_data = self.__getattribute__(algogithom.replace("-", "_"))()
                print(f"# \033[1;32m{algogithom} ✓\033[0m", end="\r")
            except Exception:
                print(f"# \033[1;31m{algogithom}\033[0m")
                continue

            if "filter" in algogithom:
                print("")
                continue

            layers: int = 0
            while True:
                try:
                    self.file_data = self.__getattribute__(algogithom)()
                    layers += 1
                    print(f"# \033[1;32m{algogithom} layers {layers} ✓\033[0m", end="\r")
                    time.sleep(.02)
                except Exception:
                    print(f"\n# \033[1;32mDONE ✓\033[0m")
                    break
            break
        try:
            with open(save_file, "w") as file:

                file.write(COPYRIGHT+self.file_data)
        except Exception:
            print("# \033[1;31mFailed to decode the file!\033[0m")

    def marshal(self) -> str:
        bytecode = marshal.loads(CodeSearchAlgorithms.bytecode(self.file_data))
        out = io.StringIO()
        version = PYTHON_VERSION if PYTHON_VERSION < 3.9 else 3.8
        decompile(version, bytecode, out, showast=False)
        return "\n".join(out.getvalue().split("\n")[4:]) + '\n'

    def zlib(self) -> str:
        return zlib.decompress(
            CodeSearchAlgorithms.bytecode(self.file_data)
        ).decode(ENCODEING)

    def base16(self) -> str:
        return base64.b16decode(
            CodeSearchAlgorithms.bytecode(self.file_data)
        ).decode(ENCODEING)

    def base32(self) -> str:
        return base64.b32decode(
            CodeSearchAlgorithms.bytecode(self.file_data)
        ).decode(ENCODEING)

    def base64(self) -> str:
        return base64.b64decode(
            CodeSearchAlgorithms.bytecode(self.file_data)
        ).decode(ENCODEING)

    def base85(self) -> str:
        return base64.b85decode(
            CodeSearchAlgorithms.bytecode(self.file_data)
        ).decode(ENCODEING)

    def machine_code(self) -> str:
        out = io.StringIO()
        version = PYTHON_VERSION if PYTHON_VERSION < 3.9 else 3.8
        decompile(version, self.file_data, out, showast=False)
        data = out.getvalue() + '\n'
        if self.file_data == data:
            raise Exception()
        return data

    def eval_filter(self) -> str:
        all_eval_functions = list(set(list(CodeSearchAlgorithms.eval_filter(self.file_data))))
        for func in all_eval_functions:
            if not func.strip():
                all_eval_functions.remove(func)

        exceptions = 0
        for eval_f in all_eval_functions:
            try:
                eval_body = re.findall(r"\((.+)\)", eval_f)[0]
                bad_functions = ["eval", "exec"]
                is_in = False
                for function in bad_functions:
                    if function in eval_body:
                        is_in = True
                if is_in:
                    exceptions += 1
                    continue
            except IndexError:
                continue

            try:
                try:
                    eval_data = eval(f"b{eval_body}").decode(ENCODEING)
                except Exception:
                    eval_data = eval(eval_body)
                self.file_data = self.file_data.replace(eval_f, eval_data)
            except Exception:
                exceptions += 1
        if exceptions == len(all_eval_functions):
            raise Exception()
        return self.file_data

    def string_filter(self) -> str:
        all_strings = list(set(list(CodeSearchAlgorithms.string_filter(self.file_data))))
        exceptions = 0
        for _str in all_strings:
            try:
                self.file_data = self.file_data.replace(_str, f"'{eval(_str)}'")
            except Exception:
                exceptions += 1
        if exceptions == len(all_strings):
            raise Exception()
        return self.file_data


if __name__ == '__main__':
    if len(sys.argv) > 2:
        if not os.path.isfile(sys.argv[1]):
            exit(f"# file not found!: {sys.argv[1]}")
        try:
            with open(sys.argv[1], "r") as file:
                data = file.read()
        except UnicodeDecodeError:
            with io.open_code(sys.argv[1]) as f:
                data = read_code(f)
        DecodingAlgorithms(data, sys.argv[2])
    else:
        print("USAGE:\n decode file.py output.py")
