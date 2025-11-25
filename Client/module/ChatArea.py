import base64

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QFrame, \
    QAbstractItemView, QFileDialog
from qfluentwidgets import TextEdit, PrimaryPushButton, StrongBodyLabel, TransparentToolButton, FluentIcon
from module.MessageBubble import MessageBubble

class ChatArea(QWidget):
    """
    右侧聊天区域：包含消息列表和输入框
    """
    sent = Signal(str, str, str)

    def __init__(self, chat_name, parent=None):
        super().__init__(parent)
        self.chat_name = chat_name
        self.chat_type = ''

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

        tool_layout = QHBoxLayout()
        self.img_btn = TransparentToolButton(FluentIcon.PHOTO, self)  # 换个图标
        self.img_btn.clicked.connect(self.select_image)  # 连接槽函数
        tool_layout.insertWidget(0, self.img_btn)  # 插入到第一个
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
        widget = MessageBubble(content, is_me, msg_type)

        item.setSizeHint(QSize(0, widget.sizeHint().height() + 20))
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
            # 1. 读取文件并转 Base64
            with open(file_path, 'rb') as f:
                img_data = f.read()
                # 转为 base64 字符串
                base64_str = base64.b64encode(img_data).decode('utf-8')

            # 2. 界面上显示图片 (is_me=True, type='image')
            self.add_message(base64_str, is_me=True, msg_type='image')

            # 3. 发送信号给 MainWindow -> Client -> Listener
            # content 是 base64 字符串， type 是 'image'
            self.sent.emit(base64_str, self.chat_name, 'image')