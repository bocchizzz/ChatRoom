from qfluentwidgets import MessageBoxBase, ListWidget, TitleLabel, LineEdit, CaptionLabel
from PySide6.QtWidgets import  QAbstractItemView


class CreateRoom(MessageBoxBase):
    def __init__(self, online_rooms, online_users, parent=None):
        super().__init__(parent)
        self.online_rooms = online_rooms

        self.title = TitleLabel('请输入聊天房间名称')
        self.name_edit = LineEdit()

        self.user_list = ListWidget()
        self.user_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.user_list.addItems(online_users)

        self.warning_label = CaptionLabel()
        self.warning_label.hide()

        self.viewLayout.addWidget(self.title, 0.2)
        self.viewLayout.addWidget(self.name_edit, 0.2)
        self.viewLayout.addWidget(self.user_list, 1)
        self.viewLayout.addWidget(self.warning_label)
        self.widget.setMinimumWidth(400)

        self.room_info = {}

    def validate(self) -> bool:
        name = self.name_edit.text()
        if name == '' or name in self.online_rooms:
            self.warning_label.setText('房间名称为空或重复')
            self.warning_label.setHidden(False)
            return False
        else:
            if self.user_list.selectedItems():
                self.room_info['name'] = name
                self.room_info['users'] = [item.text() for item in self.user_list.selectedItems()]
                self.warning_label.setHidden(True)
                return True
            else:
                self.warning_label.setText('未选择房间成员')
                self.warning_label.setHidden(False)
                return False
