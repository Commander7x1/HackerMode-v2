import re
import os
import sys
import time
from threading import Thread

EXAMLPE = """\x1b[0mexample:
    $ findall /sdcard/ '\.py$' \x1b[0;31m# all file python\x1b[0m
    $ findall your/path 'your-pattren' """

class FindAll:
    
    def __init__(self, path: str) -> None:
        self.path: str = path
        self._isdone = False
        self.anim
        
    @property
    def anim(self) -> None:
        text = "Searching..."
        i = ["\\", "|", "/", "-"]
        def _anim():
            index = 0
            while not self._isdone:
                for x in range(len(text)):
                    if self._isdone: break
                    print(f"\r{text[:x]}{text[x].upper() if text[x].islower() else text[x].lower()}{text[x+1:]} {i[index%len(i)]}",end="")
                    index += 1
                    time.sleep(0.2)
        Thread(target=_anim).start()

    def find(self, pattren: str) -> None:
        result: list = []
        data = [0, 0]
        for path, dirs, files in os.walk(self.path):
            for file in files:
                if (i := list(set(re.findall(pattren, file)))):
                    data[0] += 1
                    result.append(
                        os.path.join(
                            f"\x1b[0;36m{path}",
                            "\x1b[0;33m"+ file.replace(
                                i[-1],
                                f"\x1b[0;31m{i[-1]}\x1b[0;33m"
                            )
                        )
                    )
            for dir in dirs:
                if (i := list(set(re.findall(pattren, dir)))):
                    data[1] += 1
                    result.append(
                        os.path.join(
                            f"\x1b[0;36m{path}",
                            "\x1b[0;34m" + dir.replace(
                                i[-1],
                                f"\x1b[0;31m{i[-1]}\x1b[0;34m"
                            )
                        )
                    )
        self._isdone = True
        print('\r                                \r' + '\n'.join(result))
        print(f"\x1b[0m{data[1]} directories, {data[0]} files")



if __name__ == "__main__":
    argv = sys.argv[1:]
    if argv == []:
        pattren = "[\w\W]*"
        path = '.'
    elif len(argv) < 2:
        path = "."
        pattren = argv[0]
    else:
        if os.path.exists(argv[0]):
            path = argv[0]
        else: exit(f"# Not File or Directory '{argv[0]}'\n" + EXAMLPE)
        pattren = argv[-1]
    FindAll(path).find(pattren)
        
