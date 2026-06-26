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
            "label": {"family": "Arial", "size": 10, "weight": "bold"},
            "combo": {"family": "Arial", "size": 10, "weight": "bold"},
            "entry": {"family": "Consolas", "size": 10},
            "button": {"family": "Arial", "size": 10},
            "body": {"family": "Consolas", "size": 10},
            "output": {"family": "Consolas", "size": 10}
        }
        self.file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_data.json")
        self.load_data(self.file)

        self.setMinimumWidth(800)
        self.resize(800,600)
        self.domen_line = QLineEdit()
        self.domen_line.setPlaceholderText("Domen / IP")

        self.send_btn = QPushButton("Save")

        self.head_layout = QHBoxLayout()
        self.head_layout.addWidget(self.domen_line, 1)
        self.head_layout.addWidget(self.send_btn)

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
        
        for i in range(self.num_placeholder):
            self.add_block()

    def add_block_bt(self):
        self.num_placeholder+=1
        self.add_block()
        print(self.num_placeholder)

    def add_block(self):
        block = RequestBlock(name="Block " + str(self.block_layout.count()))
        self.block_layout.insertWidget(self.block_layout.count() - 1, block)

    def load_data(self, SAVE_FILE:str):
        if not os.path.exists(SAVE_FILE):
            return
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.main_url="https://"+data["config"]["main_url"]
        self.num_placeholder=len(data["data"])
        if self.num_placeholder==0: self.num_placeholder+=1
        print(self.main_url)
        print(self.num_placeholder)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec_())
