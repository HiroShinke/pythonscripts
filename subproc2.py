

import subprocess


cmd = [ "ls", "-l" ]
proc = subprocess.run(cmd, capture_output=True,text=True)

lines = proc.stdout.splitlines()
for i,l in enumerate(lines):
    print(f"1:{i}:{l}")

print(f"return_code = {proc.returncode}")

proc = subprocess.run(cmd, stdout=subprocess.PIPE,text=True)

lines = proc.stdout.splitlines()
for i,l in enumerate(lines):
    print(f"2:{i}:{l}")

print(f"return_code = {proc.returncode}")

pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE,text=True)

for i,l in enumerate(pipe.stdout.readlines()):
    print(f"3:{i}:{l}",end="")

ret = pipe.wait()
print(f"ret = {ret}")
print(f"return_code = {pipe.returncode}")
