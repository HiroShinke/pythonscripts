

import json

alice = {
    "name" : "alice",
    "age" : 10,
    "address" : "London"
}

bob = {
    "name" : "bob",
    "age" : 10,
    "address" : "New York"
}

person = [ alice, bob ]

s = json.dumps(person)

print(f"person = {person}")
print(f"s = {s}")

t = json.loads(s)

print(f"person = {person}")
print(f"t = {t}")


with open("test.json","w") as h:
    json.dump(person,h)

with open("test.json","r") as h:
    x = json.load(h)
    print(f"x = {x}")

