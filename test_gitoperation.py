

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

def cmd_stdout(cmdstr,print_=False):
    try:
        rets = cmd_stdout_b(cmdstr).decode("cp932")
        if print_:
            print(rets)
        return rets
    except Exception as e:
        if print_:
            print(e.stdout.decode("cp932"))
        raise e

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


    def test_diff1(self):
        make_file("hello1.txt","""\
hello, world
"""
                  )
        cmd_stdout('git add *')
        cmd_stdout('git commit -m A')                  

        make_file("hello1.txt","""\
hello, world
hello, japan
"""
                  )
        make_file("hello2.txt","""\
hello, world
"""
                  )
        cmd_stdout('git add *')
        cmd_stdout('git commit -m B')

        self.assertEqual("""\
hello1.txt
hello2.txt
"""
                         ,cmd_stdout('git diff --name-only HEAD~1 HEAD'))
                         
    def test_checkout1(self):

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

        cmd_stdout("git branch new-topic")

        make_file("hello.txt","""\
hello, world
goodby japan
goodby europe
goodby america
"""
                  )
        cmd_stdout("git checkout new-topic")

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


    def test_checkout2(self):

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
goooby world
goodby america
"""
                  )

        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m E')

        cmd_stdout("git checkout master")
        
        make_file("hello.txt","""\
hello, world
goodby japan
goodby europe
goodby america
"""
                  )
        
        cmd_stdout("git checkout -m new-topic")
        self.assertEqual("""\
hello, world
goodby japan
<<<<<<< new-topic
goooby world
=======
goodby europe
>>>>>>> local
goodby america
"""
                         ,cmd_stdout("cat hello.txt"))

        make_file("hello.txt","""\
hello, world
goodby japan
goodby europe
goooby world
goodby america
"""
                  )

        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m D')

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 2a28b8c D
* 1683878 E
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)

    def test_checkout3(self):

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

        cmd_stdout("git checkout b3db10b")
        self.assertEqual("""\
hello, world
goodby japan
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("""\
* (HEAD detached at b3db10b)
  master
"""
                         ,cmd_stdout("git branch -a"))

        cmd_stdout("git checkout master")
        self.assertEqual("""\
hello, world
goodby japan
goodby america
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("""\
* master
"""
                         ,cmd_stdout("git branch -a"))
        
                         
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

    def test_merge2(self):

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
goodby america
goodby europe
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m D')

        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 36da5b2 D
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

        with self.assertRaises(Exception) as cm:
            cmd_stdout("git merge new-topic")

        self.assertEqual("""\
On branch master
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   hello.txt

no changes added to commit (use "git add" and/or "git commit -a")
"""
                         ,cmd_stdout('git status'))
        
        self.assertEqual("""\
hello, world
goodby japan
goodby america
<<<<<<< HEAD
goodby africa
=======
goodby europe
>>>>>>> new-topic
"""
                         ,cmd_stdout("cat hello.txt"))
            
        make_file("hello.txt","""\
hello, world
goodby japan
goodby america
goodby europe
goodby africa
"""
                  )


        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m "F\'"')
        
        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
*   6b8756b F'
|\  
| * 36da5b2 D
* | 65baea3 F
|/  
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)

        ret = cmd_stdout("git show-branch")
        self.assertEqual("""\
* [master] F'
 ! [new-topic] D
--
-  [master] F'
*+ [new-topic] D
"""
                         ,ret)

    def test_rebase1(self):

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

        make_file("hello.txt","""\
hello, world
goodby japan
goodby europe
goodby america
goodby world
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout('git commit -m E')
        
        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* 91ed2a5 E
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

        with self.assertRaises(subprocess.SubprocessError) as cm:
            cmd_stdout("git rebase new-topic")

        self.assertEqual("""\
hello, world
goodby japan
goodby europe
goodby america
<<<<<<< HEAD
goodby world
=======
goodby africa
>>>>>>> 65baea3 (F)
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("""\
interactive rebase in progress; onto 91ed2a5
Last command done (1 command done):
   pick 65baea3 F
No commands remaining.
You are currently rebasing branch 'master' on '91ed2a5'.
  (fix conflicts and then run "git rebase --continue")
  (use "git rebase --skip" to skip this patch)
  (use "git rebase --abort" to check out the original branch)

Unmerged paths:
  (use "git restore --staged <file>..." to unstage)
  (use "git add <file>..." to mark resolution)
	both modified:   hello.txt

no changes added to commit (use "git add" and/or "git commit -a")
"""
                         ,cmd_stdout("git status"))

        make_file("hello.txt","""\
hello, world
goodby japan
goodby europe
goodby america
goodby africa
goodby world
"""
                  )
        cmd_stdout("git add hello.txt")
        cmd_stdout("git commit -m \"F'\"")
        cmd_stdout("git rebase --continue")
        
        ret = cmd_stdout("git log --graph --abbrev-commit --oneline")
        self.assertEqual("""\
* e316ff3 F'
* 91ed2a5 E
* 967e46b D
* 40c9072 C
* b3db10b B
* 70809e4 A
"""
                         ,ret)

        ret = cmd_stdout("git show-branch")
        self.assertEqual("""\
* [master] F'
 ! [new-topic] E
--
*  [master] F'
*+ [new-topic] E
"""
                         ,ret)

        ret = cmd_stdout("cat hello.txt")
        self.assertEqual("""\
hello, world
goodby japan
goodby europe
goodby america
goodby africa
goodby world
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


    def test_sparse1(self):

        os.chdir(DIR_ORG)
        if os.path.exists("testgitdir.git"): shutil.rmtree("testgitdir.git")
        if os.path.exists("testgitdir2"): shutil.rmtree("testgitdir2")
        if os.path.exists("testgitdir3"): shutil.rmtree("testgitdir3")
            
        cmd_stdout("git clone --bare testgitdir testgitdir.git")
        cmd_stdout("git clone testgitdir.git testgitdir2")

        os.chdir("testgitdir2")
        make_file("xxx/hello1.txt","hello world")
        make_file("xxx/hello2.txt","hello world")        
        make_file("goodbye1.txt","goodbye world")
        make_file("goodbye2.txt","goodbye world")
        cmd_stdout("git add *")
        cmd_stdout('git commit -m "add all"')
        cmd_stdout("git push origin")

        os.mkdir("../testgitdir3")
        os.chdir("../testgitdir3")
        cmd_stdout("git init")
        cmd_stdout("git config core.sparsecheckout true")
        cmd_stdout("git remote add origin ../testgitdir.git")
        make_file(".git/info/sparse-checkout","xxx\n")
        cmd_stdout("git pull origin master")

        self.assertEqual("xxx\n",cmd_stdout("ls"))
        self.assertEqual("""\
goodbye1.txt
goodbye2.txt
xxx/hello1.txt
xxx/hello2.txt
"""
                         ,cmd_stdout("git ls-files"))


    def test_reset1(self):

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

        self.assertEqual("""\
diff --git a/hello.txt b/hello.txt
index 47ca7f2..d3bbad9 100644
--- a/hello.txt
+++ b/hello.txt
@@ -1,2 +1,3 @@
 hello, world
 goodby japan
+goodby america
"""
                         ,cmd_stdout("git diff"))
                         
        cmd_stdout("git add hello.txt")
        cmd_stdout("git reset --hard")

        self.assertEqual("""\
hello, world
goodby japan
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("",
                         cmd_stdout("git diff"))


    def test_reset1(self):

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

        self.assertEqual("""\
diff --git a/hello.txt b/hello.txt
index 47ca7f2..d3bbad9 100644
--- a/hello.txt
+++ b/hello.txt
@@ -1,2 +1,3 @@
 hello, world
 goodby japan
+goodby america
"""
                         ,cmd_stdout("git diff"))
                         
        cmd_stdout("git add hello.txt")
        cmd_stdout("git reset --hard")

        self.assertEqual("""\
hello, world
goodby japan
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("",
                         cmd_stdout("git diff"))


    def test_reset2(self):

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
        cmd_stdout("git reset --mixed")

        self.assertEqual("""\
hello, world
goodby japan
goodby america
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual("""\
diff --git a/hello.txt b/hello.txt
index 47ca7f2..d3bbad9 100644
--- a/hello.txt
+++ b/hello.txt
@@ -1,2 +1,3 @@
 hello, world
 goodby japan
+goodby america
"""
                         ,cmd_stdout("git diff"))



    def test_reset3(self):

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
        cmd_stdout('git reset b3db10b --hard')

        self.assertEqual("""\
hello, world
goodby japan
"""
                         ,cmd_stdout("cat hello.txt"))

        self.assertEqual(""
                         ,cmd_stdout("git diff"))

        self.assertEqual("""\
* b3db10b B
* 70809e4 A
"""
                         ,cmd_stdout("git log --graph --abbrev-commit --oneline"))





if __name__ == "__main__":
    unittest.main()


    
