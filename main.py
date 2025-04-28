import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QGridLayout
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VZapret")
        self.setGeometry(100, 100, 400, 300)

        # Главный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Надпись "Просто строка"
        self.label = QLabel("Статус работы:")
        self.label.setStyleSheet("font-size: 16px;")
        main_layout.addWidget(self.label)

        # Сетка для 9 кнопок (3x3)
        self.grid_layout = QGridLayout()

        # Создаем 9 кнопок
        self.buttons = []
        for i in range(9):
            row = i // 3
            col = i % 3
            button = QPushButton(f"{i + 1}")
            button.setStyleSheet("padding: 10px;")
            self.buttons.append(button)
            self.grid_layout.addWidget(button, row, col)

        main_layout.addLayout(self.grid_layout)

        # Кнопки "Запуск" и "Удаление"
        self.bottom_layout = QVBoxLayout()

        self.start_button = QPushButton("Запуск")
        self.start_button.setStyleSheet("padding: 10px; background-color: #4CAF50; color: white;")
        self.bottom_layout.addWidget(self.start_button)

        self.delete_button = QPushButton("Удаление")
        self.delete_button.setStyleSheet("padding: 10px; background-color: #f44336; color: white;")
        self.bottom_layout.addWidget(self.delete_button)

        main_layout.addLayout(self.bottom_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())