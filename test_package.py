

import unittest
from pathlib import Path
import shutil

def make_file(path,contents):
    p = Path(path)
    p.parent.mkdir(exist_ok=True,parents=True)
    with open(p,"w") as fh:
        fh.write(contents)

class ModTest(unittest.TestCase):

    def setup(self):
        if Path("xxxx").is_dir():
            shutil.retree("xxxx")

    def test_basic1(self):
        make_file("xxxx/__init__.py",
                  """
def foo():
    print("hello,module: xxxx")
                  
""")
        exec("""
import xxxx
xxxx.foo()
""",    dict(),dict())

    def test_basic2(self):
        make_file("xxxx/yyyy.py",
                  """
def foo():
    print("hello,module: xxxx.yyyy")
                  
""")
        exec("""
import xxxx.yyyy
xxxx.yyyy.foo()
""",    dict(),dict())


    def test_basic3(self):

        make_file("xxxx/__init__.py",
                  """
from . import yyyy.py
""")

        make_file("xxxx/yyyy.py",
                  """
def foo():
    print("hello,module: xxxx.yyyy")
                  
""")

        
        exec("""
import xxxx
xxxx.yyyy.foo()
""",    dict(),dict())


if __name__ == "__main__":
    unittest.main()
