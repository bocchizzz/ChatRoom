import socket, json, threading, queue, time

msg_model = """{
    "type": "message",
    "from_id": "UserA", 
    "to_id": "UserB",
    "content": "你好，这是私信"
}"""
client = socket.socket()
client.connect(('localhost', 8888))
login_msg = json.loads(msg_model)
login_msg['type'] = "login"
login_msg['from_id'] = 'ccc'
client.send(json.dumps(login_msg).encode('utf-8'))
time.sleep(1)

while 1:
    msg = '111'
    send_msg = json.loads(msg_model)
    send_msg['from_id'] = 'ccc'
    send_msg['to_id'] = 'ddd'
    send_msg["content"] = msg
    client.send(json.dumps(send_msg).encode('utf-8'))
    time.sleep(1)
    # data = client.recv(1024).decode('utf-8')
    # print(data)