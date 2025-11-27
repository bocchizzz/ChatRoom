import random
import sys, threading, os, base64
from module.Login import LoginWindow
from module.Listener import Listener
from module.ChatArea import ChatArea
from module.Sidebar import Sidebar
from module.Room import CreateRoom
from PySide6.QtCore import Qt, QSize, Signal, QObject
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout,
                               QListWidget, QListWidgetItem, QFrame, QSpacerItem,
                               QSizePolicy, QScrollArea, QAbstractItemView, QStackedWidget)

from qfluentwidgets import (setTheme, Theme, setThemeColor, TextEdit, PrimaryPushButton,
                            StrongBodyLabel, BodyLabel, SearchLineEdit, AvatarWidget,
                            TransparentToolButton, FluentIcon)

# --- 配置颜色 ---
THEME_COLOR = '#0099FF'
BUBBLE_SELF_COLOR = '#E5F5FF'  # 自己发送的气泡背景色
BUBBLE_OTHER_COLOR = '#F2F2F2'  # 别人发送的气泡背景色
# 接收文件保存地址
SAVE_DIR = "downloads"


class MainWindow(QWidget):
    closed = Signal()
    sent = Signal(str, str, str, bool)
    createRoom = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatRoom")
        self.resize(900, 650)

        self.h_layout = QHBoxLayout(self)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(0)

        # 左侧边栏
        self.sidebar = Sidebar()
        self.h_layout.addWidget(self.sidebar)

        # 右侧堆叠窗口
        self.stacked_widget = QStackedWidget()
        self.h_layout.addWidget(self.stacked_widget)

        # 聊天窗口缓存字典
        self.user_chat_windows = {}
        self.room_chat_windows = {}

        # 产生自己的头像
        avatar_list = os.listdir('asset/')
        self.avatar = 'asset/' + random.choice(avatar_list)

        self.sidebar.userClicked.connect(self.switch_chat)
        self.sidebar.roomClicked.connect(self.switch_chat)
        self.sidebar.creatRoom.connect(self.createRoom.emit)

    def log_in(self, online_users):
        log_window = LoginWindow(online_users, self)
        if log_window.exec():
            return log_window.textEdit.text()

    def switch_chat(self, name, isroom):
        # 聊天窗口还没创建过
        self.add_chatarea(name)
        if isroom:
            target_widget = self.room_chat_windows[name]
        else:
            target_widget = self.user_chat_windows[name]

        # 切换显示
        self.stacked_widget.setCurrentWidget(target_widget)

    def add_chatarea(self, name, other_avatar='asset/w1.png'):
        if name not in self.user_chat_windows:
            chat_area = ChatArea(name, other_avatar, self.avatar)
            self.stacked_widget.addWidget(chat_area)
            self.user_chat_windows[name] = chat_area
            chat_area.sent.connect(self.send_msg)

    def add_room_chatarea(self, name, other_avatar='asset/w1.png'):
        if name not in self.room_chat_windows:
            chat_area = ChatArea(name, other_avatar, self.avatar, isroom=True)
            self.stacked_widget.addWidget(chat_area)
            self.room_chat_windows[name] = chat_area
            chat_area.sent.connect(self.send_msg)

    def send_msg(self, text, chat_name, chat_type, is_private):
        self.sent.emit(text, chat_name, chat_type, is_private)

    def display_msg(self, message, isroom):
        if isroom:
            if message['to_id'] in self.room_chat_windows.keys():
                chat_area = self.room_chat_windows[message['to_id']]
                msg_type = message['type']
                chat_area.add_message(message['content'], message['from_id'], is_me=False, msg_type=msg_type)
        else:
            if message['from_id'] in self.user_chat_windows.keys():
                chat_area = self.user_chat_windows[message['from_id']]
                msg_type = message['type']
                chat_area.add_message(message['content'], message['from_id'], is_me=False, msg_type=msg_type)

    def update_users(self, user, islog):
        if islog:
            avatar_list = os.listdir('asset/')
            avatar = 'asset/' + random.choice(avatar_list)
            self.add_chatarea(user, avatar)
            self.sidebar.add_user(user, avatar)
        else:
            if user in self.user_chat_windows.keys():
                self.stacked_widget.removeWidget(self.user_chat_windows[user])
                self.user_chat_windows.pop(user)
            self.sidebar.remove_user(user)

    def update_rooms(self, room_name):
        self.sidebar.add_room(room_name)
        self.add_room_chatarea(room_name)

    def create_room_box(self, user, room):
        create_room_box = CreateRoom(room, user, self)
        if create_room_box.exec():
            return create_room_box.room_info

    def closeEvent(self, event):
        self.closed.emit()


class Client(QObject):
    # 用于接收消息的信号，参数类型为 dict
    msg_received = Signal(dict, bool)
    # 用于用户登录/登出的信号，参数类型为 str(用户名), bool(是否登录)
    user_status_changed = Signal(str, bool)
    room_status_changed = Signal(str)

    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
        self.name = ''

        self.receiving_files = {}  # 接收文件的文件句柄
        self.online_users: set = set()  # 存储在线用户，主要防止重名
        self.online_rooms: set = set()  # 存储在线群聊，主要防止重名

        self.Listener = Listener(self.ip, self.port, self.name)
        self.tread_receive = threading.Thread(target=self.Listener.receive_msg, args=(self.handle_receive,))

        # 设置 QFluentWidgets 的主题
        setTheme(Theme.LIGHT)
        setThemeColor(THEME_COLOR)  # 设置全局主题色
        self.Window = MainWindow()

        self.Window.closed.connect(self.close)
        self.Window.sent.connect(self.send_msg)
        self.Window.createRoom.connect(self.create_room)

        self.Listener.file_finished.connect(self.finished_send_file)

        # 当 msg_received 发射时，主线程会自动执行 self.Window.display_msg
        self.msg_received.connect(self.Window.display_msg)
        # 当 user_status_changed 发射时，主线程会自动执行 self.Window.update_users
        self.user_status_changed.connect(self.Window.update_users)
        # 当 user_status_changed 发射时，主线程会自动执行 self.Window.update_room
        self.room_status_changed.connect(self.Window.update_rooms)


    def run(self):
        self.tread_receive.start()
        self.Window.show()
        name = self.Window.log_in(self.online_users)
        if name:
            self.name = name
            self.Listener.send_login(name)
        else:
            self.Window.close()


    def handle_receive(self, msg):
        if msg['type'] in ['text', 'image', 'file_header', 'file_chunk', 'file_finish']:
            self.receive_msg(msg)

        elif msg['type'] == 'user_list':
            # 遍历列表，批量添加用户
            for user in msg['from_id']:
                self.user_status_changed.emit(user, True)
                self.online_users.add(user)

        elif msg['type'] == 'login':
            self.user_status_changed.emit(msg['from_id'], True)
            self.online_users.add(msg['from_id'])

        elif msg['type'] == 'logout':
            self.user_status_changed.emit(msg['from_id'], False)
            self.online_users.remove(msg['from_id'])

        elif msg['type'] == 'join_room':
            self.room_status_changed.emit(msg['content'])

    def send_msg(self, content, chat_name, chat_type, is_private):
        self.Listener.send_msg(content, chat_type, chat_name, not is_private)

    def receive_msg(self, msg: dict):
        msg_type = msg.get('type')
        from_id = msg.get('from_id')
        filename = msg.get('filename')
        isroom = not msg.get('private')

        file_key = filename
        # 防止同名文件冲突
        # if os.path.exists(f'downloads/{filename}'):
        #     i = 1
        #     while 1:
        #         if not os.path.exists(f'downloads/{filename}'):
        #             file_key = f"{filename}({i})"
        #             break

        # 收到文件头：准备接收
        if msg_type == 'file_header':
            print(f"开始接收文件: {filename}, 大小: {msg['filesize']}")

            if not os.path.exists(SAVE_DIR):
                os.makedirs(SAVE_DIR)
            save_path = os.path.join(SAVE_DIR, filename)

            try:
                f = open(save_path, 'wb')
                self.receiving_files[file_key] = f

                # 显示文件接收气泡
                msg['type'] = 'file'
                msg['content'] = f'正在接收文件：{file_key}'
                self.msg_received.emit(msg, isroom)

            except Exception as e:
                print(f"文件创建失败: {e}")

        # 接收写入文件分片
        elif msg_type == 'file_chunk':
            if file_key in self.receiving_files:
                f = self.receiving_files[file_key]
                # 解码 Base64 并写入
                try:
                    chunk_data = base64.b64decode(msg['content'])
                    f.write(chunk_data)
                except Exception as e:
                    print(f"写入分片失败: {e}")

        # 收到文件结束
        elif msg_type == 'file_finish':
            if file_key in self.receiving_files:
                f = self.receiving_files[file_key]
                f.close()
                del self.receiving_files[file_key]
                msg['type'] = 'file'
                msg['content'] = f'文件接收完成：{file_key}'
                self.msg_received.emit(msg, isroom)
                print(f"文件接收完成: {filename}")

        elif msg_type in ['text', 'image']:
            self.msg_received.emit(msg, isroom)

    def create_room(self):
        room_info = self.Window.create_room_box(self.online_users, self.online_rooms)
        if room_info:
            room_info['users'].append(self.name)
            self.Listener.send_msg(room_info['name'], 'create_room', room_info['users'])

    def finished_send_file(self, filename, to_id, is_private):
        if is_private:
            self.Window.user_chat_windows[to_id].add_message(f"发送完成: {filename}", is_me=True, msg_type='file')
        else:
            self.Window.room_chat_windows[to_id].add_message(f"发送完成: {filename}", is_me=True, msg_type='file')

    def close(self):
        self.Listener.send_msg("", "logout", "All")
        self.Listener.close()


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)

    client = Client('localhost', 8888)
    client.run()

    sys.exit(app.exec())
