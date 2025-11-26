import socket
import json
import asyncio

###type: text, image, login, logout, user_list
msg_template = """{
    "type": "message", 
    "private": false,
    "from_id": "UserA", 
    "to_id": "UserB",
    "content": ""
}"""


class Room:
    def __init__(self, name, creator):
        self.name: str = name
        self.users: dict = {}

    # def Add(self, user: User):
    #     self.users.append(user)
    #
    # def Remove(self, user):
    #     self.users.remove(user)


class Server:
    def __init__(self, ip, port, max_user):
        self.users: dict = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen(max_user)
        self.server.setblocking(False)

    async def broadcast(self, client_name, data_dict, loop):
        """
        广播消息
        """
        bytes_data = json.dumps(data_dict).encode('utf-8')
        for name, conn in self.users.items():
            if name != client_name:
                try:
                    await loop.sock_sendall(conn, bytes_data)
                except Exception as e:
                    print(f"Broadcast error to {name}: {e}")

    async def send_to_user(self, to_id, data_dict, loop):
        """发送给指定用户"""
        if to_id in self.users:
            bytes_data = json.dumps(data_dict).encode('utf-8')
            try:
                await loop.sock_sendall(self.users[to_id], bytes_data)
            except Exception as e:
                print(f"Send error to {to_id}: {e}")

    async def get_allusers(self, sock, loop, client_name):
        online_users = [name for name in self.users.keys() if name != client_name]

        if online_users:
            data = json.loads(msg_template)
            data['type'] = 'user_list'
            data['to_id'] = client_name
            data['from_id'] = online_users  # 注意这里 key 最好叫 user_list 配合客户端

            raw_data = json.dumps(data).encode('utf-8')
            await loop.sock_sendall(sock, raw_data)

    async def handle(self, client_sock, loop):
        buffer = ""
        decoder = json.JSONDecoder()
        current_user_name = None  # 记录当前连接的用户名

        try:
            while True:
                # 接收数据块
                raw_chunk = await loop.sock_recv(client_sock, 4096)  # 加大接收缓冲区
                if not raw_chunk:
                    break

                try:
                    buffer += raw_chunk.decode('utf-8')
                except UnicodeDecodeError:
                    continue

                while buffer:
                    buffer = buffer.lstrip()
                    if not buffer:
                        break

                    try:
                        data, idx = decoder.raw_decode(buffer)

                        await self.process_message(data, client_sock, loop, current_user_name)

                        if data.get('type') == 'login':
                            current_user_name = data['from_id']

                        buffer = buffer[idx:]

                    except json.JSONDecodeError:
                        break

        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            # 断开连接后的清理
            if current_user_name and current_user_name in self.users:
                print(f"{current_user_name} disconnected")
                self.users.pop(current_user_name)

                logout_msg = {'type': 'logout', 'from_id': current_user_name}
                await self.broadcast(current_user_name, logout_msg, loop)

            client_sock.close()

    async def process_message(self, data, client_sock, loop, current_user_name):
        """
        处理单条完整的 JSON 消息
        """
        msg_type = data.get('type')

        if msg_type == 'login':
            client_name = data['from_id']
            self.users[client_name] = client_sock
            print(f"User {client_name} logged in")

            # 广播登录
            await self.broadcast(client_name, data, loop)
            # 发送在线列表给自己
            # await self.get_allusers(client_sock, loop, client_name)

        elif msg_type == 'logout':
            if current_user_name:
                await self.broadcast(current_user_name, data, loop)

        elif msg_type in ['text', 'image', 'file_header', 'file_chunk', 'file_finish']:
            recipient_id = data['to_id']
            await self.send_to_user(recipient_id, data, loop)

    async def run(self):
        loop = asyncio.get_running_loop()
        print("Server started on port 8888...")
        while True:
            client_sock, addr = await loop.sock_accept(self.server)
            print(f"Connection from {addr}")
            client_sock.setblocking(False)
            await self.get_allusers(client_sock, loop, '')
            loop.create_task(self.handle(client_sock, loop))


if __name__ == '__main__':
    server = Server('localhost', 8888, 10)
    asyncio.run(server.run())
