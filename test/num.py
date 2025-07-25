import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt


STEP = 1024
MIN_VALUE = 1024


class StepInputWidget(QWidget):
    def __init__(self, label_text=""):
        super().__init__()

        layout = QHBoxLayout()
        layout.setSpacing(5)

        # 减号按钮
        self.minus_button = QPushButton("-")
        self.minus_button.setFixedWidth(10)
        self._apply_button_style(self.minus_button)
        layout.addWidget(self.minus_button)

        # 数字输入框
        self.input = QLineEdit("1024")
        self.input.setFixedWidth(60)
        self.input.setAlignment(Qt.AlignCenter)
        self.input.setValidator(QIntValidator(MIN_VALUE, 999999))
        layout.addWidget(self.input)

        # 加号按钮
        self.plus_button = QPushButton("+")
        self.plus_button.setFixedWidth(10)
        self._apply_button_style(self.plus_button)
        layout.addWidget(self.plus_button)

        self.setLayout(layout)

        self.plus_button.clicked.connect(self.increment)
        self.minus_button.clicked.connect(self.decrement)

    def _apply_button_style(self, button):
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                color: #0078d7;  /* Windows 蓝 或改为 #1E90FF 更现代 */
            }
        """)

    def increment(self):
        try:
            value = int(self.input.text())
            value += STEP
            self.input.setText(str(value))
        except ValueError:
            self.input.setText(str(MIN_VALUE))

    def decrement(self):
        try:
            value = int(self.input.text())
            value = max(MIN_VALUE, value - STEP)
            self.input.setText(str(value))
        except ValueError:
            self.input.setText(str(MIN_VALUE))

    def get_value(self):
        try:
            return max(MIN_VALUE, int(self.input.text()))
        except ValueError:
            return MIN_VALUE


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RSA 参数设置")

        layout = QVBoxLayout()

        self.label1 = QLabel("输入框 1：")
        self.input_widget1 = StepInputWidget()
        layout.addWidget(self.label1)
        layout.addWidget(self.input_widget1)

        self.label2 = QLabel("输入框 2：")
        self.input_widget2 = StepInputWidget()
        layout.addWidget(self.label2)
        layout.addWidget(self.input_widget2)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())