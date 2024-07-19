from flask import Flask, render_template
from flask_socketio import SocketIO, send
import subprocess

app = Flask(__name__, static_folder='public')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return "WebSocket server is running!"

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    global shell
    shell = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    def read_stdout():
        for line in iter(shell.stdout.readline, ''):
            socketio.send(line)
    def read_stderr():
        for line in iter(shell.stderr.readline, ''):
            socketio.send(f'ERROR: {line}')
    socketio.start_background_task(read_stdout)
    socketio.start_background_task(read_stderr)

@socketio.on('message')
def handle_message(message):
    print(f'Message received: {message}')
    send(f'> {message}\n')
    shell.stdin.write(f'{message}\n')
    shell.stdin.flush()

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    shell.kill()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000)


