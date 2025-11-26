import base64
import os

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QFrame, \
    QAbstractItemView, QFileDialog
from qfluentwidgets import TextEdit, PrimaryPushButton, StrongBodyLabel, TransparentToolButton, FluentIcon
from module.MessageBubble import MessageBubble


class ChatArea(QWidget):
    """
    右侧聊天区域：包含消息列表和输入框
    """
    sent = Signal(str, str, str)  # content, to_id, type

    def __init__(self, chat_name, other_avatar, self_avatar, parent=None):
        super().__init__(parent)
        self.chat_name = chat_name
        self.chat_type = ''
        self.other_avatar = other_avatar
        self.self_avatar = self_avatar

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 顶部标题栏 (显示当前聊天对象)
        self.header = QFrame()
        self.header.setFixedHeight(50)
        self.header.setStyleSheet("background-color: white; border-bottom: 2px solid #E5E5E5;")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        self.title_label = StrongBodyLabel(chat_name)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)

        self.layout.addWidget(self.header)

        # 消息列表区域
        self.message_list = QListWidget()
        self.message_list.setFrameShape(QListWidget.NoFrame)
        self.message_list.setStyleSheet("QListWidget { background-color: #F9F9F9; border: none; }")
        self.message_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.message_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.message_list.setStyleSheet("""
                    QListWidget {
                        background-color: #F9F9F9; 
                        border: none;
                        outline: none;
                    }
                    QListWidget::item {
                        background-color: transparent;
                        border: none; 
                        padding: 0px;
                    }
                    QListWidget::item:hover, 
                    QListWidget::item:selected {
                        background-color: transparent;
                        border: none;
                    }
                """)
        self.layout.addWidget(self.message_list)

        # 输入区域
        self.input_container = QFrame()
        self.input_container.setFixedHeight(160)
        self.input_container.setStyleSheet("background-color: white; border-top: 1px solid #E5E5E5;")
        input_layout = QVBoxLayout(self.input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)

        # 工具栏区域
        # 图片选择按钮
        tool_layout = QHBoxLayout()
        self.img_btn = TransparentToolButton(FluentIcon.PHOTO, self)
        self.img_btn.clicked.connect(self.select_image)
        tool_layout.addWidget(self.img_btn)
        # 文件选择按钮
        self.file_btn = TransparentToolButton(FluentIcon.DOCUMENT, self)
        self.file_btn.setToolTip("发送文件")
        self.file_btn.clicked.connect(self.select_file)
        tool_layout.addWidget(self.file_btn)

        tool_layout.addStretch(1)
        input_layout.addLayout(tool_layout)

        # 文本输入框
        self.text_edit = TextEdit()
        self.text_edit.setPlaceholderText("请输入消息...")
        self.text_edit.setStyleSheet("QTextEdit { border: none; background: transparent; }")
        input_layout.addWidget(self.text_edit)

        # 发送按钮区
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        self.send_btn = PrimaryPushButton("发送")
        self.send_btn.setFixedWidth(100)
        self.send_btn.clicked.connect(self.send_message)
        btn_layout.addWidget(self.send_btn)
        input_layout.addLayout(btn_layout)

        self.layout.addWidget(self.input_container)

    def add_message(self, content, is_me=True, msg_type='text'):
        item = QListWidgetItem()
        widget = MessageBubble(content, self.self_avatar if is_me else self.other_avatar, is_me, msg_type)

        item.setSizeHint(QSize(0, widget.sizeHint().height() + 4))
        self.message_list.addItem(item)
        self.message_list.setItemWidget(item, widget)
        self.message_list.scrollToBottom()

    def send_message(self):
        """
        发送消息
        """
        text = self.text_edit.toPlainText().strip()
        if text:
            self.add_message(text, is_me=True)
            self.text_edit.clear()
            self.sent.emit(text, self.chat_name, 'text')

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            # 读取文件并转 Base64
            with open(file_path, 'rb') as f:
                img_data = f.read()
                base64_str = base64.b64encode(img_data).decode('utf-8')

            # 显示图片
            self.add_message(base64_str, is_me=True, msg_type='image')

            # 发送信号MainWindow -> Client -> Listener
            self.sent.emit(base64_str, self.chat_name, 'image')

    def select_file(self):
        """选择并发送文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "All Files (*)"
        )
        if file_path:
            filename = os.path.basename(file_path)
            self.add_message(f"正在发送: {filename}", is_me=True, msg_type='file')
            self.sent.emit(file_path, self.chat_name, 'file')
