

import dis
from types import CodeType
from bytecode import Instr, Bytecode

def wadd(x,y=1):
    pow_n = 3
    result = (x + y) ** pow_n
    return abs(result)

def print_codetype(c):
    for attr in dir(c):
        if attr.startswith("co_"):
            print(f"{attr} = {c.__getattribute__(attr)}")

def wrap_stores_bytecode(func):

    bytecodes = Bytecode.from_code(func.__code__)

    def wrappStore(x):
        code = [Instr("LOAD_GLOBAL", 'goo'),
                Instr("LOAD_FAST", x),
                Instr("CALL_FUNCTION", 1),
                Instr("STORE_FAST", x)]
        return code

    new_code = []
    
    for inst in bytecodes:
        new_code.append(inst.copy())
        if  inst.name == "STORE_FAST":
            codes = wrappStore(inst.arg)
            new_code.extend(codes)

    return Bytecode(new_code)
    
def wrap_stores_in_function(func):

    bytecode = wrap_stores_bytecode(func)

    fn_code = func.__code__
    bytecode.argnames = fn_code.co_varnames
    argcount = fn_code.co_argcount

    code = bytecode.to_code();
    func.__code__ = code.replace(co_argcount = argcount)

def fix_function(func, payload):
    fn_code = func.__code__
    func.__code__ = fn_code.replace( co_code = payload )

print_codetype(wadd.__code__);
    
payload = wadd.__code__.co_code

# replace BINARY_ADD (0x17) at position #12 with BINARY_SUBTRACT (0x18)
subtract_opcode = dis.opmap['BINARY_SUBTRACT'].to_bytes(1, byteorder='little')
payload = payload[0:12] + subtract_opcode + payload[13:]

dis.dis(wadd)
print(f"wadd = {wadd(3,1)}")

fix_function(wadd,payload)

dis.dis(wadd)
print(f"wadd = {wadd(3,1)}")

def goo(x):
    print(f"goo called: {x}")
    return x + 2

def foo1(a,b,c):
    x = a
    y = b
    z = c
    return (x,y,z)

def foo2(a,b,c):
    x = a
    x = goo(x)
    y = b
    y = goo(y)
    z = c
    z = goo(y)
    return (x,y,z)

print("foo1 dis.dis(foo1)")
dis.dis(foo1)
print("foo2 dis.dis(foo2)")
dis.dis(foo2)


bytecode = Bytecode([Instr("LOAD_NAME", 'print'),
                     Instr("LOAD_CONST", 'Hello World!'),
                     Instr("CALL_FUNCTION", 1),
                     Instr("POP_TOP"),
                     Instr("LOAD_CONST", None),
                     Instr("RETURN_VALUE")])
code = bytecode.to_code()
exec(code)


print_codetype(foo1.__code__);
print()
print()
print_codetype(foo2.__code__);
print()
print()

print(f"ret = {foo1(1,2,3)}");
print(f"ret = {foo2(1,2,3)}");


wrap_stores_in_function(foo1)
    
print("foo1 dis.dis(foo1)")
dis.dis(foo1)

print_codetype(foo1.__code__);
print()
print()

print(f"ret = {foo1(1,2,3)}");


