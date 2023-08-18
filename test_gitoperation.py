

import unittest
import subprocess
import os
import shutil
import sys
import re
import hashlib
from datetime import datetime

def cmd_stdout_b(cmdstr):
    p = subprocess.run(cmdstr,
                       shell=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       check=True)
    return p.stdout

def cmd_stdout(cmdstr):
    return cmd_stdout_b(cmdstr).decode("cp932")

def make_file(p,contents):
    if dir := os.path.dirname(p):
        os.makedirs(dir, exist_ok = True)
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

DIR_ORG = os.path.abspath(".")

class GitTest(unittest.TestCase):

    def setUp(self):
        os.chdir(DIR_ORG)
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
        self.assertTrue(re.search("No commits yet",ret))

    def test_basec2(self):
        make_file("hello.txt","hello world")
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m "add hello.txt" hello.txt')
        ret = cmd_stdout("git status")
        self.assertTrue( re.search("nothing to commit, working tree clean",ret) )

    def test_basec3(self):
        make_file("hello.txt","hello world\n")
        cmd_stdout("git add hello.txt")
        ret = cmd_stdout("git ls-files -s")
        self.assertEqual('100644 3b18e512dba79e4c8300dd08aeb37f8e728b8dad 0\thello.txt\n',ret)

    def test_basec4(self):
        make_file("hello.txt","hello world\n")
        cmd_stdout("git add hello.txt")
        ret = cmd_stdout("git write-tree")
        self.assertEqual('68aba62e560c0ebc3396e8ae9335232cd93a3f60\n',ret)

    def test_basec5(self):
        make_file("hello.txt","hello world\n")
        ret = hexdigest("hello.txt","blob")
        self.assertEqual('3b18e512dba79e4c8300dd08aeb37f8e728b8dad',ret)

    def test_basec6(self):
        make_file("hello.txt","hello world\n")
        cmd_stdout("git add hello.txt")
        cmd_stdout("git write-tree")
        ret = cmd_stdout("git cat-file -p 3b18e5")
        self.assertEqual("hello world\n",ret)

        ret2 = cmd_stdout("git cat-file -p 68aba6")
        self.assertEqual('100644 blob 3b18e512dba79e4c8300dd08aeb37f8e728b8dad\thello.txt\n',
                         ret2)
        ret3 = cmd_stdout("git ls-files -s")
        self.assertEqual('100644 3b18e512dba79e4c8300dd08aeb37f8e728b8dad 0\thello.txt\n',
                         ret3)


    def test_merge1(self):

        os.environ["GIT_AUTHOR_DATE"] = "Fri May 5 20:30:55 2023 +0900"
        os.environ["GIT_COMMITTER_DATE"] = "Fri May 5 20:30:55 2023 +0900"
        
        make_file("hello.txt","""\
hello, world
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m A')

        make_file("hello.txt","""\
hello, world
goodby japan
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m B')

        make_file("hello.txt","""\
hello, world
goodby japan
goodby america
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m C')

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)

        cmd_stdout("git checkout -b new-topic")

        make_file("hello.txt","""\
hello, world
goodby japan
goodby europe
goodby america
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m D')

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 967e46b D
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)
        
        cmd_stdout("git checkout master")

        make_file("hello.txt","""\
hello, world
goodby japan
goodby america
goodby africa
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m F')

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 65baea3 F
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)

        cmd_stdout("git merge new-topic")

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
*   2108e11 Merge branch 'new-topic'
|\  
| * 967e46b D
* | 65baea3 F
|/  
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)

        ret = cmd_stdout("git show-branch")
        self.assertEqual("""\
* [master] Merge branch 'new-topic'
 ! [new-topic] D
--
-  [master] Merge branch 'new-topic'
*+ [new-topic] D
"""
                         ,ret)
        
    def test_remote1(self):
        make_file("hello.txt","hello world")
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m "add hello.txt" hello.txt')
        
        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir2"):
            shutil.rmtree("testgitdir2")
        cmd_stdout("cp -r testgitdir testgitdir2")
        
        os.chdir("testgitdir2")
        cmd_stdout("git remote add first ../testgitdir")
        ret = cmd_stdout("git remote")
        self.assertEqual("first\n",ret)
        cmd_stdout("git remote update first")
        ret = cmd_stdout("git branch -a")
        self.assertEqual('* master\n' + 
                         '  remotes/first/master\n',
                         ret)
        
        os.chdir("../testgitdir")
        make_file("hello1.txt","hello world")
        cmd_stdout("git add hello1.txt")
        ret = cmd_stdout('git commit -m "add hello1.txt" hello1.txt')
        
        os.chdir("../testgitdir2")
        cmd_stdout("git remote update")
        cmd_stdout("git merge first/master")
        ret = cmd_stdout("ls")
        self.assertEqual('hello.txt\nhello1.txt\n',ret)

    def test_remote2(self):
        make_file("hello.txt","hello world")
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m "add hello.txt" hello.txt')
        
        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir2"):
            shutil.rmtree("testgitdir2")
        cmd_stdout("cp -r testgitdir testgitdir2")
        
        os.chdir("testgitdir2")
        cmd_stdout("git remote add first ../testgitdir")
        ret = cmd_stdout("git remote")
        self.assertEqual("first\n",ret)
        cmd_stdout("git remote update first")
        ret = cmd_stdout("git branch -a")
        self.assertEqual('* master\n' + 
                         '  remotes/first/master\n',
                         ret)
        
        os.chdir("../testgitdir")
        make_file("hello1.txt","hello world")
        cmd_stdout("git add hello1.txt")
        ret = cmd_stdout('git commit -m "add hello1.txt" hello1.txt')
        
        os.chdir("../testgitdir2")
        cmd_stdout("git pull first master")
        ret = cmd_stdout("ls")
        self.assertEqual('hello.txt\nhello1.txt\n',ret)


    def test_remote2_2(self):
        make_file("hello.txt","hello world")
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m "add hello.txt" hello.txt')
        
        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir2"):
            shutil.rmtree("testgitdir2")
        cmd_stdout("cp -r testgitdir testgitdir2")
        
        os.chdir("testgitdir2")
        cmd_stdout("git remote add first ../testgitdir")
        ret = cmd_stdout("git remote")
        self.assertEqual("first\n",ret)
        cmd_stdout("git remote update first")
        ret = cmd_stdout("git branch -a")
        self.assertEqual('* master\n' + 
                         '  remotes/first/master\n',
                         ret)
        cmd_stdout("git branch --set-upstream-to=first/master master")
        
        os.chdir("../testgitdir")
        make_file("hello1.txt","hello world")
        cmd_stdout("git add hello1.txt")
        ret = cmd_stdout('git commit -m "add hello1.txt" hello1.txt')
        
        os.chdir("../testgitdir2")
        cmd_stdout("git pull")
        ret = cmd_stdout("ls")
        self.assertEqual('hello.txt\nhello1.txt\n',ret)


    def test_remote3(self):
        make_file("hello.txt","hello world")
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m "add hello.txt" hello.txt')
        
        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir2"):
            shutil.rmtree("testgitdir2")
        cmd_stdout("cp -r testgitdir testgitdir2")
        
        os.chdir("testgitdir2")
        cmd_stdout("git remote add first ../testgitdir")
        ret = cmd_stdout("git remote")
        self.assertEqual("first\n",ret)
        cmd_stdout("git remote update first")
        ret = cmd_stdout("git branch -a")
        self.assertEqual('* master\n' + 
                         '  remotes/first/master\n',
                         ret)
        
        os.chdir("../testgitdir")
        make_file("hello1.txt","hello world")
        cmd_stdout("git add hello1.txt")
        ret = cmd_stdout('git commit -m "add hello1.txt" hello1.txt')
        
        os.chdir("../testgitdir2")
        cmd_stdout("git pull first master")
        ret = cmd_stdout("ls")
        self.assertEqual('hello.txt\nhello1.txt\n',ret)
        
        make_file("hello2.txt","hello world2")
        cmd_stdout("git add hello2.txt")
        ret = cmd_stdout('git commit -m "add hello2.txt" hello2.txt')
        
        os.chdir("../testgitdir")

        cmd_stdout("git remote add second ../testgitdir2")
        ret = cmd_stdout("git remote")
        self.assertEqual("second\n",ret)
        cmd_stdout("git remote update second")
        ret = cmd_stdout("git branch -a")
        self.assertEqual('* master\n' + 
                         '  remotes/second/master\n',
                         ret)

        cmd_stdout("git pull second master")
        ret = cmd_stdout("ls")
        self.assertEqual("""\
hello.txt
hello1.txt
hello2.txt
"""
                         ,ret)


    def test_push1(self):

        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir.git"): shutil.rmtree("testgitdir.git")
        if os.path.exists("testgitdir2"): shutil.rmtree("testgitdir2")
        if os.path.exists("testgitdir3"): shutil.rmtree("testgitdir3")
            
        cmd_stdout("git clone --bare testgitdir testgitdir.git")
        cmd_stdout("git clone testgitdir.git testgitdir2")
        cmd_stdout("git clone testgitdir.git testgitdir3")

        os.chdir("testgitdir2")
        make_file("hello1.txt","hello world")
        cmd_stdout("git add hello1.txt")
        cmd_stdout('git commit -m "add hello1.txt" hello1.txt')
        cmd_stdout("git push origin")

        os.chdir("../testgitdir3")
        cmd_stdout("git pull origin master")
        ret = cmd_stdout("ls")
        self.assertEqual("""\
hello1.txt
"""
                         ,ret)

    def test_push2(self):

        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir.git"): shutil.rmtree("testgitdir.git")
        if os.path.exists("testgitdir2"): shutil.rmtree("testgitdir2")
        if os.path.exists("testgitdir3"): shutil.rmtree("testgitdir3")
            
        cmd_stdout("git clone --bare testgitdir testgitdir.git")
        cmd_stdout("git clone testgitdir.git testgitdir2")
        cmd_stdout("git clone testgitdir.git testgitdir3")

        os.chdir("testgitdir2")
        make_file("hello1.txt","hello world\n")
        cmd_stdout("git add hello1.txt")
        cmd_stdout('git commit -m "add hello1.txt" hello1.txt')
        make_file("hello1.txt","hello world\nhello world, again\n")
        cmd_stdout("git push origin")

        cmd_stdout("git checkout -b new-topic")
        cmd_stdout("git add hello1.txt")
        cmd_stdout('git commit -m "add hello1.txt" hello1.txt')        
        cmd_stdout("git push origin new-topic")

        os.chdir("../testgitdir3")
        cmd_stdout("git fetch origin")
        cmd_stdout("git checkout --track -b new-topic origin/new-topic")
        ret = cmd_stdout("git diff HEAD~1 HEAD")
        self.assertEqual("""\
diff --git a/hello1.txt b/hello1.txt
index 3b18e51..b652454 100644
--- a/hello1.txt
+++ b/hello1.txt
@@ -1 +1,2 @@
 hello world
+hello world, again
"""
              ,ret)

        cmd_stdout("git checkout master")
        cmd_stdout("git merge new-topic")
        cmd_stdout("git push origin master")

        os.chdir("../testgitdir2")
        cmd_stdout("git pull origin master")
        ret = cmd_stdout("git diff HEAD~1 HEAD")
        self.assertEqual("""\
diff --git a/hello1.txt b/hello1.txt
index 3b18e51..b652454 100644
--- a/hello1.txt
+++ b/hello1.txt
@@ -1 +1,2 @@
 hello world
+hello world, again
"""
                         ,ret)

        os.chdir("../testgitdir3")
        ret = cmd_stdout("git branch -a")
        self.assertEqual("""\
* master
  new-topic
  remotes/origin/master
  remotes/origin/new-topic
"""
              ,ret)
        cmd_stdout("git branch -d new-topic")
        cmd_stdout("git push origin --delete new-topic")
        ret = cmd_stdout("git branch -a")
        self.assertEqual("""\
* master
  remotes/origin/master
"""
              ,ret)


        os.chdir("../testgitdir2")
        cmd_stdout("git checkout master")        
        cmd_stdout("git pull origin master")
        cmd_stdout("git fetch --prune origin")
        cmd_stdout("git branch -d new-topic")
        ret = cmd_stdout("git branch -a")        
        self.assertEqual("""\
* master
  remotes/origin/master
"""
              ,ret)
        
if __name__ == "__main__":
    unittest.main()


    
