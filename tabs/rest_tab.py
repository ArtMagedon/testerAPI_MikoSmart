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

        self.domain_line.setFont(QFont(self.config["fonts"]["domain_line"]["family"],
                                       self.config["fonts"]["domain_line"]["size"],
                                       QFont.Bold if self.config["fonts"]["domain_line"]["weight"] == "bold" else QFont.Normal))
        
        self.save_btn.setFont(QFont(self.config["fonts"]["save_btn"]["family"],
                                    self.config["fonts"]["save_btn"]["size"],
                                    QFont.Bold if self.config["fonts"]["save_btn"]["weight"] == "bold" else QFont.Normal))
        
        self.add_btn.setFont(QFont(self.config["fonts"]["add_btn"]["family"],
                                   self.config["fonts"]["add_btn"]["size"],
                                   QFont.Bold if self.config["fonts"]["add_btn"]["weight"] == "bold" else QFont.Normal))
        
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
