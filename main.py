from flask import Flask, render_template, request
from flask_socketio import SocketIO, send
import random, string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

clients = {}
default_key = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

def xor_crypt(text, key):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))

@app.route('/')
def index():
    return render_template('index.html', key=default_key)

@socketio.on('join')
def handle_join(data):
    clients[request.sid] = data['name']
    send(f"[sys] {data['name']} joined the chat.", broadcast=True)

@socketio.on('message')
def handle_message(data):
    name = clients.get(request.sid, "Unknown")
    decrypted = xor_crypt(data['msg'], data['key'])
    print(f"[{name}] {decrypted}")
    for sid in clients:
        if sid != request.sid:
            enc = xor_crypt(f"{name}: {decrypted}", data['key'])
            socketio.emit("message", enc, to=sid)

@socketio.on('disconnect')
def handle_disconnect():
    name = clients.get(request.sid, "Unknown")
    send(f"[sys] {name} left the chat.", broadcast=True)
    clients.pop(request.sid, None)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
