from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QGroupBox
)


class RequestBlock(QGroupBox):
    def __init__(self, name:str = "BLOCK", parent=None):
        super().__init__(parent)
        self.box_Height=200


        self.setTitle(name)
        self.setMaximumHeight(260)  # Ограничение высоты

        # ---------- Верхняя строка ----------
        self.req_type_selector = QComboBox()
        self.req_type_selector.addItems([
            "GET",
            "POST",
            "PUT",
            "DELETE"
        ])
        self._update_combo_style()

        self.url_line = QLineEdit()
        self.url_line.setPlaceholderText("url")

        self.send_btn = QPushButton("Send")

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.req_type_selector)
        top_layout.addWidget(self.url_line, 1)
        top_layout.addWidget(self.send_btn)

        # ---------- Нижняя строка ----------
        self.body_box = QTextEdit()
        self.body_box.setPlaceholderText("Body")
        self.body_box.setFixedHeight(self.box_Height) 
        

        self.response_box = QTextEdit()
        self.response_box.setPlaceholderText("Response")
        self.response_box.setFixedHeight(self.box_Height) 

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.body_box)
        bottom_layout.addWidget(self.response_box)

        # ---------- Основной Layout ----------
        layout = QVBoxLayout(self)
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout, 1)

        self.req_type_selector.currentIndexChanged.connect(self._update_combo_style)

    def _update_combo_style(self):
        index = self.req_type_selector.currentIndex()
        colors = ["#4CAF50", "#FF9800", "#2196F3", "#F44336"]
        if 0 <= index < len(colors):
            self.req_type_selector.setStyleSheet(f"""
                QComboBox {{
                    color: {colors[index]};
                }}
            """)
        else:
            self.req_type_selector.setStyleSheet("")

    
    
    def import_data(self, external_data:dict):
        if external_data:
            self.url=external_data["url"]
            self.body=external_data["body"]
            self.req_type=external_data["req_type"]
        

    
