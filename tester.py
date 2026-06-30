import sys
import os
import json

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTabWidget,
)

from PyQt5.QtGui import QCloseEvent

from tabs.rest_tab import RestTab
from tabs.settings_tab import SettingsTab


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

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
        if geometry and geometry !="":
            self.restoreGeometry(bytes.fromhex(geometry))

        self.tabs = QTabWidget()

        self.rest_tab = RestTab(rest_file)
        self.settings_tab = SettingsTab()

        self.tabs.addTab(self.rest_tab, "REST")
        self.tabs.addTab(self.settings_tab, "Настройки")

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

    def load_config(self):
        if not os.path.exists(self.config_file):
            self.config = {
                "geometry": "",
                "tabs": {}
            }
            return
        with open(self.config_file, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def save_data(self):
        self.save_config()
        self.rest_tab.save_to_file()

    

    def closeEvent(self, event: QCloseEvent):
        self.config["geometry"] = bytes(self.saveGeometry()).hex()
        self.save_data()
        event.accept()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec_())
