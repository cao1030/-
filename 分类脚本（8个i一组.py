import sys
import os
import re
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# 线程类，用于后台分类文件
class FileClassifierThread(QThread):
    progress = pyqtSignal(int)  # 信号，用于进度条更新

    def __init__(self, input_dir, output_dir):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir

    def run(self):
        files = [f for f in os.listdir(self.input_dir) if os.path.isfile(os.path.join(self.input_dir, f))]
        total_files = len(files)

        if total_files == 0:
            self.progress.emit(100)
            return

        for i, file in enumerate(files):
            self.classify_file(file)

            # 更新进度条
            self.progress.emit(int((i + 1) / total_files * 100))

    def classify_file(self, filename):
        name, _ = os.path.splitext(filename)
        char_count = len(re.sub(r'\s', '', name))  # 不计空格的字符长度
        group = (char_count - 1) // 8 * 8 + 1
        group_folder = f"{group}-{group + 7}"

        last_8_chars = re.sub(r'\s', '', name)[-8:]  # 获取最后 8 个字符，去掉空格

        # 构建子目录路径
        sub_dir = self.build_sub_dirs(last_8_chars)

        # 创建完整输出路径
        output_path = os.path.join(self.output_dir, group_folder, *sub_dir, filename)

        # 创建目录并移动文件
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        shutil.copy(os.path.join(self.input_dir, filename), output_path)

    def build_sub_dirs(self, last_8_chars):
        # 创建二级及以下目录，每个字符对应一个目录，数字、字母和其他字符
        return [char for char in last_8_chars]

class ClassifierApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # 界面布局
        self.setWindowTitle('File Classifier')
        self.setGeometry(200, 200, 400, 200)
        layout = QVBoxLayout()

        # 输入文件夹路径
        self.input_label = QLabel('输入文件夹:')
        self.input_path = QLineEdit(self)
        self.input_browse = QPushButton('浏览', self)
        self.input_browse.clicked.connect(self.browse_input_dir)

        # 输出文件夹路径
        self.output_label = QLabel('输出文件夹:')
        self.output_path = QLineEdit(self)
        self.output_browse = QPushButton('浏览', self)
        self.output_browse.clicked.connect(self.browse_output_dir)

        # 开始按钮
        self.start_button = QPushButton('开始分类', self)
        self.start_button.clicked.connect(self.start_classification)

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

    def browse_input_dir(self):
        dir_name = QFileDialog.getExistingDirectory(self, "选择输入文件夹")
        if dir_name:
            self.input_path.setText(dir_name)

    def browse_output_dir(self):
        dir_name = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if dir_name:
            self.output_path.setText(dir_name)

    def start_classification(self):
        input_dir = self.input_path.text()
        output_dir = self.output_path.text()

        if not input_dir or not output_dir:
            QMessageBox.warning(self, "错误", "请输入有效的输入文件夹和输出文件夹路径")
            return

        # 禁用按钮
        self.start_button.setEnabled(False)

        # 创建并启动后台处理线程
        self.thread = FileClassifierThread(input_dir, output_dir)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_finished(self):
        QMessageBox.information(self, "完成", "文件分类完成！")
        self.start_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ClassifierApp()
    window.show()
    sys.exit(app.exec_())
