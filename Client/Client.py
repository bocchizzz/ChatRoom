import json
import sys
import threading
from module.Login import LoginWindow
from module.Listener import Listener
from module.ChatArea import ChatArea
from module.Sidebar import Sidebar
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

class MainWindow(QWidget):
    closed = Signal()
    sent = Signal(str, str, str)

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
        self.chat_windows = {}

        self.sidebar.contactClicked.connect(self.switch_chat)

    def switch_chat(self, name):
        # 聊天窗口还没创建过
        self.add_chatarea(name)

        target_widget = self.chat_windows[name]

        # 切换显示
        self.stacked_widget.setCurrentWidget(target_widget)

    def add_chatarea(self, name):
        if name not in self.chat_windows:
            print(f"创建新窗口: {name}")
            chat_area = ChatArea(chat_name=name)
            self.stacked_widget.addWidget(chat_area)
            self.chat_windows[name] = chat_area
            chat_area.sent.connect(self.send_msg)

    def send_msg(self, text, chat_name, chat_type):
        self.sent.emit(text, chat_name, chat_type)

    def display_msg(self, message):
        if message['from_id'] in self.chat_windows:
            chat_area = self.chat_windows[message['from_id']]
            msg_type = message['type']
            chat_area.add_message(message['content'], is_me=False, msg_type=msg_type)

    def update_users(self, user, islog):
        if islog:
            self.add_chatarea(user)
            self.sidebar.add_user(user)
        else:
            if user in self.chat_windows.keys():
                self.stacked_widget.removeWidget(self.chat_windows[user])
                self.chat_windows.pop(user)
            self.sidebar.remove_user(user)

    def closeEvent(self, event):
        self.closed.emit()


class Client(QObject):
    # 用于接收消息的信号，参数类型为 dict
    msg_received = Signal(dict)
    # 用于用户登录/登出的信号，参数类型为 str(用户名), bool(是否登录)
    user_status_changed = Signal(str, bool)

    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
        self.name = ''
        self.Window = LoginWindow()
        self.Window.show()
        self.Window.closed.connect(self.login)

    def login(self, name, log):
        if log:
            self.name = name
            self.init_main()
            self.run()

    def init_main(self):
        self.Listener = Listener(self.ip, self.port, self.name)
        self.tread_receive = threading.Thread(target=self.Listener.receive_msg, args=(self.handle_receive,))

        # 设置 QFluentWidgets 的主题
        setTheme(Theme.LIGHT)
        setThemeColor(THEME_COLOR)  # 设置全局主题色
        self.Window = MainWindow()

        self.Window.closed.connect(self.close)
        self.Window.sent.connect(self.send_msg)

        # 当 msg_received 发射时，主线程会自动执行 self.Window.display_msg
        self.msg_received.connect(self.Window.display_msg)
        # 当 user_status_changed 发射时，主线程会自动执行 self.Window.update_users
        self.user_status_changed.connect(self.Window.update_users)

    def run(self):
        self.tread_receive.start()
        self.Window.show()

    def handle_receive(self, data):
        if data['type'] == 'text' or data['type'] == 'image':
            self.msg_received.emit(data)

        elif data['type'] == 'user_list':
            # 遍历列表，批量添加用户
            for user in data['from_id']:
                self.user_status_changed.emit(user, True)

        elif data['type'] == 'login':
            self.user_status_changed.emit(data['from_id'], True)

        elif data['type'] == 'logout':
            self.user_status_changed.emit(data['from_id'], False)

    def send_msg(self, content, chat_name, chat_type):
        self.Listener.send_msg(content, chat_type, chat_name)

    def close(self):
        self.Listener.send_msg("", "logout", "All")
        self.Listener.close()


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)

    client = Client('localhost', 8888)

    sys.exit(app.exec())
