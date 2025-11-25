from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                               QListWidget, QListWidgetItem, QFrame, QAbstractItemView)
from qfluentwidgets import StrongBodyLabel

THEME_COLOR = '#0099FF'


class UserList(QWidget):
    """
    在线用户或群聊列表
    """
    item_clicked = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 0)
        self.stats_container = QFrame()
        self.stats_container.setFixedHeight(50)
        stats_layout = QHBoxLayout(self.stats_container)

        self.online_label = StrongBodyLabel("在线人数")
        self.count_label = StrongBodyLabel("0")
        self.count_label.setStyleSheet(f"color: {THEME_COLOR};")

        stats_layout.addWidget(self.online_label)
        stats_layout.addStretch(1)
        stats_layout.addWidget(self.count_label)

        layout.addWidget(self.stats_container)

        self.contact_list = QListWidget()
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

    def add_user(self, item):
        self.contact_list.addItem(item)

    def remove_user(self, name: str):
        items = self.contact_list.findItems(name, Qt.MatchExactly)

        if not items:
            print(f"未找到联系人: {name}")
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
    contactClicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setStyleSheet("background-color: #F2F2F2;")  # 稍微深一点的灰

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 0)

        self.user_list = UserList()
        self.user_list.item_clicked.connect(self.on_item_clicked)

        layout.addWidget(self.user_list, 1)
        layout.addStretch(1)  # 底部顶上去

    def add_user(self, name, avatar):
        item = QListWidgetItem(name)
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        item.setIcon(QIcon(avatar))
        self.user_list.add_user(item)

    def remove_user(self, name):
        self.user_list.remove_user(name)

    def on_item_clicked(self, name):
        self.contactClicked.emit(name)
