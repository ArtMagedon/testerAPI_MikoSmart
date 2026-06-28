from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QGroupBox,
    QLabel
)

from PyQt5.QtCore import Qt, pyqtSignal

import requests


class RequestBlock(QGroupBox):
    deleteRequested = pyqtSignal(object)

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.box_Height = 200
        print(data)
        self.setMaximumHeight(260)  # Ограничение высоты

        # ---------- Верхняя строка ----------
        self.req_type_selector = QComboBox()
        self.req_type_selector.addItems([
            "GET",
            "POST",
            "PUT",
            "DELETE"
        ])

        self.url_line = QLineEdit()
        self.url_line.setPlaceholderText("url")

        self.send_btn = QPushButton("Send")
        self.delete_btn = QPushButton("✕")
        self.delete_btn.setMaximumWidth(30)
        self.delete_btn.setObjectName("DeleteButton")
        self.setStyleSheet("""
            #DeleteButton {
                background-color: #F44336;
                color: white;
                border-radius: 5px;
                border: none;
                padding: 2px 4px;
            }
            #DeleteButton:hover { background-color: #D32F2F; }
        """)

        self.top_layout = QHBoxLayout()
        self.top_layout.addWidget(self.req_type_selector)
        self.top_layout.addWidget(self.url_line, 1)
        self.top_layout.addWidget(self.send_btn)
        self.top_layout.addWidget(self.delete_btn)

        # ---------- Средняя строка ----------
        self.mid_layout = QHBoxLayout()
        self.status_code = QLabel()
        self.mid_layout.addStretch(1) 
        self.mid_layout.addWidget(self.status_code, 1)
        self.mid_layout.setContentsMargins(6, 0, 0, 0) 
        #self._hide_status()

        # ---------- Нижняя строка ----------
        self.body_box = QTextEdit()
        self.body_box.setPlaceholderText("Body")
        self.body_box.setFixedHeight(self.box_Height)

        self.response_box = QTextEdit()
        self.response_box.setPlaceholderText("Response")
        self.response_box.setFixedHeight(self.box_Height)
        self.response_box.setReadOnly(True)
        
        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addWidget(self.body_box)
        self.bottom_layout.addWidget(self.response_box)

        # ---------- Основной Layout ----------
        layout = QVBoxLayout(self)
        layout.addLayout(self.top_layout)
        layout.addLayout(self.mid_layout)
        layout.addLayout(self.bottom_layout, 1)

        self.update_data(data)

        self.req_type_selector.currentIndexChanged.connect(self._update_combo_style)
        self._update_combo_style()
        self.send_btn.clicked.connect(self.sendReq)
        self.delete_btn.clicked.connect(self.on_delete)
        
    def on_delete(self):
        self.deleteRequested.emit(self)

    def sendReq(self):
        request_data = {
            "url": self.main_url+self.url_line.text(),
            "body": self.body_box.toPlainText(),
            "method": self.req_type_selector.currentIndex(),
        }
        print(request_data)
        try:
            if request_data["method"] == 0:
                resp = requests.get(request_data["url"])
            elif request_data["method"] == 1:
                resp = requests.post(request_data["url"], data=request_data["body"])
            elif request_data["method"] == 2:
                resp = requests.put(request_data["url"], data=request_data["body"])
            elif request_data["method"] == 3:
                resp = requests.delete(request_data["url"], data=request_data["body"])
            else:
                resp = None
            if resp is not None:
                #print(resp.text)
                self._show_status()
                self.response_box.setPlainText(resp.text)
                self.status_code.setText(str(resp.status_code))
        except Exception as e:
            self._show_status()
            self.response_box.setPlainText(str(e))
            self.status_code.setText("ERROR")

    def _show_status(self):
        if self.mid_layout.indexOf(self.status_code) == -1:
            self.mid_layout.addWidget(self.status_code, 1)
            self.status_code.show()

    def _hide_status(self):
        self.mid_layout.removeWidget(self.status_code)
        self.status_code.hide()
        self.status_code.setText("")

    def updateUrl(self,main_url):
        self.main_url=main_url
        print(self.title(), self.main_url)

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

    def update_data(self, external_data: dict):
        self.setTitle(external_data["title"])
        self.url_line.setText(external_data["url"])
        self.body_box.setText(external_data["body"])
        self.req_type_selector.setCurrentIndex(external_data["method"])

    def getData(self):
        return {
            "title": self.title(),
            "url": self.url_line.text(),
            "body": self.body_box.toPlainText(),
            "method": self.req_type_selector.currentIndex(),
        }
    
    
