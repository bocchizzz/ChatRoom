import base64
import os, socket, json, threading
from PySide6.QtCore import QThread, Signal, QObject

msg_template = """{
    "type": "message", 
    "private": false,
    "from_id": "UserA", 
    "to_id": "UserB",
    "content": ""
}"""


class SendWorker(QThread):
    finished = Signal(str, str, bool)

    def __init__(self, sock, lock, file_path, to_id, from_id, is_private):
        super().__init__()
        self.sock = sock
        self.lock = lock  # 接收共享锁
        self.file_path = file_path
        self.to_id = to_id
        self.from_id = from_id
        self.is_private = is_private
        self.chunk_size = 512 * 1024  # 512KB 分片大小

    def run(self):
        try:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError("文件不存在")

            file_name = os.path.basename(self.file_path)
            file_size = os.path.getsize(self.file_path)

            # 发送文件头
            header = {
                'type': 'file_header',
                'to_id': self.to_id,
                'from_id': self.from_id,
                'private': self.is_private,
                'filename': file_name,
                'filesize': file_size,
            }
            self.send_safe(header)

            # 循环发送分片
            sent_size = 0
            with open(self.file_path, 'rb') as f:
                while True:
                    chunk_data = f.read(self.chunk_size)
                    if not chunk_data:
                        break

                    b64_str = base64.b64encode(chunk_data).decode('utf-8')
                    chunk_msg = {
                        'type': 'file_chunk',
                        'to_id': self.to_id,
                        'from_id': self.from_id,
                        'private': self.is_private,
                        'content': b64_str,
                        'filename': file_name
                    }

                    # 发送分片 (需要加锁)
                    self.send_safe(chunk_msg)

                    # 更新进度
                    # sent_size += len(chunk_data)
                    # progress = int((sent_size / file_size) * 100)
                    # print(progress)
                    # self.progress_signal.emit(progress)

                    # 可选：极短暂休眠防止占满带宽导致心跳包发不出去
                    # self.msleep(5)

            # 发送结束包
            finish_msg = {
                'type': 'file_finish',
                'filename': file_name,
                'private': self.is_private,
                'to_id': self.to_id,
                'from_id': self.from_id
            }
            self.send_safe(finish_msg)
            self.finished.emit(file_name, self.to_id, self.is_private)

        except Exception as e:
            print(str(e))
            return

    def send_safe(self, data):
        """线程安全的发送辅助函数"""
        json_bytes = json.dumps(data).encode('utf-8')

        with self.lock:
            self.sock.send(json_bytes)


class Listener(QObject):
    file_finished = Signal(str, str, bool)

    def __init__(self, ip, port, name):
        super().__init__()
        self.name = name
        self.isrun = True
        self.listener = socket.socket()
        self.listener.connect((ip, port))
        self.send_lock = threading.Lock()

        self.worker = None

    def send_login(self, name):
        # 登录
        self.name = name
        self.send_msg(to_id="All", msg_type="login", content="")

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

    def send_msg(self, content, msg_type, to_id, is_private=True):
        if msg_type == 'file':
            if not content:
                print("Error: Send file but no path provided.")
                return

            self.worker = SendWorker(
                self.listener,
                self.send_lock,
                content,
                to_id,
                self.name,
                is_private
            )

            self.worker.finished.connect(self.file_finished.emit)

            # 启动线程
            self.worker.start()

        else:
            msg = json.loads(msg_template)
            msg['type'] = msg_type
            msg['content'] = content
            msg['to_id'] = to_id
            msg['from_id'] = self.name
            msg['private'] = is_private

            try:
                json_bytes = json.dumps(msg).encode('utf-8')

                with self.send_lock:
                    self.listener.sendall(json_bytes)

            except Exception as e:
                print(f"Send text error: {e}")

    def close(self):
        self.listener.close()
        self.isrun = False
