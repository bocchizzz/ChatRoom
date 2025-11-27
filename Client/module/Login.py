from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from qfluentwidgets import PushButton, LineEdit, MessageBoxBase, TitleLabel, CaptionLabel


class LoginWindow(MessageBoxBase):
    closed = Signal(str, bool)

    def __init__(self, online_users, parent=None):
        super().__init__(parent)
        self.online_users = online_users
        self.textEdit = LineEdit()

        self.title = TitleLabel()
        self.title.setText("请输入用户名")
        font = self.title.font()
        font.setPixelSize(16)
        self.title.setFont(font)

        self.waring_label = CaptionLabel("名字为空或有重复")
        self.waring_label.hide()

        self.viewLayout.addWidget(self.title)
        self.viewLayout.addWidget(self.textEdit)
        self.viewLayout.addWidget(self.waring_label)
        self.widget.setMinimumWidth(350)

    def validate(self) -> bool:
        isvalid = (not self.textEdit.text() in self.online_users) and (self.textEdit.text() != '')
        self.waring_label.setHidden(isvalid)
        return isvalid
