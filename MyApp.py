import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QMessageBox, QGridLayout,
    QWidget, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QSpinBox
)
from PyQt5.QtCore import Qt

class Cell(QPushButton):
    def __init__(self, x, y):
        super().__init__()
        self.setFixedSize(30, 30)
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_revealed = False
        self.has_flag = False
        self.setStyleSheet("font-weight: bold;")

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton and not self.is_revealed:
            if not self.has_flag:
                self.setText("🚩")
                self.has_flag = True
            else:
                self.setText("")
                self.has_flag = False
        else:
            super().mousePressEvent(event)

class MinesweeperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minesweeper")
        self.setGeometry(100, 100, 600, 600)

        self.difficulty = "Easy"
        self.rows = 9
        self.cols = 9
        self.mines = 10

        self.init_main_menu()

    def init_main_menu(self):
        self.main_menu = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Minesweeper")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        start_btn = QPushButton("Start")
        start_btn.clicked.connect(self.start_game)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.show_settings)

        quit_btn = QPushButton("Quit")
        quit_btn.clicked.connect(QApplication.quit)

        layout.addWidget(title)
        layout.addWidget(start_btn)
        layout.addWidget(settings_btn)
        layout.addWidget(quit_btn)

        self.main_menu.setLayout(layout)
        self.setCentralWidget(self.main_menu)

    def show_settings(self):
        self.settings_menu = QWidget()
        layout = QVBoxLayout()

        self.difficulty_box = QComboBox()
        self.difficulty_box.addItems(["Easy", "Medium", "Hard", "Custom"])
        self.difficulty_box.setCurrentText(self.difficulty)

        self.rows_input = QSpinBox()
        self.rows_input.setRange(5, 30)
        self.rows_input.setValue(self.rows)

        self.cols_input = QSpinBox()
        self.cols_input.setRange(5, 30)
        self.cols_input.setValue(self.cols)

        self.mines_input = QSpinBox()
        self.mines_input.setRange(1, 300)
        self.mines_input.setValue(self.mines)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.init_main_menu)

        layout.addWidget(QLabel("Difficulty:"))
        layout.addWidget(self.difficulty_box)
        layout.addWidget(QLabel("Rows:"))
        layout.addWidget(self.rows_input)
        layout.addWidget(QLabel("Columns:"))
        layout.addWidget(self.cols_input)
        layout.addWidget(QLabel("Mines:"))
        layout.addWidget(self.mines_input)
        layout.addWidget(save_btn)
        layout.addWidget(back_btn)

        self.settings_menu.setLayout(layout)
        self.setCentralWidget(self.settings_menu)

    def save_settings(self):
        self.difficulty = self.difficulty_box.currentText()
        self.rows = self.rows_input.value()
        self.cols = self.cols_input.value()
        self.mines = self.mines_input.value()
        self.init_main_menu()

    def start_game(self):
        if self.difficulty == "Easy":
            self.rows, self.cols, self.mines = 9, 9, 10
        elif self.difficulty == "Medium":
            self.rows, self.cols, self.mines = 12, 12, 20
        elif self.difficulty == "Hard":
            self.rows, self.cols, self.mines = 16, 16, 40

        self.board_widget = QWidget()
        layout = QVBoxLayout()
        self.grid = QGridLayout()
        layout.addLayout(self.grid)
        self.board_widget.setLayout(layout)

        self.cells = {}
        for x in range(self.rows):
            for y in range(self.cols):
                cell = Cell(x, y)
                cell.clicked.connect(lambda _, cx=x, cy=y: self.reveal_cell(cx, cy))
                self.grid.addWidget(cell, x, y)
                self.cells[(x, y)] = cell

        mine_positions = random.sample(list(self.cells.keys()), self.mines)
        for pos in mine_positions:
            self.cells[pos].is_mine = True

        self.setCentralWidget(self.board_widget)

    def reveal_cell(self, x, y):
        cell = self.cells[(x, y)]
        if cell.is_revealed or cell.has_flag:
            return

        cell.is_revealed = True
        if cell.is_mine:
            cell.setText("💣")
            cell.setStyleSheet("background-color: red;")
            self.end_game(False)
        else:
            mines_around = self.count_adjacent_mines(x, y)
            if mines_around > 0:
                cell.setText(str(mines_around))
            cell.setStyleSheet("background-color: lightgray;")
            if mines_around == 0:
                for nx in range(x - 1, x + 2):
                    for ny in range(y - 1, y + 2):
                        if (nx, ny) != (x, y) and (nx, ny) in self.cells:
                            self.reveal_cell(nx, ny)
            if self.check_win():
                self.end_game(True)

    def count_adjacent_mines(self, x, y):
        count = 0
        for nx in range(x - 1, x + 2):
            for ny in range(y - 1, y + 2):
                if (nx, ny) in self.cells and self.cells[(nx, ny)].is_mine:
                    count += 1
        return count

    def check_win(self):
        for cell in self.cells.values():
            if not cell.is_mine and not cell.is_revealed:
                return False
        return True

    def end_game(self, won):
        for cell in self.cells.values():
            cell.setEnabled(False)
            if cell.is_mine:
                cell.setText("💣")
        msg = QMessageBox()
        msg.setWindowTitle("Game Over")
        msg.setText("You Win!" if won else "You Lost!")
        msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Close)
        msg.button(QMessageBox.Retry).setText("Restart")
        msg.button(QMessageBox.Close).setText("Main Menu")
        result = msg.exec_()
        if result == QMessageBox.Retry:
            self.start_game()
        else:
            self.init_main_menu()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MinesweeperApp()
    window.show()
    sys.exit(app.exec_())