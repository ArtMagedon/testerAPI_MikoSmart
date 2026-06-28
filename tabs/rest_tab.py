from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QScrollArea,
    QFrame,
)

from request_block import RequestBlock


class RestTab(QWidget):

    def __init__(self, data):
        super().__init__()

        self.data = data

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
            self.data["config"]["main_url"]
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

        self.data["config"]["main_url"] = \
            self.domain_line.text()

        self.data["data"] = []

        for block in self.blocks:
            self.data["data"].append(
                block.getData()
            )

    def save_to_file(self):
        self.save_to_data()