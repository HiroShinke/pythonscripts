

import sys
from pathlib import Path
import argparse
import re


def do_path(path,pred):
    if pred(path):
        print(path)
    if path.is_dir():
        do_dir(path,pred)

def do_dir(path,pred):
    for x in path.iterdir():
        do_path(x,pred)

def pred_and(pre1,pre2):
    def helper(path):
        return pre1(path) and pre2(path)
    return helper
        
def pre_true(path):
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target",action='append')
    parser.add_argument("-name" ,type=str,  action='store')    
    parser.add_argument("-type" ,type=str,  action='store')    
    args = parser.parse_args()

    pre = pre_true

    if args.name:
        pat = re.compile(args.name)
        def pre_name(path):
            #print(f'pre_name: {pat.search(path.name)}')
            return pat.search(path.name)
        pre = pred_and(pre,pre_name)

    if args.type == "f":
        pre = pred_and(pre,lambda path: path.is_file())
    if args.type == "d":
        pre = pred_and(pre,lambda path: path.is_dir())
    
    for f in args.target:
        path = Path(f)
        do_path(path,pre)

if __name__ == "__main__":
    main()



    
