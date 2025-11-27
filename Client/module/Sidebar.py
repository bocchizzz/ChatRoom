from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                               QListWidget, QListWidgetItem, QFrame, QAbstractItemView)
from qfluentwidgets import StrongBodyLabel, TransparentToolButton, FluentIcon, ListWidget

THEME_COLOR = '#0099FF'


class UserList(QWidget):
    """
    在线用户或群聊列表
    """
    item_clicked = Signal(str)
    createroom_clicked = Signal()

    def __init__(self, title="在线人数", is_private=True):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 0)
        self.stats_container = QFrame()
        self.stats_container.setFixedHeight(50)
        stats_layout = QHBoxLayout(self.stats_container)

        self.online_label = StrongBodyLabel(title)
        self.count_label = StrongBodyLabel("0")
        self.count_label.setStyleSheet(f"color: {THEME_COLOR};")

        stats_layout.addWidget(self.online_label)
        stats_layout.addStretch(1)
        stats_layout.addWidget(self.count_label)

        if not is_private:
            self.createroom_butn = TransparentToolButton()
            self.createroom_butn.setIcon(FluentIcon.ADD_TO)
            self.createroom_butn.setFixedSize(20, 20)
            self.createroom_butn.clicked.connect(self.createroom_clicked.emit)
            stats_layout.addWidget(self.createroom_butn)

        layout.addWidget(self.stats_container)

        self.contact_list = ListWidget()
        self.contact_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.contact_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.contact_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.contact_list.setFrameShape(QListWidget.NoFrame)
        self.contact_list.setStyleSheet("""
                            QListWidget { background: transparent; border: none; }
                            QListWidget::item { padding: 10px; font-size:16px;}
                            QListWidget::item:hover { background-color: #E6E6E6; border-radius: 5px;}
                            QListWidget::item:selected { background-color: #FFFFFF; color: black; border-radius: 0px; outline: 0px;}
                            QListWidget::item:focus {outline: 0px;}
                        """)
        layout.addWidget(self.contact_list)

        self.contact_list.itemClicked.connect(self.on_item_clicked)

    def add_item(self, item):
        self.contact_list.addItem(item)

    def remove_item(self, name: str):
        items = self.contact_list.findItems(name, Qt.MatchExactly)

        if not items:
            return

        for item in items:
            row = self.contact_list.row(item)
            self.contact_list.takeItem(row)
            del item

        print(f"已移除联系人: {name}")

    def on_item_clicked(self, item):
        self.item_clicked.emit(item.text())


class Sidebar(QWidget):
    """
    左侧边栏：显示在线人数和列表
    """
    userClicked = Signal(str, bool)
    roomClicked = Signal(str, bool)
    creatRoom = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setStyleSheet("background-color: #F2F2F2;")  # 稍微深一点的灰

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 0)

        self.user_list = UserList()
        self.user_list.item_clicked.connect(self.on_item_clicked)

        self.room_list = UserList('加入的房间', False)
        self.room_list.createroom_clicked.connect(self.creatRoom.emit)
        self.room_list.item_clicked.connect(self.on_room_item_clicked)

        layout.addWidget(self.user_list, 1)
        layout.addWidget(self.room_list, 1)
        layout.addStretch(1)  # 底部顶上去

    def add_user(self, name, avatar):
        item = QListWidgetItem(name)
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        item.setIcon(QIcon(avatar))
        self.user_list.add_item(item)

    def add_room(self, name):
        item = QListWidgetItem(name)
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.room_list.add_item(item)

    def remove_user(self, name):
        self.user_list.remove_item(name)

    def on_item_clicked(self, name):
        self.userClicked.emit(name, False)

    def on_room_item_clicked(self, name):
        self.roomClicked.emit(name, True)
