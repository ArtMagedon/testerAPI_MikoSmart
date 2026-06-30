import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QMessageBox,
)

from PyQt5.QtGui import QCloseEvent, QFont, QIcon

from tabs.rest_tab import RestTab
from tabs.settings_tab import SettingsTab


#сделать настройку шрифтов, перетаскивание блоков, переименование. сделать вохможность добавлять несколько вкладок

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Miko Smart API Tester")

        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "icon.png"
        )
        self.setWindowIcon(QIcon(icon_path))

        self.unsaved_changes = False
        self.default_fonts = {
            "tab_name": {"family": "Arial", "size": 10, "weight": "bold"},

            "domain_line": {"family": "Consolas", "size": 12, "weight": "normal"},
            "save_btn": {"family": "Consolas", "size": 12, "weight": "normal"},
            "add_btn": {"family": "Consolas", "size": 12, "weight": "normal"},

            "block_name": {"family": "Arial", "size": 10, "weight": "normal"},
            "method_selector": {"family": "Arial", "size": 10, "weight": "bold"},
            "url_line": {"family": "Consolas", "size": 10, "weight": "normal"},
            "status_code": {"family": "Consolas", "size": 10, "weight": "bold"},
            "send_btn": {"family": "Arial", "size": 10, "weight": "bold"},
            "body_box": {"family": "Consolas", "size": 10, "weight": "normal"},
            "response_box": {"family": "Consolas", "size": 10, "weight": "normal"}
        }

        self.config_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "config.json"
        )

        rest_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data.json"
        )

        self.load_config()

        self.setMinimumSize(800, 350)

        geometry = self.config.get("geometry")
        if geometry and geometry != "":
            self.restoreGeometry(bytes.fromhex(geometry))

        self.tabs = QTabWidget()

        self.rest_tab = RestTab(rest_file, self.config["fonts"])
        self.settings_tab = SettingsTab()

        self.tabs.addTab(self.rest_tab, "REST")
        self.tabs.addTab(self.settings_tab, "Настройки")

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

        self.apply_fonts()

    def apply_fonts(self):
        self.tabs.tabBar().setFont(self.make_font(self.config["fonts"],"tab_name"))  # type: ignore

    def load_config(self):
        if not os.path.exists(self.config_file):
            self.config = {
                "geometry": "",
                "tabs": {},
                "fonts": {}
            }
            return
        with open(self.config_file, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def make_font(self, fonts, key):
        font = fonts[key]
        weight = QFont.Bold if font["weight"] == "bold" else QFont.Normal
        return QFont(font["family"], font["size"], weight)

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def save_data(self):
        self.save_config()
        self.rest_tab.save_to_file()

    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(
            self, 
            'Exit', 
            'Save changes?',
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )
        
        if reply == QMessageBox.Save:
            self.config["geometry"] = bytes(self.saveGeometry()).hex()
            self.save_data()
            event.accept()
        elif reply == QMessageBox.Discard:
            event.accept()
        else: # Нажали "Отмена"
            event.ignore()



app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec_())
