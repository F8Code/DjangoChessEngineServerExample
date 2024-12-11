import subprocess
from queue import Queue
from threading import Thread
from django.http import HttpResponse
from rest_framework.decorators import api_view
import time

is_ready_ongoing = False

process = subprocess.Popen(
    ['/app/stockfish/stockfish'], #relative path to the stockfish engine
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True,
    bufsize=1,
)    

output_queue = Queue()

def read_engine_output(process):
    while True:
        line = process.stdout.readline().strip()
        if line:
            output_queue.put(line)
            print(f"Engine: {line}")

engine_thread = Thread(target=read_engine_output, args=(process,))
engine_thread.daemon = True
engine_thread.start()

process.stdin.write('isready\n')
process.stdin.flush()
while True:
    line = output_queue.get()
    if line == 'readyok':
        break

@api_view(['POST'])
def ucinewgame(request):
    process.stdin.write('ucinewgame\n')
    process.stdin.flush()

    return HttpResponse('')

@api_view(['GET'])
def isready(request):
    if is_ready_ongoing:
        return HttpResponse('Engine not responding after restart.', status=500)
    
    def restart_engine():
        global process, engine_thread, output_queue
        try:
            process.stdin.write('quit\n')
            process.stdin.flush()
            process.terminate()
            process.wait()
        except Exception as e:
            print(f"Error terminating engine: {e}")

        process = subprocess.Popen(
            ['/app/stockfish/stockfish'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
        )
        output_queue = Queue()

        engine_thread = Thread(target=read_engine_output, args=(process,))
        engine_thread.daemon = True
        engine_thread.start()

    def wait_for_readyok(timeout):
        process.stdin.write('isready\n')
        process.stdin.flush()
        start_time = time.time()
        while True:
            line = output_queue.get()
            if line == 'readyok':
                return True
            print(f"{time.time() - start_time}, {timeout}")
            if time.time() - start_time > timeout:
                return False

    try:
        is_ready_ongoing = True
        if wait_for_readyok(5):
            is_ready_ongoing = False
            return HttpResponse('readyok\n')

        restart_engine()
        if wait_for_readyok(10):
            is_ready_ongoing = False
            return HttpResponse('readyok\n')

        is_ready_ongoing = False
        return HttpResponse('Engine not responding after restart.', status=500)
    except Exception as e:
            print(f"Error in engine: {e}")

@api_view(['POST'])
def position(request):
    position_data = request.data.get('position', '')

    process.stdin.write('position fen ' + position_data + '\n')
    process.stdin.flush()

    return HttpResponse('')

@api_view(['POST'])
def go(request):
    parameters = request.data.get('parameters', '')

    process.stdin.write('go ' + parameters + '\n')
    process.stdin.flush()

    response = ''
    while True:
        line = output_queue.get()
        response += line + '\n'
        if 'bestmove' in line:
            break

    return HttpResponse(response)

@api_view(['POST'])
def stop(request):
    process.stdin.write('stop\n')
    process.stdin.flush()

    response = ''
    while True:
        line = output_queue.get()
        response += line + '\n'
        if 'bestmove' in line:
            break

    return HttpResponse(response)

@api_view(['POST'])
def quit(request):
    process.stdin.write('quit\n')
    process.stdin.flush()

    return HttpResponse('')

@api_view(['POST'])
def chat(request):
    chatData = request.data.get('chat', '')
    process.stdin.write(chatData + '\n')
    process.stdin.flush()

    if not any(cmd in chatData for cmd in ['stop', 'go']):
        process.stdin.write('isready\n')
        process.stdin.flush()

    response = ''
    while True:
        line = output_queue.get()

        if line == 'readyok':
            if 'isready' in chatData:
                response += line + '\n'
            break

        response += line + '\n'

        if 'bestmove' in line:
            break

    return HttpResponse(response)