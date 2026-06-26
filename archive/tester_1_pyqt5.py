import sys
import json
import os
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, 
                             QComboBox, QFrame, QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor


# Определение пути к файлу сохранения (рядом со скриптом)
script_dir = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(script_dir, "saved_data1.json")


# --- КОНСТАНТЫ И НАСТРОЙКИ ---
TOTAL_ROWS = 20
VISIBLE_ROWS = 3
BLOCK_ROWS = 12
TEXT_ROWS = 12
methods = ["GET", "PUT", "POST", "DELETE"]


class ContextMenuTextEdit(QTextEdit):
    """Текстовое поле с контекстным меню (Вставить при ПКМ)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def contextMenuEvent(self, e):
        menu = self.createStandardContextMenu()
        action_insert = menu.addAction("Вставить")
        action_insert.triggered.connect(self.insert_text)
        menu.exec_(e.globalPos())
        e.accept()
    
    def insert_text(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        self.append(text)


class RESTBlock(QWidget):
    """Один блок REST-запроса"""
    def __init__(self, row_num, parent=None):
        super().__init__(parent)
        self.row_num = row_num
        
        # Стили для методов
        self.method_colors = {
            "GET": "#008000",    # зеленый
            "POST": "#0000FF",   # синий
            "PUT": "#FFA500",    # оранжевый
            "DELETE": "#FF0000"  # красный
        }
        
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Верхняя панель: метод + путь + кнопка Send
        top_row = QHBoxLayout()
        
        # Метка с номером блока
        label = QLabel(f"№{self.row_num + 1}")
        label_font = QFont("Arial", 10, QFont.Bold)
        label.setFont(label_font)
        top_row.addWidget(label)
        
        # Выпадающий список методов
        self.method_combo = QComboBox()
        self.method_combo.addItems(methods)
        self.method_combo.currentTextChanged.connect(self.update_method_color)
        combo_font = QFont("Arial", 10, QFont.Bold)
        self.method_combo.setFont(combo_font)
        self.update_method_color()  # Установка начального цвета
        top_row.addWidget(self.method_combo)
        
        # Поле ввода пути
        self.path_edit = QLineEdit()
        entry_font = QFont("Consolas", 10)
        self.path_edit.setFont(entry_font)
        self.path_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.path_edit.setFixedHeight(25)
        top_row.addWidget(self.path_edit)
        
        # Кнопка отправки запроса
        self.send_button = QPushButton("Send")
        button_font = QFont("Arial", 10)
        self.send_button.setFont(button_font)
        self.send_button.setFixedWidth(80)
        self.send_button.clicked.connect(lambda: self.button_action())
        top_row.addWidget(self.send_button)
        
        main_layout.addLayout(top_row)
        
        # Тело запроса и ответ (в одну строку)
        content_layout = QHBoxLayout()
        
        # Поле для ввода тела запроса
        body_container = QVBoxLayout()
        body_label = QLabel("Body:")
        body_font = QFont("Consolas", 10)
        self.body_edit = ContextMenuTextEdit()
        self.body_edit.setFont(body_font)
        self.body_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.body_edit.setFixedHeight(300)  # Высота для текстового поля
        
        body_container.addWidget(body_label)
        body_container.addWidget(self.body_edit)
        
        content_layout.addLayout(body_container)
        
        # Поле для вывода ответа
        output_container = QVBoxLayout()
        output_label = QLabel("Response:")
        self.output_edit = QTextEdit()
        self.output_edit.setFont(body_font)
        self.output_edit.setReadOnly(True)
        self.output_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output_edit.setFixedHeight(300)
        
        output_container.addWidget(output_label)
        output_container.addWidget(self.output_edit)
        
        content_layout.addLayout(output_container)
        main_layout.addLayout(content_layout)
    
    def update_method_color(self):
        """Обновление цвета выпадающего списка в зависимости от выбранного метода"""
        method = self.method_combo.currentText()
        color = self.method_colors.get(method, "black")
        
        palette = self.method_combo.palette()
        palette.setColor(palette.WindowText, QColor(color))
        self.method_combo.setPalette(palette)
    
    def button_action(self):
        """Логика выполнения HTTP-запроса при нажатии кнопки Send"""
        # Сбор данных из полей ввода
        method = self.method_combo.currentText()
        path = self.path_edit.text().strip()
        body = self.body_edit.toPlainText().strip()
        base_url = self.window().findChild(QLineEdit, "base_url").text().strip() if hasattr(self.window(), 'findChild') else ""
        
        # Проверка наличия базового URL
        if not base_url:
            self.output_edit.setPlainText("❌ Укажите базовый адрес в верхнем поле")
            return
        
        # Формирование полного URL
        url = base_url.rstrip("/") + "/" + path.lstrip("/")
        
        # Выполнение запроса в зависимости от выбранного метода
        try:
            if method == "GET":
                resp = requests.get(url)
            elif method == "POST":
                resp = requests.post(url, data=body)
            elif method == "PUT":
                resp = requests.put(url, data=body)
            elif method == "DELETE":
                resp = requests.delete(url, data=body)
            else:
                resp = None
            
            # Вывод результата в правое текстовое поле
            if resp is not None:
                self.output_edit.setPlainText(f"Status: {resp.status_code}\n\n{resp.text}")
        except Exception as e:
            self.output_edit.setPlainText(f"❌ Ошибка: {e}")


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    def __init__(self):
        super().__init__()
        
        # Настройка шрифтов
        self.default_fonts = {
            "label": {"family": "Arial", "size": 10, "weight": "bold"},
            "combo": {"family": "Arial", "size": 10, "weight": "bold"},
            "entry": {"family": "Consolas", "size": 10},
            "button": {"family": "Arial", "size": 10},
            "body": {"family": "Consolas", "size": 10}
        }
        
        self.init_ui()
        self.load_fonts()
        self.load_data()
    
    def init_ui(self):
        self.setWindowTitle("REST Client GUI (20 блоков с прокруткой)")
        self.setGeometry(100, 100, 1200, 800)
        
        # Создание главного виджета и вкладок
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Вкладки
        tabs = QTabWidget()
        
        tab1 = QWidget()
        tab2 = QWidget()
        
        tabs.addTab(tab1, "REST Client")
        tabs.addTab(tab2, "Config")
        
        main_layout.addWidget(tabs)
        
        # Вкладка REST Client
        rest_layout = QVBoxLayout(tab1)
        
        # Верхняя панель с полем ввода базового URL
        top_row = QHBoxLayout()
        top_label = QLabel("Базовый URL:")
        label_font = QFont("Arial", 10, QFont.Bold)
        top_label.setFont(label_font)
        
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setObjectName("base_url")
        entry_font = QFont("Consolas", 10)
        self.base_url_edit.setFont(entry_font)
        
        # Кнопка сохранения
        btn_save_manual = QPushButton("Сохранить")
        button_font = QFont("Arial", 10)
        btn_save_manual.setFont(button_font)
        btn_save_manual.clicked.connect(self.save_data)
        
        top_row.addWidget(top_label)
        top_row.addWidget(self.base_url_edit, stretch=1)
        top_row.addWidget(btn_save_manual)
        
        rest_layout.addLayout(top_row)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        rest_layout.addWidget(separator)
        
        # Область прокрутки с блоками запросов
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(10)
        
        # Добавление блоков запросов
        self.blocks = []
        for i in range(TOTAL_ROWS):
            block = RESTBlock(i, self)
            self.scroll_layout.addWidget(block)
            self.blocks.append(block)
            
            # Горизонтальный разделитель между блоками
            if i < TOTAL_ROWS - 1:
                separator_row = QFrame()
                separator_row.setFrameShape(QFrame.HLine)
                separator_row.setFrameShadow(QFrame.Sunken)
                self.scroll_layout.addWidget(separator_row)
        
        scroll_area.setWidget(self.scroll_content)
        rest_layout.addWidget(scroll_area)
    
    def load_fonts(self):
        """Загрузка настроек шрифтов из файла или использование стандартных"""
        if not os.path.exists(SAVE_FILE):
            self.create_json_file()
        
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            fonts_data = data.get("fonts", {})
            for key, params in fonts_data.items():
                if key in self.default_fonts:
                    font_info = self.default_fonts[key]
                    font_info.update(params)
        except Exception as e:
            print(f"Ошибка при загрузке шрифтов: {e}")
    
    def create_json_file(self):
        """Создание пустого файла конфигурации"""
        default_data = {
            "fonts": self.default_fonts,
            "blocks": []
        }
        
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
    
    def save_data(self):
        """Сохранение текущих данных в файл"""
        data = {
            "fonts": self.default_fonts,
            "base_url": self.base_url_edit.text(),
            "blocks": []
        }
        
        # Сохраняем состояние блоков
        for block in self.blocks:
            block_data = {
                "method": block.method_combo.currentText(),
                "path": block.path_edit.text(),
                "body": block.body_edit.toPlainText()
            }
            data["blocks"].append(block_data)
        
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
    
    def load_data(self):
        """Загрузка данных из файла"""
        if not os.path.exists(SAVE_FILE):
            return
        
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Загружаем базовый URL
            base_url = data.get("base_url", "")
            self.base_url_edit.setText(base_url)
            
            # Загружаем состояние блоков
            blocks_data = data.get("blocks", [])
            for i, block_data in enumerate(blocks_data):
                if i < len(self.blocks):
                    block = self.blocks[i]
                    method = block_data.get("method", "GET")
                    path = block_data.get("path", "")
                    body = block_data.get("body", "")
                    
                    # Устанавливаем значения с задержкой, чтобы избежать проблем с отрисовкой
                    def set_block_data(block=block, method=method, path=path, body=body):
                        block.method_combo.setCurrentText(method)
                        block.path_edit.setText(path)
                        block.body_edit.setPlainText(body)
                    
                    # Используем однократный таймер для установки данных после отрисовки
                    QTimer.singleShot(10, set_block_data)
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
    
    def closeEvent(self, event):
        """Обработчик закрытия окна (автосохранение)"""
        self.save_data()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())