import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class CalculatorEngine:
    def __init__(self):
        self.expression = []

    def input(self, value):
        if value in ['+', '-', '*', '/']:
            self._add_operator(value)
        elif value == '.':
            self._add_dot()
        else:
            self._add_digit(value)

    def _add_operator(self, op):
        if self.expression:
            if self.expression[-1] in ['+', '-', '*', '/']:
                self.expression[-1] = op
            else:
                self.expression.append(op)

    def _add_dot(self):
        if self.expression and '.' not in self.expression[-1]:
            self.expression[-1] += '.'

    def _add_digit(self, digit):
        if not self.expression or self.expression[-1] in ['+', '-', '*', '/']:
            self.expression.append(digit)
        else:
            self.expression[-1] += digit

    def toggle_sign(self):
        if self.expression:
            if self.expression[-1].startswith('-'):
                self.expression[-1] = self.expression[-1][1:]
            else:
                self.expression[-1] = '-' + self.expression[-1]

    def calculate(self, percent=False):
        try:
            expr = ''.join(self.expression)
            result = eval(expr)
            if percent:
                result /= 100
            self.expression = [str(result)]
            return result
        except:
            return 'Error'

    def clear(self):
        self.expression = []

    def get_expression(self):
        return self.expression

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = CalculatorEngine()
        self.setWindowTitle('Calculator')
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)
        self.setStyleSheet('background-color: black;')

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(300)
        self.display.setStyleSheet('background-color: black; color: white; border: none;')
        self.display.setFont(QFont('Helvetica', 50))
        layout.addWidget(self.display, 0, 0, 1, 4)

        buttons = [
            ('AC', 'gray'), ('+/-', 'gray'), ('%', 'gray'), ('÷', 'orange'),
            ('7', 'dark'), ('8', 'dark'), ('9', 'dark'), ('×', 'orange'),
            ('4', 'dark'), ('5', 'dark'), ('6', 'dark'), ('−', 'orange'),
            ('1', 'dark'), ('2', 'dark'), ('3', 'dark'), ('+', 'orange'),
            ('0', 'dark2', 2), ('.', 'dark'), ('=', 'orange')
        ]

        row = 1
        col = 0

        for btn in buttons:
            text = btn[0]
            color = btn[1]
            colspan = btn[2] if len(btn) == 3 else 1

            button = QPushButton(text)
            button.setFixedSize(130 * colspan, 130)
            button.setFont(QFont('Helvetica', 25))
            button.setStyleSheet(self.buttonStyle(color))

            layout.addWidget(button, row, col, 1, colspan)
            col += colspan
            if col >= 4:
                col = 0
                row += 1

            button.clicked.connect(self.onButtonClick)

    def buttonStyle(self, color):
        if color == 'gray':
            return 'background-color: #A5A5A5; color: black; border-radius: 65px;'
        elif color == 'orange':
            return 'background-color: #FF9500; color: white; border-radius: 65px;'
        elif color == 'dark':
            return 'background-color: #333333; color: white; border-radius: 65px;'
        elif color == 'dark2':
            return 'background-color: #333333; color: white; border-radius: 65px; text-align: left; padding-left: 45px;'

    def onButtonClick(self):
        button = self.sender()
        text = button.text()

        if text == 'AC':
            self.engine.clear()
        elif text == '+/-':
            self.engine.toggle_sign()
        elif text == '%':
            result = self.engine.calculate(percent=True)
            if result == 'Error':
                self.display.setText('Error')
                return
        elif text == '=':
            result = self.engine.calculate()
            if result == 'Error':
                self.display.setText('Error')
                return
        elif text in ['+', '−', '×', '÷']:
            symbol = self.operatorToSymbol(text)
            self.engine.input(symbol)
        else:
            self.engine.input(text)

        self.updateDisplay()

    def updateDisplay(self):
        display_expr = ''
        for item in self.engine.get_expression():
            if item in ['+', '-', '*', '/']:
                display_expr += self.symbolToDisplay(item)
            else:
                display_expr += self.format_number(item)
        self.display.setText(display_expr)

        if len(display_expr) > 12:
            self.display.setFont(QFont('Helvetica', 25))
        elif len(display_expr) > 6:
            self.display.setFont(QFont('Helvetica', 35))
        else:
            self.display.setFont(QFont('Helvetica', 50))

    def operatorToSymbol(self, op):
        return {
            '+': '+',
            '−': '-',
            '×': '*',
            '÷': '/'
        }[op]

    def symbolToDisplay(self, op):
        return {
            '+': '+',
            '-': '−',
            '*': '×',
            '/': '÷'
        }[op]

    def format_number(self, number_str):
        try:
            if '.' in number_str:
                integer, decimal = number_str.split('.')
                return f'{int(integer):,}.{decimal}'
            else:
                return f'{int(number_str):,}'
        except:
            return number_str


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    sys.exit(app.exec_())