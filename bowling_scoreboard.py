import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QAbstractItemView, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel
from PyQt6.QtGui import QValidator
from PyQt6.QtCore import Qt

class InputValidator(QValidator):
    """Custom validator for the input field

    Args:
        QValidator (Object): Standard QLineEdit validator
    """
    def validate(self, input, index):
        if input in {"x", "X", "/", ""}:
            return QValidator.State.Acceptable, input, index
        
        if input.isdigit() and int(input) in range(10):
            return QValidator.State.Acceptable, input, index

        return QValidator.State.Invalid, input, index

class BowlingScoreboard(QMainWindow):
    """Main class

    Args:
        QMainWindow (Object): Main window widget
    """
    def __init__(self):
        super().__init__()
        # setting the window props
        self.setWindowTitle("Bowling Scoreboard")
        self.setGeometry(100, 100, 1050, 200)

        # setting the class cache
        self.table_data = [[[] for _ in range(10)], [0 for _ in range(10)]]
        self.current_frame = 0

        # initializing all UI components
        self.table_widget = QTableWidget(2, 10)
        self.label = QLabel("Please, enter scores below. Acceptable values: '0-9', '/', 'x', 'X'", alignment=Qt.AlignmentFlag.AlignHCenter)
        self.input_field = QLineEdit()
        self.button_reset = QPushButton("Reset")

        # hooking up UI components
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.input_field.setValidator(InputValidator())
        self.input_field.editingFinished.connect(self.shot)
        self.button_reset.clicked.connect(self.reset)

        # adding widgets to the layout
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        layout.addWidget(self.label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.button_reset)

        # setting up the central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def shot(self):
        """Method implementing a single shot based on the user input
        """
        # checking for the gameover situation
        if self.current_frame == 9 and len(self.table_data[0][self.current_frame]) == 3:
            self.label.setText("This game is over! To start over press 'Reset' button")
            return

        # cacheing the input field data
        input = self.input_field.text()
        self.input_field.clear()

        # checking for although valid but misused input values
        if input  == "" or (input == "/" and not len(self.table_data[0][self.current_frame])):
            return
        
        if input in {"x", "X"} and len(self.table_data[0][self.current_frame]) and self.current_frame < 9:
            return
        
        if input.isdigit() and len(self.table_data[0][self.current_frame]) and int(input) + int(self.table_data[0][self.current_frame][0]) >= 10:
            return

        # appending the current frame data with current input value
        self.table_data[0][self.current_frame].append(input)

        # checking if current input is a strike to auto-close the frame (not applicable for the frame 10)
        if input in {"x", "X"} and len(self.table_data[0][self.current_frame]) == 1 and self.current_frame < 9:
            self.table_data[0][self.current_frame].append("_")

        # auto-separating the current shot in the frame
        if len(self.table_data[0][self.current_frame]):
            input = " | ".join(self.table_data[0][self.current_frame])

        # rendering the current table view item (frame scores)
        frame_score_item = QTableWidgetItem(str(input))
        frame_score_item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        frame_score_item.flags()
        self.table_widget.setItem(0, self.current_frame, frame_score_item)

        # recalculating and re-rendering the total scores
        self.recalculate_total_score()

        # checking if the current frame can be closed
        if len(self.table_data[0][self.current_frame]) == 2 and self.current_frame < 9:
            self.current_frame += 1
        
        # checking for the gameover situation
        if self.current_frame == 9 and len(self.table_data[0][self.current_frame]) == 3:
            self.label.setText("This game is over! To start over press 'Reset' button")
            return
    
    def recalculate_total_score(self):
        """Method to recalculate the total scoreboard 
        """
        # calculating the base scores (within a frame only)
        for index, item in enumerate(self.table_data[0][:self.current_frame + 1]):
            if "/" in item or "x" in item or "X" in item:
                self.table_data[1][index] = 10
            else:
                self.table_data[1][index] = sum([int(element) for element in item])

        unpacked_table = [score for frame in self.table_data[0] for score in frame]
        extra_scores = []

        # calculating scores for extra shots
        for index, item in enumerate(unpacked_table):
            if item == "/":
                try:
                    extra_scores.append(unpacked_table[index + 1])
                except IndexError:
                    pass

            if item in {"x", "X"}:
                try:
                    extra_scores.append(unpacked_table[index + 2])
                    extra_scores[-1] += (unpacked_table[index + 3] if not unpacked_table[index + 3] == "_" else unpacked_table[index + 4])
                except IndexError:
                    pass

        # applying extra shots scores to base scores if applicable
        for index, item in enumerate(extra_scores):
            num = 0

            if "/" in item:
                extra_scores[index] = 10
                continue

            for char in item:
                if char.isdigit():
                    num += int(char)
                if char in {"x", "X"}:
                    num += 10
            extra_scores[index] = num
        
        extra_scores.reverse()
        
        # calculating final scores consecutively adding totals
        for index, score in enumerate(self.table_data[1][:self.current_frame + 1]):
            frame = self.table_data[0][index]

            if "/" in frame or "x" in frame or "X" in frame:
                try:
                    score += extra_scores.pop()
                except IndexError:
                    pass

            self.table_data[1][index] = score + self.table_data[1][index - 1] if index else score

            # rendering total scores
            total_score_item = QTableWidgetItem(str(self.table_data[1][index]))
            total_score_item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.table_widget.setItem(1, index, total_score_item)
        
        # dropping total scores cache
        self.table_data[1] = [0 for _ in range(10)]

    def reset(self):
        """Reset button method
        """
        self.table_data = [[[] for _ in range(10)], [0 for _ in range(10)]]
        self.current_frame = 0
        self.table_widget.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BowlingScoreboard()
    window.show()
    window.table_widget.resizeRowsToContents()
    sys.exit(app.exec())