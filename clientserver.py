

# for server
import random

# for client
import contextlib
import math
import socket
import time
from threading import Thread

WARMER = 'Warmer'
COLDER = 'Colder'
UNSURE = 'Unsure'
CORRECT = 'Correct'


class EOFError(Exception):
    pass

class ConnectionBase:
    def __init__(self, connection):
        self.connection = connection
        self.file = connection.makefile('rb')

    def send(self, command):
        line = command + '\n'
        data = line.encode()
        self.connection.send(data)

    def receive(self):
        line = self.file.readline()
        if not line:
            raise EOFError('Connection closed')
        return line[:-1].decode()


class UnknownCommandError(Exception):
    pass

###### Server Code

class Session(ConnectionBase):
    def __init__(self, *args):
        super().__init__(*args)
        self._clear_state(None, None)

    def _clear_state(self, lower, upper):
        self.lower = lower
        self.upper = upper
        self.secret = None
        self.guesses = []

    def loop(self):
        while command := self.receive():
            parts = command.split(' ')
            match parts:
                case ['PARAMS', _, _]:
                    self.set_params(parts)
                case ['NUMBER']:
                    self.send_number()
                case ['REPORT', _]:
                    self.receive_report(parts)
                case _:
                    raise UnknownCommandError(command)

    def set_params(self,parts):
        match parts:
            case [_,l,u]:
                self._clear_state(int(l),int(u))

    def next_guess(self):
        if self.secret is not None:
            return self.secret

        while True:
            guess = random.randint(self.lower, self.upper)
            if guess not in self.guesses:
                return guess

    def send_number(self):
        guess = self.next_guess()
        self.guesses.append(guess)
        self.send(format(guess))

    def receive_report(self, parts):
        match parts:
            case [_, decision]:
                last = self.guesses[-1]
                if decision == CORRECT:
                    self.secret = last

                print(f'Server: {last} is {decision}')


#### Client code ######

class Client(ConnectionBase):

    def __init__(self, *args):
        super().__init__(*args)
        self._clear_state()

    def _clear_state(self):
        self.secret = None
        self.last_distance = None

    @contextlib.contextmanager
    def session(self, lower, upper, secret):
        print(f'Guess a number between {lower} and {upper}!'
              f' Shhhhh, it\'s {secret}.')
        self.secret = secret
        self.send(f'PARAMS {lower} {upper}')
        try:
            yield
        finally:
            self._clear_state()
            self.send('PARAMS 0 -1')

    def request_numbers(self, count):
        for _ in range(count):
            self.send('NUMBER')
            data = self.receive()
            yield int(data)
            if self.last_distance == 0:
                return

    def report_outcome(self, number):
        new_distance = math.fabs(number - self.secret)
        decision = UNSURE
                 
        if new_distance == 0:
            decision = CORRECT
        elif self.last_distance is None:
            pass
        elif new_distance < self.last_distance:
            decision = WARMER
        elif new_distance > self.last_distance:
            decision = COLDER
            
        self.last_distance = new_distance

        self.send(f'REPORT {decision}')
        return decision


#### Server Thread

def handle_connection(connection):
    with connection:
        session = Session(connection)
        try:
            session.loop()
        except EOFError:
            pass

def run_server(address):
    print("Server thread start")
    with socket.socket() as listener:
        listener.bind(address)
        listener.listen()
        print("Server lesten")
        while True:
            connection, _ = listener.accept()
            print(f"Server start session: connection = {connection}")
            thread = Thread(target = handle_connection,
                            args = (connection,),
                            daemon = True)
            thread.start()

def run_client(address):
    with socket.create_connection(address) as connection:
        client = Client(connection)

        with client.session(1, 5, 3):
            results = [(x, client.report_outcome(x))
                       for x in client.request_numbers(5)]

        with client.session(10, 15, 12):
            for number in client.request_numbers(5):
                outcome = client.report_outcome(number)
                results.append((number, outcome))

        return results
        
def main():
    address = ('127.0.0.1', 1234)

    server_thread = Thread(
        target = run_server, args = (address,), daemon=True)
    server_thread.start()

    # time.sleep(1)

    results = run_client(address)
    for number, outcome in results:
        print(f"Client: {number} is {outcome}")


if __name__ == "__main__":
    main()

