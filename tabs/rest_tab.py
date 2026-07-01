from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QEvent, Qt
import json
import os

from request_block import RequestBlock


class RestTab(QWidget):

    def __init__(self, file, fonts):
        super().__init__()
        self.config={"fonts": fonts}

        self.file = file
        self.load_data()

        self.blocks = []
        self.drag_block = None

        self.clear_module = {
            "title": "",
            "url": "",
            "body": "",
            "method": 0
        }

        self.domain_line = QLineEdit()
        self.domain_line.setPlaceholderText("Domain / IP")
        self.domain_line.setText(
            self.data["main_url"]
        )

        self.save_btn = QPushButton("Save")

        self.head_layout = QHBoxLayout()
        self.head_layout.addWidget(self.domain_line, 1)
        self.head_layout.addWidget(self.save_btn)

        self.blocks_widget = QWidget()

        self.block_layout = QVBoxLayout(self.blocks_widget)
        self.block_layout.setSpacing(10)
        self.block_layout.addStretch()

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setWidget(self.blocks_widget)

        self.bottom_layout = QHBoxLayout()

        self.add_btn = QPushButton("Добавить блок")
        self.bottom_layout.addWidget(self.add_btn)

        layout = QVBoxLayout(self)

        layout.addLayout(self.head_layout)
        layout.addWidget(self.scroll)
        layout.addLayout(self.bottom_layout)

        self.add_btn.clicked.connect(self.add_block_bt)
        self.save_btn.clicked.connect(self.save_to_file)
        self.domain_line.textChanged.connect(self.update_url)

        if len(self.data["data"]) == 0:
            self.data["data"].append(self.clear_module)

        for block in self.data["data"]:
            self.add_block(block)

        self.update_url()
        self.apply_fonts()

    def load_data(self):
        if not os.path.exists(self.file):
            self.data = {
                "main_url": "",
                "data": []
            }
            return

        with open(self.file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def remove_block(self, block):

        if block in self.blocks:
            self.blocks.remove(block)

        self.block_layout.removeWidget(block)

        block.drag_handle.removeEventFilter(self)
        block.deleteLater()

    def update_url(self):

        for block in self.blocks:
            block.updateUrl(
                self.domain_line.text()
            )

    def add_block_bt(self):

        self.add_block()

    def add_block(self, data=None):

        if data is None:
            data = self.clear_module.copy()
            data["title"] = f"Block {len(self.blocks)+1}"

        block = RequestBlock(data)

        block.deleteRequested.connect(
            self.remove_block
        )

        self.block_layout.insertWidget(
            self.block_layout.count()-1,
            block
        )

        self.blocks.append(block)
        block.drag_handle.installEventFilter(self)


    def eventFilter(self, obj, event):
        block = None

        for item in self.blocks:
            if getattr(item, "drag_handle", None) is obj:
                block = item
                break

        if block is None:
            return super().eventFilter(obj, event)

        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            self.drag_block = block
            block.drag_handle.setCursor(Qt.CursorShape.ClosedHandCursor)
            return True

        if event.type() == QEvent.Type.MouseMove and self.drag_block is block:
            self.move_drag_block(event.globalPos())
            return True

        if event.type() == QEvent.Type.MouseButtonRelease and self.drag_block is block:
            block.drag_handle.setCursor(Qt.CursorShape.OpenHandCursor)
            self.drag_block = None
            return True

        return super().eventFilter(obj, event)


    def move_drag_block(self, global_pos):
        if self.drag_block is None:
            return

        local_pos = self.blocks_widget.mapFromGlobal(global_pos)

        new_index = len(self.blocks) - 1

        for index, block in enumerate(self.blocks):
            if block is self.drag_block:
                continue

            block_middle = block.y() + block.height() // 2

            if local_pos.y() < block_middle:
                new_index = index
                break

        old_index = self.blocks.index(self.drag_block)

        if new_index == old_index:
            return

        self.blocks.pop(old_index)

        if new_index > old_index:
            new_index -= 1

        self.blocks.insert(new_index, self.drag_block)

        self.block_layout.removeWidget(self.drag_block)
        self.block_layout.insertWidget(new_index, self.drag_block)

    def make_font(self, fonts, key):
        font = fonts[key]
        weight = QFont.Bold if font["weight"] == "bold" else QFont.Normal
        return QFont(font["family"], font["size"], weight)

    def save_to_data(self):

        self.data["main_url"] = self.domain_line.text()

        self.data["data"] = []

        for block in self.blocks:
            self.data["data"].append(
                block.getData()
            )

    def save_to_file(self):
        self.save_to_data()
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def apply_fonts(self):

        self.domain_line.setFont(self.make_font(self.config["fonts"],"domain_line"))
        self.save_btn.setFont(self.make_font(self.config["fonts"],"save_btn"))
        self.add_btn.setFont(self.make_font(self.config["fonts"],"add_btn"))
        
        for i in self.blocks:
            i.apply_fonts(self.config["fonts"])

    def get_fonts(self):
        s = [self.domain_line, self.save_btn, self.add_btn, self.blocks[0]]
        for i in s:
            font_info = i.fontInfo()
            print(i)
            print(font_info.family())        # Название
            print(font_info.pointSize())     # Размер
            print(font_info.bold())         # Жирный ли шрифт
            print(font_info.italic())       # Курсивный ли шрифт
        print(self.blocks[0])
        self.blocks[0].get_fonts()
