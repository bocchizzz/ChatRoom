import base64
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel
from qfluentwidgets import BodyLabel, AvatarWidget

THEME_COLOR = '#0099FF'
BUBBLE_SELF_COLOR = '#E5F5FF'  # 自己发送的气泡背景色
BUBBLE_OTHER_COLOR = '#F2F2F2'  # 别人发送的气泡背景色


class MessageBubble(QWidget):
    # 修改 init，增加 msg_type 参数，默认为 'text'
    def __init__(self, content, is_me=False, msg_type='text', parent=None):
        super().__init__(parent)
        self.is_me = is_me

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        self.avatar = AvatarWidget()
        self.avatar.setImage('asset/m1.png')
        self.avatar.setFixedSize(50, 50)
        self.avatar.setMaximumSize(50, 50)
        avatar_layout = QVBoxLayout()
        avatar_layout.addWidget(self.avatar)
        avatar_layout.addStretch(1)

        self.bubble_container = QFrame()
        self.bubble_layout = QVBoxLayout(self.bubble_container)
        self.bubble_layout.setContentsMargins(12, 8, 12, 8)

        if msg_type == 'image':
            # 如果是图片，content 是 base64 字符串
            self.content_widget = QLabel()

            # Base64 -> QPixmap
            img_data = base64.b64decode(content)
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)

            # 限制图片最大显示尺寸
            if pixmap.width() > 300:
                pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)
            if pixmap.height() > 300:
                pixmap = pixmap.scaledToHeight(300, Qt.SmoothTransformation)

            self.content_widget.setPixmap(pixmap)
            # 图片气泡背景可以设为透明或保留颜色
            bubble_bg = "transparent"

        else:
            # 如果是文本，content 是普通字符串
            self.content_widget = BodyLabel(content)
            self.content_widget.setWordWrap(True)
            self.content_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            if is_me:
                self.content_widget.setStyleSheet("color: white;")
            else:
                self.content_widget.setStyleSheet("color: black;")
            bubble_bg = THEME_COLOR if is_me else BUBBLE_OTHER_COLOR

        self.bubble_layout.addWidget(self.content_widget)

        # 布局逻辑保持不变，但要动态设置背景色
        if is_me:
            layout.addStretch(1)
            layout.addWidget(self.bubble_container)
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
            layout.addWidget(self.bubble_container)
            layout.addStretch(1)

            self.bubble_container.setStyleSheet(f"""
                QFrame {{
                    background-color: {bubble_bg if msg_type == 'text' else 'transparent'};
                    border-radius: 8px; border-top-left-radius: 2px;
                }}
            """)

# class MessageBubble(QWidget):
#     """
#     自定义聊天气泡组件
#     """
#
#     def __init__(self, text, is_me=False, parent=None):
#         super().__init__(parent)
#         self.is_me = is_me
#
#         # 主布局
#         layout = QHBoxLayout(self)
#         layout.setContentsMargins(10, 5, 10, 5)
#
#         # 头像
#         self.avatar = AvatarWidget('path/to/avatar.png')  # 这里可以用真实的图片路径
#         self.avatar.setFixedSize(36, 36)
#
#         # 消息气泡容器
#         self.bubble_container = QFrame()
#         self.bubble_layout = QVBoxLayout(self.bubble_container)
#         self.bubble_layout.setContentsMargins(12, 8, 12, 8)
#
#         # 消息文本
#         self.content_label = BodyLabel(text)
#         self.content_label.setWordWrap(True)  # 自动换行
#         self.content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
#
#         # 根据是谁发的消息设置样式和布局方向
#         if is_me:
#             # 我发的：[弹簧] [气泡] [头像]
#             layout.addStretch(1)
#             layout.addWidget(self.bubble_container)
#             layout.addSpacing(8)
#             layout.addWidget(self.avatar)
#
#             # 气泡样式 (浅蓝色，圆角)
#             self.bubble_container.setStyleSheet(f"""
#                 QFrame {{
#                     background-color: {THEME_COLOR};
#                     border-radius: 8px;
#                     border-top-right-radius: 2px;
#                 }}
#             """)
#             self.content_label.setStyleSheet("color: white;")  # 蓝色背景配白字
#
#         else:
#             # 别人发的：[头像] [气泡] [弹簧]
#             layout.addWidget(self.avatar)
#             layout.addSpacing(8)
#             layout.addWidget(self.bubble_container)
#             layout.addStretch(1)
#
#             # 气泡样式 (浅灰色，圆角)
#             self.bubble_container.setStyleSheet(f"""
#                 QFrame {{
#                     background-color: {BUBBLE_OTHER_COLOR};
#                     border-radius: 8px;
#                     border-top-left-radius: 2px;
#                 }}
#             """)
#             self.content_label.setStyleSheet("color: black;")
#
#         self.bubble_layout.addWidget(self.content_label)