import sys
import os
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# 线程类，用于后台处理大文件
class FileProcessorThread(QThread):
    progress = pyqtSignal(int)  # 信号，用于进度条更新

    def __init__(self, input_file, output_dir):
        super().__init__()
        self.input_file = input_file
        self.output_dir = output_dir

    def run(self):
        # 正则表达式模式，匹配词条、发音和中文解释
        pattern = re.compile(
            r'<div class="hwd">(.+?)</div>.*?'
            r'<span class="ipa">\[(.+?)\]</span>.*?'
            r'<span class="dcn">(.+?)</span>',
            re.DOTALL
        )

        with open(self.input_file, 'r', encoding='utf-8') as file:
            content = file.read()
            matches = pattern.findall(content)
            total_matches = len(matches)

            if total_matches == 0:
                self.progress.emit(100)
                return

            for i, match in enumerate(matches):
                word, pronunciation, translation = match
                filename = re.sub(r'[\\/*?:"<>|]', "_", word.strip())

                with open(os.path.join(self.output_dir, f"{filename}.txt"), 'w', encoding='utf-8') as word_file:
                    word_file.write(f"Word: {word.strip()}\n")
                    word_file.write(f"Pronunciation: [{pronunciation.strip()}]\n")
                    word_file.write(f"Translation: {translation.strip()}\n")

                # 进度条更新
                self.progress.emit(int((i + 1) / total_matches * 100))

class DictionaryApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # 界面布局
        self.setWindowTitle('Dictionary Processor')
        self.setGeometry(200, 200, 400, 200)
        layout = QVBoxLayout()

        # 输入路径
        self.input_label = QLabel('输入文件路径:')
        self.input_path = QLineEdit(self)
        self.input_browse = QPushButton('浏览', self)
        self.input_browse.clicked.connect(self.browse_input_file)

        # 输出路径
        self.output_label = QLabel('输出目录:')
        self.output_path = QLineEdit(self)
        self.output_browse = QPushButton('浏览', self)
        self.output_browse.clicked.connect(self.browse_output_dir)

        # 开始按钮
        self.start_button = QPushButton('开始处理', self)
        self.start_button.clicked.connect(self.start_processing)

        # 进度条
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # 布局控件
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_path)
        layout.addWidget(self.input_browse)
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_path)
        layout.addWidget(self.output_browse)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def browse_input_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择输入文件", "", "Text Files (*.txt)")
        if file_name:
            self.input_path.setText(file_name)

    def browse_output_dir(self):
        dir_name = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_name:
            self.output_path.setText(dir_name)

    def start_processing(self):
        input_file = self.input_path.text()
        output_dir = self.output_path.text()

        if not input_file or not output_dir:
            QMessageBox.warning(self, "错误", "请输入有效的输入文件和输出目录路径")
            return

        # 禁用按钮
        self.start_button.setEnabled(False)

        # 创建并启动后台处理线程
        self.thread = FileProcessorThread(input_file, output_dir)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_finished(self):
        QMessageBox.information(self, "完成", "文件处理完成！")
        self.start_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DictionaryApp()
    window.show()
    sys.exit(app.exec_())
