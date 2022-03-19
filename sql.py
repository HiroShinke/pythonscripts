

import sqlite3


def main():

    db = sqlite3.connect("test.db")
    c = db.cursor()
    
    c.execute("""\n

create table if not exists Person (
    name Char,
    age  Interger
)

""")

    c.execute("""\n

create table if not exists Address (
    name Char,
    address Char
)

""")

    c.execute("delete from Person")
    c.execute("delete from Address")
    
    c.execute("insert into Person values(?,?)", ("alice", 12))
    c.execute("insert into Person values(?,?)", ("bob",   11))
    c.execute("insert into Person values(?,?)", ("cathy", 10))

    c.execute("insert into Address values(?,?)", ("alice", "alabama"))
    c.execute("insert into Address values(?,?)", ("bob",   "brazil"))
    c.execute("insert into Address values(?,?)", ("cathy", "canada"))

    query(c,"select * from Person")
    query(c,"select * from Person order by age")
    query(c,"select * from Person order by (age  + 1)")
    query(c,"select * from Address")
    query(c,"select * from Person, Address where Person.name = Address.name")
          
    
    db.commit()

    
def query(c,q):
    ret = c.execute(q)
    
    print(f"ret = {ret}")
    for x in ret:
        print(f"x = {x}")
    
if __name__ == "__main__":
    main()

    





