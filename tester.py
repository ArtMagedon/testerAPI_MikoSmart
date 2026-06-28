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

        self.file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "config_data.json"
        )

        self.load_data()

        self.setMinimumSize(800, 350)

        geometry = self.data["config"].get("geometry")
        if geometry:
            self.restoreGeometry(bytes.fromhex(geometry))

        self.tabs = QTabWidget()

        self.rest_tab = RestTab(self.data)
        self.settings_tab = SettingsTab(self.data)

        self.tabs.addTab(self.rest_tab, "REST")
        self.tabs.addTab(self.settings_tab, "Настройки")

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

    def load_data(self):
        if not os.path.exists(self.file):
            self.data = {
                "config": {
                    "main_url": "",
                },
                "data": []
            }
            return

        with open(self.file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def save_data(self):
        self.rest_tab.save_to_data()

        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def closeEvent(self, event: QCloseEvent):
        self.data["config"]["geometry"] = bytes(self.saveGeometry()).hex()
        self.save_data()
        event.accept()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec_())