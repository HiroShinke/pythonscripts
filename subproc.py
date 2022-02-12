

import subprocess

procs = []

#### run parallel 

for i in range(10):
    proc = subprocess.Popen(
        ['cat'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    proc.stdin.write(bytes(f'write input to {i}','utf-8'))
    proc.stdin.flush()
    procs.append(proc)

for p in procs:
    out,_ = p.communicate()
    print(out)


#### making pipeline

proc0 = subprocess.Popen(
    ['cat'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE
)

proc1 = subprocess.Popen(
    ['cat','-n'],
    stdin=proc0.stdout,
    stdout=subprocess.PIPE
)

proc2 = subprocess.Popen(
    ['cat','-n'],
    stdin=proc1.stdout,
    stdout=subprocess.PIPE
)

proc0.stdin.write(b'write input to proc0')
proc0.stdin.close()

proc0.stdout.close()
proc0.stdout = None
proc1.stdout.close()
proc1.stdout = None

xxx, _= proc2.communicate()
print(xxx)




