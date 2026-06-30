from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout
)


class SettingsTab(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel("Настройки приложения")
        )

        layout.addStretch()