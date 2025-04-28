import os
import sys
import ctypes
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QLabel, QTextEdit, QHBoxLayout, QGridLayout
)
from PyQt6.QtCore import Qt, QProcess, pyqtSignal, QObject


class ConsoleOutput(QObject):
    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(text)


class BatLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VZapret")
        self.setGeometry(100, 100, 800, 600)

        self.bat_files = []
        self.selected_server = None
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.main_bat = os.path.join(self.script_dir, "service_install.bat")
        self.process = None

        self.init_ui()
        self.check_admin()
        self.scan_bat_files()
        self.start_bat_process()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Консольный вывод
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            background-color: black;
            color: white;
            font-family: Consolas;
            font-size: 12px;
        """)
        layout.addWidget(self.console, 3)

        # Панель выбора сервера
        server_panel = QWidget()
        server_layout = QVBoxLayout()
        server_panel.setLayout(server_layout)

        self.server_label = QLabel("Выберите сервер:")
        server_layout.addWidget(self.server_label)

        self.buttons_container = QWidget()
        self.buttons_layout = QGridLayout()
        self.buttons_container.setLayout(self.buttons_layout)
        server_layout.addWidget(self.buttons_container)

        layout.addWidget(server_panel, 1)

        # Панель управления
        control_panel = QWidget()
        control_layout = QHBoxLayout()
        control_panel.setLayout(control_layout)

        self.launch_btn = QPushButton("Запустить (Enter)")
        self.launch_btn.setEnabled(False)
        self.launch_btn.clicked.connect(self.confirm_launch)
        control_layout.addWidget(self.launch_btn)

        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.clicked.connect(self.stop_process)
        control_layout.addWidget(self.stop_btn)

        layout.addWidget(control_panel)

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def check_admin(self):
        if not self.is_admin():
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()

    def scan_bat_files(self):
        try:
            self.bat_files = [
                f for f in os.listdir(self.script_dir)
                if f.endswith(".bat")
                   and not f.startswith(("service", "check_updates"))
            ]

            # Очистка старых кнопок
            for i in reversed(range(self.buttons_layout.count())):
                self.buttons_layout.itemAt(i).widget().setParent(None)

            # Создание кнопок выбора
            for i, bat_file in enumerate(self.bat_files, 1):
                btn = QPushButton(f"{i}. {bat_file}")
                btn.clicked.connect(lambda _, x=i: self.select_server(x))
                row = (i - 1) // 3
                col = (i - 1) % 3
                self.buttons_layout.addWidget(btn, row, col)

        except Exception as e:
            self.log_error(f"Ошибка сканирования: {str(e)}")

    def start_bat_process(self):
        """Запуск основного bat-файла"""
        if not os.path.exists(self.main_bat):
            self.log_error("Основной bat-файл не найден!")
            return

        try:
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.read_output)
            self.process.readyReadStandardError.connect(self.read_output)

            # Перенаправляем вывод консоли
            sys.stdout = ConsoleOutput()
            sys.stdout.text_written.connect(self.console.append)

            self.process.start("cmd.exe", ["/k", self.main_bat, "admin"])
            self.log_message("Консоль запущена. Выберите сервер...")

        except Exception as e:
            self.log_error(f"Ошибка запуска: {str(e)}")

    def select_server(self, choice):
        """Выбор сервера (отправка цифры в консоль)"""
        self.selected_server = choice
        self.launch_btn.setEnabled(True)

        # Отправляем 'n' для пропуска обновлений
        self.process.write(b'n\n')

        # Отправляем выбранный номер
        self.process.write(f"{choice}\n".encode())
        self.log_message(f"Выбран сервер {choice}. Нажмите 'Запустить'")

    def confirm_launch(self):
        """Подтверждение запуска (отправка Enter)"""
        if self.selected_server:
            self.process.write(b'\n')  # Отправляем Enter
            self.log_message(f"Запуск сервера {self.selected_server}...")
            self.launch_btn.setEnabled(False)

    def stop_process(self):
        """Остановка процесса"""
        if self.process:
            self.process.kill()
            self.log_message("Процесс остановлен")
            self.launch_btn.setEnabled(False)
            self.selected_server = None

    def read_output(self):
        """Чтение вывода консоли"""
        output = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        error = self.process.readAllStandardError().data().decode('utf-8', errors='replace')

        if output:
            self.console.append(output.strip())
        if error:
            self.console.append(f"Ошибка: {error.strip()}")

    def log_message(self, text):
        self.console.append(f"[SYSTEM] {text}")

    def log_error(self, text):
        self.console.append(f"[ERROR] {text}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BatLauncher()
    window.show()
    sys.exit(app.exec())