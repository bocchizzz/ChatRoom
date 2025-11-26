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


        # self.butn_confirm = PushButton()
        # self.butn_confirm.setText("确定")
        #
        # self.butn_cancel = PushButton()
        # self.butn_cancel.setText("取消")
        #
        # v = QVBoxLayout()
        # v.addWidget(self.title, 1)
        # v.addWidget(self.textEdit, 2)
        # h = QHBoxLayout()
        # h.addWidget(self.butn_confirm)
        # h.addWidget(self.butn_cancel)
        # v.addLayout(h, 1)
        # self.setLayout(v)
        #
        # self.setMaximumSize(300, 160)
        # self.setMinimumSize(300, 160)
        #
        # self.butn_confirm.clicked.connect(self.confirm)
        # self.butn_cancel.clicked.connect(self.cancel)

    # def confirm(self):
    #     if self.textEdit.text():
    #         self.closed.emit(self.textEdit.text(), True)
    #         self.close()
    #
    # def cancel(self):
    #     self.closed.emit("", False)
    #     self.close()
