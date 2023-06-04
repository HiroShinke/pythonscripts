

import unittest
import subprocess
import os
import shutil
import sys
import re
import hashlib
from datetime import datetime

def cmd_stdout(cmdstr):
    p = subprocess.run(cmdstr,
                       shell=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       check=True)
    return p.stdout

def make_file(p,contents):
    with open(p,"w") as fh:
        fh.write(contents)

def hexdigest(path,type=None):
    m=hashlib.sha1()
    with open(path,"rb") as fh:
        contents = fh.read()
        if type == "blob":
            m.update(b"blob ")
            s = f"{len(contents)}"
            m.update(bytes(s,"iso-8859-1"))
            m.update(b"\x00")
        m.update(contents)
    return m.hexdigest()
        
class GitTest(unittest.TestCase):

    def setUp(self):
        if os.path.exists("testgitdir"):
            shutil.rmtree("testgitdir")
        os.mkdir("testgitdir")
        os.chdir("testgitdir")
        cmd_stdout("git init")
        cmd_stdout("git config user.name HirofumiShinke")
        cmd_stdout("git config user.email hiro.shinke@gmail.com")

    def test_basec1(self):
        make_file("hello.txt","hello world")
        cmd_stdout("git add hello.txt")
        ret = cmd_stdout("git status")
        self.assertTrue(re.search(b"No commits yet",ret))

    def test_basec2(self):
        make_file("hello.txt","hello world")
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m "add hello.txt" hello.txt')
        ret = cmd_stdout("git status")
        self.assertTrue( re.search(b"nothing to commit, working tree clean",ret) )

    def test_basec3(self):
        make_file("hello.txt","hello world\n")
        cmd_stdout("git add hello.txt")
        ret = cmd_stdout("git ls-files -s")
        self.assertEqual(b'100644 3b18e512dba79e4c8300dd08aeb37f8e728b8dad 0\thello.txt\n',ret)

    def test_basec4(self):
        make_file("hello.txt","hello world\n")
        cmd_stdout("git add hello.txt")
        ret = cmd_stdout("git write-tree")
        self.assertEqual(b'68aba62e560c0ebc3396e8ae9335232cd93a3f60\n',ret)

    def test_basec5(self):
        make_file("hello.txt","hello world\n")
        ret = hexdigest("hello.txt","blob")
        self.assertEqual('3b18e512dba79e4c8300dd08aeb37f8e728b8dad',ret)

    def test_basec6(self):
        make_file("hello.txt","hello world\n")
        cmd_stdout("git add hello.txt")
        cmd_stdout("git write-tree")
        ret = cmd_stdout("git cat-file -p 3b18e5")
        self.assertEqual(b"hello world\n",ret)

        ret2 = cmd_stdout("git cat-file -p 68aba6")
        self.assertEqual(b'100644 blob 3b18e512dba79e4c8300dd08aeb37f8e728b8dad\thello.txt\n',
                         ret2)
        ret3 = cmd_stdout("git ls-files -s")
        self.assertEqual(b'100644 3b18e512dba79e4c8300dd08aeb37f8e728b8dad 0\thello.txt\n',
                         ret3)







        
if __name__ == "__main__":
    unittest.main()


    
