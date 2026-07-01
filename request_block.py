from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QGroupBox,
    QLabel,
    QSizePolicy,
    QInputDialog,
    QStyleOptionGroupBox,
    QStyle
)
from PyQt5.QtGui import QFont, QFontMetrics, QMouseEvent

from PyQt5.QtCore import Qt, pyqtSignal

import requests


class RequestBlock(QGroupBox):
    deleteRequested = pyqtSignal(object)

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.box_Height = 200
        print(data)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Maximum
        )

        # ---------- Верхняя строка ----------
        self.drag_handle = QLabel("☰")
        self.drag_handle.setFixedWidth(24)
        self.drag_handle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_handle.setCursor(Qt.CursorShape.OpenHandCursor)
        self.drag_handle.setObjectName("DragHandle")

        self.method_selector = QComboBox()
        self.method_selector.addItems([
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
        self.top_layout.addWidget(self.drag_handle)
        self.top_layout.addWidget(self.method_selector)
        self.top_layout.addWidget(self.url_line, 1)
        self.top_layout.addWidget(self.send_btn)
        self.top_layout.addWidget(self.delete_btn)

        # ---------- Средняя строка ----------
        self.mid_layout = QHBoxLayout()
        self.status_code = QLabel()
        self.mid_layout.addStretch(1)
        self.mid_layout.addWidget(self.status_code, 1)
        self.mid_layout.setContentsMargins(6, 0, 0, 0)
        self._hide_status()

        # ---------- Нижняя строка ----------
        self.body_box = QTextEdit()
        self.body_box.setPlaceholderText("Body")
        self.body_box.setFixedHeight(self.box_Height)
        self.body_box.setAcceptRichText(False)

        self.response_box = QTextEdit()
        self.response_box.setPlaceholderText("Response")
        self.response_box.setFixedHeight(self.box_Height)
        self.response_box.setReadOnly(True)

        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addWidget(self.body_box)
        self.bottom_layout.addWidget(self.response_box)
        self.response_box.setTabStopDistance(30)

        # ---------- Основной Layout ----------
        layout = QVBoxLayout(self)
        layout.addLayout(self.top_layout)
        layout.addLayout(self.mid_layout)
        layout.addLayout(self.bottom_layout, 1)

        self.update_data(data)

        self.method_selector.currentIndexChanged.connect(
            self._update_combo_style)
        self._update_combo_style()
        self.send_btn.clicked.connect(self.sendReq)
        self.delete_btn.clicked.connect(self.on_delete)

    def on_delete(self):
        self.deleteRequested.emit(self)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self._title_rect().contains(event.pos()):
            self.rename_block()
            event.accept()
            return

        super().mousePressEvent(event)

    def _title_rect(self):
        option = QStyleOptionGroupBox()
        self.initStyleOption(option)

        style = self.style()
        if style is None:
            return self.rect()

        return style.subControlRect(
            QStyle.ComplexControl.CC_GroupBox,
            option,
            QStyle.SubControl.SC_GroupBoxLabel,
            self
        )


    def rename_block(self):
        new_title, ok = QInputDialog.getText(
            self,
            "Переименование блока",
            "Новое название:",
            text=self.title()
        )

        if ok:
            new_title = new_title.strip()

            if new_title:
                self.setTitle(new_title)

    def make_font(self, fonts, key):
        font = fonts[key]
        weight = QFont.Bold if font["weight"] == "bold" else QFont.Normal
        return QFont(font["family"], font["size"], weight)

    def sendReq(self):
        request_data = {
            "url": self.main_url+self.url_line.text(),
            "body": self.body_box.toPlainText(),
            "method": self.method_selector.currentIndex(),
        }
        print(request_data)
        try:
            if request_data["method"] == 0:
                resp = requests.get(request_data["url"], timeout=10)
            elif request_data["method"] == 1:
                resp = requests.post(
                    request_data["url"], data=request_data["body"], timeout=10)
            elif request_data["method"] == 2:
                resp = requests.put(
                    request_data["url"], data=request_data["body"], timeout=10)
            elif request_data["method"] == 3:
                resp = requests.delete(
                    request_data["url"], data=request_data["body"], timeout=10)
            else:
                resp = None
            if resp is not None:
                # print(resp.text)
                self._show_status()
                self.response_box.setPlainText(resp.text)
                self.status_code.setText(str(resp.status_code))
                self.update_status_code_style()
        except Exception as e:
            self._show_status()
            self.response_box.setPlainText(str(e))
            self.status_code.setText("ERROR")
            self.status_code.setStyleSheet(f"""
            QLabel {{
                color: {"#F44336"};
            }}
            """)

    def _update_tab_width(self, text_edit_widget, font):
        fm = QFontMetrics(font)
        
        space_width = fm.width(' ')
        
        tab_width = space_width * 2 
        
        if tab_width == 0:
            tab_width = 30
            
        text_edit_widget.setTabStopDistance(tab_width)

    def _show_status(self):
        if self.mid_layout.indexOf(self.status_code) == -1:
            self.mid_layout.addWidget(self.status_code, 1)
            self.status_code.show()
            self.adjustSize()

    def _hide_status(self):
        self.mid_layout.removeWidget(self.status_code)
        self.status_code.hide()
        self.status_code.setText("")
        self.adjustSize()

    def updateUrl(self, main_url):
        self.main_url = main_url
        print(self.title(), self.main_url)

    def update_status_code_style(self):
        code = self.status_code.text()
        colors = ["#2196F3", "#4CAF50", "#FF9800",
                  "#F44336", "#F44336"]
        index = int(code[0])-1
        if 0 <= index < len(colors):
           self.status_code.setStyleSheet(f"""
            QLabel {{
                color: {colors[index]};
            }}
            """)
        else:
           self.status_code.setStyleSheet("")

    def _update_combo_style(self):
        index = self.method_selector.currentIndex()
        colors = ["#4CAF50", "#FF9800", "#2196F3", "#F44336"]
        if 0 <= index < len(colors):
            self.method_selector.setStyleSheet(f"""
                QComboBox {{
                    color: {colors[index]};
                }}
            """)
        else:
            self.method_selector.setStyleSheet("")

    def update_data(self, external_data: dict):
        self.setTitle(external_data["title"])
        self.url_line.setText(external_data["url"])
        self.body_box.setText(external_data["body"])
        self.method_selector.setCurrentIndex(external_data["method"])

    def getData(self):
        return {
            "title": self.title(),
            "url": self.url_line.text(),
            "body": self.body_box.toPlainText(),
            "method": self.method_selector.currentIndex(),
        }

    def apply_fonts(self, fonts):
        self.method_selector.setFont(self.make_font(fonts,"method_selector"))
        self.url_line.setFont(self.make_font(fonts,"url_line"))
        self.status_code.setFont(self.make_font(fonts,"status_code"))
        self.send_btn.setFont(self.make_font(fonts,"send_btn"))
        self.delete_btn.setFont(self.make_font(fonts,"send_btn"))
        self.body_box.setFont(self.make_font(fonts,"body_box"))
        self.response_box.setFont(self.make_font(fonts,"response_box"))
        self.setFont(self.make_font(fonts,"block_name"))

        self._update_tab_width(self.body_box, self.make_font(fonts,"body_box"))
        self._update_tab_width(self.response_box, self.make_font(fonts,"response_box"))

        #print(fonts)

    def get_fonts(self):
        s = [self.method_selector, self.url_line, self.status_code,
             self.send_btn, self.body_box, self.response_box,]
        for i in s:
            font_info = i.fontInfo()
            print(i)
            print(font_info.family())        # Название
            print(font_info.pointSize())     # Размер
            print(font_info.bold())         # Жирный ли шрифт
            print(font_info.italic())       # Курсивный ли шрифт
