from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout
)


class SettingsTab(QWidget):

    def __init__(self, data):
        super().__init__()

        self.data = data

        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel("Настройки приложения")
        )

        layout.addStretch()