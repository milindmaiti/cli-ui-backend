from flask import Flask, request, jsonify
from flask_socketio import SocketIO, send, emit
import paramiko
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
ssh_client = None
ssh_lock = threading.Lock()

@app.route('/connect', methods=['POST'])
def connect_ssh():
    global ssh_client
    data = request.json
    host = data['host']
    username = data['username']
    password = data['password']

    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, username=username, password=password)
        return jsonify({'message': 'SSH connection established'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    if ssh_client:
        send('SSH connection established')
    else:
        send('No SSH connection established')

@socketio.on('message')
def handle_message(msg):
    global ssh_client
    if ssh_client:
        with ssh_lock:
            stdin, stdout, stderr = ssh_client.exec_command(msg)
            output = stdout.read().decode()
            error = stderr.read().decode()
            if output:
                send(output)
            if error:
                send(f'ERROR: {error}')
    else:
        send('No SSH connection established')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
