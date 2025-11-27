import base64
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QSizePolicy
from qfluentwidgets import BodyLabel, AvatarWidget, FluentIcon, IconWidget, TitleLabel

THEME_COLOR = '#0099FF'
BUBBLE_SELF_COLOR = '#E5F5FF'  # 自己发送的气泡背景色
BUBBLE_OTHER_COLOR = '#F2F2F2'  # 别人发送的气泡背景色


class SystemMessageLabel(BodyLabel):
    def __init__(self, text):
        super().__init__()
        font = self.font()
        font.setPixelSize(12)
        self.setFont(font)
        self.setMinimumSize(100, 25)
        self.setMaximumWidth(400)
        self.setContentsMargins(20, 8, 20, 8)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.setWordWrap(True)
        self.setText(text)
        self.setStyleSheet("background-color: rgba(150, 150, 150, 50); border-radius: 15px")


class MessageBubble(QWidget):
    def __init__(self, content, avatar, name, is_me=False, is_room=False, msg_type='text', parent=None):
        super().__init__(parent)
        self.is_me = is_me

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        self.avatar = AvatarWidget()
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.avatar.setImage(avatar)
        self.avatar.setFixedSize(60, 60)

        avatar_layout = QVBoxLayout()

        avatar_layout.addWidget(self.avatar)
        avatar_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        avatar_layout.addStretch(1)

        self.bubble_container = QFrame()
        self.bubble_layout = QVBoxLayout(self.bubble_container)
        self.bubble_layout.setContentsMargins(8, 4, 8, 4)

        self.name_bubble_layout = QVBoxLayout()
        # 判断是否为房间消息，如果是则聊天气泡带上发送方的名字
        if is_room and not is_me:
            name_label = TitleLabel(name)
            name_label.setAlignment(Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignLeft)
            font = name_label.font()
            font.setPixelSize(10)
            name_label.setFont(font)
            self.name_bubble_layout.addWidget(name_label, 0.1)
        self.name_bubble_layout.addWidget(self.bubble_container, 1)
        # self.name_bubble_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

        if msg_type == 'file':
            self.content_widget = SystemMessageLabel(content)
            self.content_widget.setWordWrap(False)
            layout.addWidget(self.content_widget, 1)
            layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        else:
            if msg_type == 'image':
                # 如果是图片，content 是 base64 字符串
                self.content_widget = QLabel()

                img_data = base64.b64decode(content)
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)

                # 限制图片最大显示尺寸
                if pixmap.width() > 300:
                    pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)
                if pixmap.height() > 300:
                    pixmap = pixmap.scaledToHeight(300, Qt.SmoothTransformation)

                self.content_widget.setPixmap(pixmap)

                bubble_bg = "transparent"

            else:
                # 如果是文本，content 是普通字符串
                self.content_widget = BodyLabel(content)
                self.content_widget.setMaximumWidth(400)
                self.content_widget.setMinimumHeight(0)
                self.content_widget.setWordWrap(True)
                self.content_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
                self.content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
                if is_me:
                    self.content_widget.setStyleSheet("color: white;")
                else:
                    self.content_widget.setStyleSheet("color: black;")
                bubble_bg = THEME_COLOR if is_me else BUBBLE_OTHER_COLOR

            self.bubble_layout.addWidget(self.content_widget)

            # 判断是自己发送的消息还是接收的消息
            if is_me:
                layout.addStretch(1)
                layout.addLayout(self.name_bubble_layout)
                self.name_bubble_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
                layout.addSpacing(8)
                layout.addLayout(avatar_layout)

                # 如果是图片，可能不需要背景色，或者保留
                self.bubble_container.setStyleSheet(f"""
                    QFrame {{
                        background-color: {bubble_bg if msg_type == 'text' else 'transparent'};
                        border-radius: 8px; border-top-right-radius: 2px; 
                    }}
                """)
            else:
                layout.addLayout(avatar_layout)
                layout.addSpacing(8)
                layout.addLayout(self.name_bubble_layout)
                self.name_bubble_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                layout.addStretch(1)

                self.bubble_container.setStyleSheet(f"""
                    QFrame {{
                        background-color: {bubble_bg if msg_type == 'text' else 'transparent'};
                        border-radius: 8px; border-top-left-radius: 2px;
                    }}
                """)