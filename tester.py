import sys
import os
import json

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QScrollArea,
    QFrame,
)
from PyQt5.QtCore import Qt

from request_block import RequestBlock


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.default_fonts = {
            "title": {"family": "Arial", "size": 10, "weight": "bold"},
            "status_code": {"family": "Arial", "size": 10, "weight": "bold"},
            "combo": {"family": "Arial", "size": 10, "weight": "bold"},
            "entry": {"family": "Consolas", "size": 10},
            "button": {"family": "Arial", "size": 10},
            "body": {"family": "Consolas", "size": 10},
            "response": {"family": "Consolas", "size": 10}
        }
        self.blocks = []
        self.clear_module = {"title": "", "url": "", "body": "", "method": 0}

        self.file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "config_data.json")
        self.load_data()

        self.setMinimumWidth(800)
        self.resize(800, 600)

        # Контейнер для строки запроса
        self.domen_line = QLineEdit()
        self.domen_line.setPlaceholderText("Domen / IP")
        self.domen_line.setText(self.data["config"]["main_url"])

        self.save_btn = QPushButton("Save")
        self.head_layout = QHBoxLayout()
        self.head_layout.addWidget(self.domen_line, 1)
        self.head_layout.addWidget(self.save_btn)

        # Контейнер для блоков
        self.blocks_widget = QWidget()
        self.block_layout = QVBoxLayout(self.blocks_widget)
        self.block_layout.setContentsMargins(0, 0, 0, 0)
        self.block_layout.setSpacing(10)
        self.block_layout.addStretch()

        # Область прокрутки
        self.block_scroll = QScrollArea()
        self.block_scroll.setWidgetResizable(True)
        self.block_scroll.setFrameShape(QFrame.NoFrame)
        self.block_scroll.setWidget(self.blocks_widget)

        self.down_layout = QHBoxLayout()

        # Главный Layout
        self.layoutMain = QVBoxLayout(self)
        self.layoutMain.addLayout(self.head_layout)
        self.layoutMain.addWidget(self.block_scroll)
        self.layoutMain.addLayout(self.down_layout)

        self.btn_add_block = QPushButton("Добавить блок")
        self.down_layout.addWidget(self.btn_add_block)
        self.btn_add_block.clicked.connect(self.add_block_bt)
        self.save_btn.clicked.connect(self.save_data)
        self.domen_line.textChanged.connect(self.updateUrl)

        for i in range(len(self.data["data"])):
            self.add_block(self.data["data"][i])
        self.updateUrl()


    def updateUrl(self):
        for i in self.blocks:
            i.updateUrl(self.domen_line.text())
            print(i, self.domen_line.text())

    def add_block_bt(self):
        self.data["data"].append(self.clear_module)
        self.add_block()
        print(len(self.data["data"]))

    def add_block(self, data=None):
        if data:
            block = RequestBlock(data)
        else:
            data = self.clear_module
            data["title"] = "Block " + str(self.block_layout.count())
            block = RequestBlock(data)
        self.block_layout.insertWidget(self.block_layout.count() - 1, block)
        self.blocks.append(block)

    def load_data(self):
        if not os.path.exists(self.file):
            return
        with open(self.file, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        if len(self.data["data"]) == 0:
            self.data["data"].append(self.clear_module)
        print(self.data["config"]["main_url"])
        print(len(self.data["data"]))

    def save_data(self):
        self.data["config"]["main_url"] = self.domen_line.text()
        self.data["data"]=[]
        for i in self.blocks:
            self.data["data"].append(i.getData())
        print(self.data)
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec_())
