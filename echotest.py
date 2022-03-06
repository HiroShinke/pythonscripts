

import asyncio
import time
import argparse

async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    print(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()

async def tcp_echo_server():
    server = await asyncio.start_server(
        handle_echo, '127.0.0.1', 1234)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 1234)

    print(f'Send: {message!r}')
    writer.write(message.encode())

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()

async def main_async1():
    """ good """
    task = tcp_echo_server()
    asyncio.create_task(task)

    await asyncio.sleep(5)
    await tcp_echo_client("Hello Echo")


async def main_async2():
    """ not so good """
    await tcp_echo_server()
    await tcp_echo_client("Hello Echo")


async def main_async3():
    """ not so good """
    t1 = asyncio.create_task(tcp_echo_server())
    t2 = asyncio.create_task(tcp_echo_client("Hello Echo"))

    await asyncio.gather(t1,t2)
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-type',type=str,action='store')
    args = parser.parse_args()
    
    match args.type:
        case "1":
            asyncio.run(main_async1())            
        case "2":
            asyncio.run(main_async2())            
        case "3":
            asyncio.run(main_async3())            

if __name__ == "__main__":        
    main()
