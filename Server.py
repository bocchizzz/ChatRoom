import socket
import json
import asyncio

###type: text, image, login, logout, user_list, create_room, join_room
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
        self.users: set = set()
        self.creator = creator

    # def Add(self, user: User):
    #     self.users.append(user)
    #
    # def Remove(self, user):
    #     self.users.remove(user)


class Server:
    def __init__(self, ip, port, max_user):
        self.users: dict = {}
        self.rooms: dict[str, Room] = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen(max_user)
        self.server.setblocking(False)
        self.loop: asyncio.AbstractEventLoop

    async def broadcast(self, client_name, data_dict):
        """
        广播消息
        """
        bytes_data = json.dumps(data_dict).encode('utf-8')
        for name, conn in self.users.items():
            if name != client_name:
                try:
                    await self.loop.sock_sendall(conn, bytes_data)
                except Exception as e:
                    print(f"Broadcast error to {name}: {e}")

    async def send_to_user(self, to_id, msg):
        """发送给指定用户"""
        if to_id in self.users:
            bytes_data = json.dumps(msg).encode('utf-8')
            try:
                await self.loop.sock_sendall(self.users[to_id], bytes_data)
            except Exception as e:
                print(f"Send error to {to_id}: {e}")

    async def join_room(self, room_name, user, inviter):
        msg = json.loads(msg_template)
        msg['type'] = 'join_room'
        msg['to_id'] = user
        msg['from_id'] = inviter
        msg['content'] = room_name
        self.rooms[room_name].users.add(user)
        await self.send_to_user(user, msg)

    async def get_allusers(self, sock, client_name):
        online_users = [name for name in self.users.keys() if name != client_name]

        if online_users:
            data = json.loads(msg_template)
            data['type'] = 'user_list'
            data['to_id'] = client_name
            data['from_id'] = online_users

            raw_data = json.dumps(data).encode('utf-8')
            await self.loop.sock_sendall(sock, raw_data)

    async def handle(self, client_sock):
        buffer = ""
        decoder = json.JSONDecoder()
        current_user_name = None  # 记录当前连接的用户名

        try:
            while True:
                # 接收数据块
                raw_chunk = await self.loop.sock_recv(client_sock, 4096)
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

                        await self.process_message(data, client_sock, current_user_name)

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
                await self.broadcast(current_user_name, logout_msg)

            client_sock.close()

    async def process_message(self, msg, client_sock, current_user_name):
        """
        处理单条完整的 JSON 消息
        """
        msg_type = msg.get('type')

        if msg_type == 'login':
            client_name = msg['from_id']
            self.users[client_name] = client_sock
            print(f"User {client_name} logged in")

            # 广播登录
            await self.broadcast(client_name, msg)

        elif msg_type == 'logout':
            if current_user_name:
                await self.broadcast(current_user_name, msg)

        elif msg_type in ['text', 'image', 'file_header', 'file_chunk', 'file_finish']:
            recipient_id = msg['to_id']
            if msg['private']:
                await self.send_to_user(recipient_id, msg)
            else:
                if recipient_id in self.rooms.keys():
                    for user in self.rooms[recipient_id].users:
                        if user != msg['from_id']:
                            await self.send_to_user(user, msg)

        elif msg_type in 'create_room':
            room_name = msg['content']
            users = msg['to_id']
            creator = msg['from_id']
            room = Room(room_name, creator)
            self.rooms[room_name] = room
            for user in users:
                await self.join_room(room_name, user, creator)

    async def run(self):
        self.loop = asyncio.get_running_loop()
        print("Server started on port 8888...")
        while True:
            client_sock, addr = await self.loop.sock_accept(self.server)
            print(f"Connection from {addr}")
            client_sock.setblocking(False)
            await self.get_allusers(client_sock, '')
            self.loop.create_task(self.handle(client_sock))


if __name__ == '__main__':
    server = Server('localhost', 8888, 10)
    asyncio.run(server.run())
