# ui/sm2_tab.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit

class ToolsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 示例 UI 元素（后续你可以放签名、验签、生成密钥等）
        self.info_label = QLabel("SM2 签名与验签工具")
        self.text_edit = QTextEdit()
        self.run_button = QPushButton("执行")

        # 添加到布局
        layout.addWidget(self.info_label)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

        # 绑定事件
        self.run_button.clicked.connect(self.run_sm2)

    def run_sm2(self):
        input_text = self.text_edit.toPlainText()
        # 这里调用实际的算法处理逻辑，放在 core/sm2_utils.py 中
        print(f"[SM2] 收到输入：{input_text}")