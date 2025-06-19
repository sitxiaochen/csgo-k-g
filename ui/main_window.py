from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
)
from core.fetcher import fetch_skin_data
from core.processor import extract_key_data
from core.analyzer import Analyzer
from core.utils import setup_logger

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = setup_logger()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("CSGO饰品分析助手")
        self.resize(600, 400)
        layout = QVBoxLayout()

        self.label = QLabel("请输入饰品链接：")
        self.input = QLineEdit()
        self.button = QPushButton("分析")
        self.result = QTextEdit()
        self.result.setReadOnly(True)

        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.button)
        layout.addWidget(self.result)
        self.setLayout(layout)

        self.button.clicked.connect(self.on_analyze)

    def on_analyze(self):
        skin_url = self.input.text().strip()
        if not skin_url:
            self.result.setText("请填写饰品链接！")
            return
        try:
            raw_data = fetch_skin_data(skin_url)
            df = extract_key_data(raw_data)
            is_good_buy, analysis = Analyzer.analyze_skin(df)
            output = (
                f"分析结论: {'值得购入' if is_good_buy else '不建议购入'}\n\n"
                f"{analysis}"
            )
            self.result.setText(output)
        except Exception as e:
            self.logger.error(f"分析失败: {e}")
            self.result.setText(f"分析失败: {e}")