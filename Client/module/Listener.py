import socket, json

msg_template = """{
    "type": "message",
    "from_id": "UserA", 
    "to_id": "UserB",
    "content": ""
}"""


class Listener:
    def __init__(self, ip, port, name):
        self.name = name
        self.isrun = True
        self.listener = socket.socket()
        self.listener.connect((ip, port))
        login_msg = json.loads(msg_template)
        login_msg['type'] = "login"
        login_msg['from_id'] = name
        self.listener.send(json.dumps(login_msg).encode('utf-8'))
        self.msg = ""

    def receive_msg(self, handle_func):
        decoder = json.JSONDecoder()
        buffer = ""

        while self.isrun:
            try:
                # 接收数据并拼接到缓冲区
                raw_data = self.listener.recv(4096)
                if not raw_data:
                    break
                buffer += raw_data.decode('utf-8')

                # 循环解析缓冲区中的数据，直到解析不出完整的 JSON 为止
                while buffer:
                    buffer = buffer.lstrip()
                    if not buffer:
                        break
                    try:
                        # obj: 解析出来的 Python 对象
                        # idx: 解析结束的索引位置
                        obj, idx = decoder.raw_decode(buffer)

                        handle_func(obj)

                        buffer = buffer[idx:]

                    except json.JSONDecodeError:
                        break

            except Exception as e:
                print(f"Error in receive_msg: {e}")
                break

        print("stop")

    def send_msg(self, content, msg_type, to_id):
        msg = json.loads(msg_template)
        msg['type'] = msg_type
        msg['content'] = content
        msg['to_id'] = to_id
        msg['from_id'] = self.name
        self.listener.send(json.dumps(msg).encode('utf-8'))

    def close(self):
        self.listener.close()
        self.isrun = False
