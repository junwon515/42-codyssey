import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QGridLayout, QLineEdit, QPushButton, QWidget


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Calculator')
        self.initUI()
        self.reset()

    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)
        self.setStyleSheet('background-color: black;')

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(300)
        self.display.setStyleSheet(
            'background-color: black; color: white; border: none;'
        )
        self.display.setFont(QFont('Helvetica', 50))
        layout.addWidget(self.display, 0, 0, 1, 4)

        buttons = [
            ('AC', 'gray'),
            ('+/-', 'gray'),
            ('%', 'gray'),
            ('÷', 'orange'),
            ('7', 'dark'),
            ('8', 'dark'),
            ('9', 'dark'),
            ('×', 'orange'),
            ('4', 'dark'),
            ('5', 'dark'),
            ('6', 'dark'),
            ('−', 'orange'),
            ('1', 'dark'),
            ('2', 'dark'),
            ('3', 'dark'),
            ('+', 'orange'),
            ('0', 'dark2', 2),
            ('.', 'dark'),
            ('=', 'orange'),
        ]

        button_styles = {
            'gray': 'background-color: #A5A5A5; color: black; border-radius: 65px;',
            'orange': 'background-color: #FF9500; color: white; border-radius: 65px;',
            'dark': 'background-color: #333333; color: white; border-radius: 65px;',
            'dark2': 'background-color: #333333; color: white; border-radius: 65px; text-align: left; padding-left: 45px;',
        }

        row = 1
        col = 0

        for btn in buttons:
            text = btn[0]
            color = btn[1]
            colspan = btn[2] if len(btn) == 3 else 1

            button = QPushButton(text)
            button.setFixedSize(130 * colspan, 130)
            button.setFont(QFont('Helvetica', 25))
            button.setStyleSheet(button_styles[color])

            layout.addWidget(button, row, col, 1, colspan)
            col += colspan
            if col >= 4:
                col = 0
                row += 1

            button.clicked.connect(self.onButtonClick)

    def reset(self):
        self.current = ''
        self.operator = ''
        self.operand = None
        self.updateDisplay('0')

    def add(self):
        self.calculate()
        self.operator = '+'

    def subtract(self):
        self.calculate()
        self.operator = '-'

    def multiply(self):
        self.calculate()
        self.operator = '*'

    def divide(self):
        self.calculate()
        self.operator = '/'

    def equal(self):
        self.calculate()
        self.operator = ''

    def negative_positive(self):
        try:
            if self.current == '' and self.operand is not None:
                self.current = str(self.operand)
                self.operator = ''

            value = float(self.current)
            self.current = str(-value)
            self.updateDisplay(self.current)
        except Exception:
            self.updateDisplay('Error')

    def percent(self):
        try:
            if self.current == '' and self.operand is not None:
                self.current = str(self.operand)
                self.operator = ''

            value = float(self.current)
            self.current = str(round(value / 100, 6))
            self.updateDisplay(self.current)
        except Exception:
            self.updateDisplay('Error')

    def calculate(self):
        if self.current:
            try:
                if self.operand is not None and self.operator:
                    expression = f'{self.operand}{self.operator}{self.current}'
                    result = round(eval(expression), 6)
                    self.operand = result
                    self.current = str(result)
                    self.updateDisplay(self.current)
                else:
                    self.operand = float(self.current)
                self.current = ''
            except Exception:
                self.reset()
                self.updateDisplay('Error')

    def format_number(self, number_str):
        try:
            if '.' in number_str:
                if number_str.startswith('-'):
                    sign = '-'
                    number_str = number_str[1:]
                else:
                    sign = ''
                integer, decimal = number_str.split('.')
                formatted_integer = f'{int(integer):,}'
                return f'{sign}{formatted_integer}.{decimal}'
            else:
                return f'{int(number_str):,}'
        except Exception:
            return number_str

    def updateDisplay(self, number_str):
        length = len(number_str)
        formatted = self.format_number(number_str)

        if length <= 6:
            font_size = 50
        elif length <= 8:
            font_size = 40
        elif length <= 10:
            font_size = 30
        else:
            font_size = 20

        self.display.setFont(QFont('Helvetica', font_size))
        self.display.setText(formatted)

    def onButtonClick(self):
        button = self.sender()
        text = button.text()

        if text == 'AC':
            self.reset()
        elif text in '0123456789':
            if self.current == '':
                self.current = text
            else:
                self.current += text
            self.updateDisplay(self.current)
        elif text == '.':
            if '.' not in self.current:
                self.current += '.' if self.current else '0.'
                self.updateDisplay(self.current)
        elif text == '+':
            self.add()
        elif text == '−':
            self.subtract()
        elif text == '×':
            self.multiply()
        elif text == '÷':
            self.divide()
        elif text == '=':
            self.equal()
        elif text == '+/-':
            self.negative_positive()
        elif text == '%':
            self.percent()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    sys.exit(app.exec_())
