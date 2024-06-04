import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, \
    QHBoxLayout, QFormLayout, QListWidget, QSizePolicy, QMessageBox, QFrame
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

#workssss
#works2
#workkkkkkkkk21
class FinanceManager(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Expense and Income Manager")
        self.setGeometry(100, 100, 800, 600)

        # Create or connect to the SQLite database
        self.conn = sqlite3.connect("finance_data.db")
        self.create_tables()

        # Set initial balance to 0 (or any other value you prefer)
        # Set initial balance to None
        self.balance = None

        # Load initial data from the database
        self.load_data_from_database()

        # If balance is still None, set it to 0 (or any other default value)
        if self.balance is None:
            self.balance = 0
            self.save_balance_to_database()

        # Load initial data from the database


        self.setup_ui()
        self.load_balance_history_from_database()

        self.balance_history = []

    def load_data_from_database(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM finance_data ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                self.balance = row[1]
            else:
                # If no record found, initialize balance to 0 and save to database
                self.balance = 0
                cursor.execute("INSERT INTO finance_data (balance) VALUES (?)", (self.balance,))

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM expenses")
            rows = cursor.fetchall()
            self.expenses = [{"description": row[2], "amount": row[3],
                              "entry": f"{row[4]}: {row[2]} - {row[3]}" if row[4] is not None and row[
                                  4] != "None" else "Unknown"} for row in rows]
        self.load_balance_history_from_database()

    def load_balance_history_from_database(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM balance_history")
            rows = cursor.fetchall()
            self.balance_history = [row[1] for row in rows if row[1] is not None]

    def setup_ui(self):
        main_layout = QVBoxLayout()
        # Set gradient background
        gradient_palette = QPalette()
        gradient_palette.setColor(QPalette.Window, QColor(0xda, 0xd1, 0xec))  # #dad1ec
        gradient_palette.setColor(QPalette.WindowText, Qt.black)  # Text color is set to black
        self.setPalette(gradient_palette)

        # Frame for Balance Section
        balance_frame = QFrame(self)
        balance_frame.setFrameShape(QFrame.Panel)
        balance_frame.setFrameShadow(QFrame.Raised)
        balance_frame_layout = QHBoxLayout(balance_frame)

        # Balance Section
        balance_layout = QVBoxLayout()
        self.balance_label = QLabel(f"Balance: {self.balance}", self)
        self.balance_label.setStyleSheet("font:18px")
        balance_layout.addWidget(self.balance_label)

        add_balance_layout = QFormLayout()
        self.add_balance_input = QLineEdit(self)
        add_balance_layout.addRow("Add Balance:", self.add_balance_input)
        add_balance_button = QPushButton("Add", self)
        add_balance_button.clicked.connect(self.add_balance)
        add_balance_layout.addWidget(add_balance_button)
        balance_layout.addLayout(add_balance_layout)

        self.balance_history_list = QListWidget(self)
        self.balance_history_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        balance_layout.addWidget(self.balance_history_list)

        balance_frame_layout.addLayout(balance_layout)

        # Expenses Section
        expenses_layout = QVBoxLayout()
        self.expenses_label = QLabel("Expenses:", self)
        self.expenses_label.setStyleSheet("font:18px")
        expenses_layout.addWidget(self.expenses_label)

        add_expense_layout = QFormLayout()
        self.expense_description_input = QLineEdit(self)
        self.expense_amount_input = QLineEdit(self)
        add_expense_layout.addRow("Description:", self.expense_description_input)
        add_expense_layout.addRow("Amount:", self.expense_amount_input)
        add_expense_button = QPushButton("Add Expense", self)
        add_expense_button.clicked.connect(self.add_expense)
        add_expense_layout.addWidget(add_expense_button)
        expenses_layout.addLayout(add_expense_layout)

        balance_frame_layout.addLayout(expenses_layout)
        main_layout.addWidget(balance_frame)

        # Expenses List
        self.expenses_list = QListWidget(self)
        self.expenses_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set background color of the list
        list_palette = self.expenses_list.palette()
        list_palette.setColor(QPalette.Window, QColor(0x75, 0xb4, 0xe9))
        self.expenses_list.setPalette(list_palette)
        main_layout.addWidget(self.expenses_list)

        # Statistics Section
        self.fig, (self.ax_pie, self.ax_bar) = plt.subplots(1, 2, figsize=(10, 5))
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas)



        self.update_balance_label()
        self.update_statistics()
        self.update_expenses_list()

        # Update UI elements
        self.update_balance_label()
        self.update_statistics()
        self.update_expenses_list()
        self.update_balance_history_list()

        # Style for labels
        label_style = "font-weight: bold; font-size: 18px; color: #333;"

        self.balance_label.setStyleSheet(label_style)
        self.expenses_label.setStyleSheet(label_style)

        # Style for buttons
        button_style = "background-color: #3498db; color: white; padding: 8px 16px; font-size: 14px; border: none;"

        add_balance_button.setStyleSheet(button_style)
        add_expense_button.setStyleSheet(button_style)

        # Style for QListWidget
        list_style = "background-color: #ecf0f1; border: 1px solid #bdc3c7; padding: 5px;"

        self.balance_history_list.setStyleSheet(list_style)
        self.expenses_list.setStyleSheet(list_style)

        # Style for QFrame
        frame_style = "QFrame { background-color: #ffffff; border: 1px solid #bdc3c7; border-radius: 8px; margin: 10px; }"
        balance_frame.setStyleSheet(frame_style)


        # After creating self.fig, (self.ax_pie, self.ax_bar)
        self.ax_pie.set_title("Pie Chart")
        self.ax_bar.set_title("Bar Chart")

        # After creating self.canvas
        self.canvas.setMinimumSize(400, 200)

        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)



    def create_tables(self):
        # Create tables if they do not exist
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS finance_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    balance REAL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    finance_id INTEGER,
                    description TEXT,
                    amount REAL,
                    entry_time DATETIME,  -- Add this column for date and time
                    FOREIGN KEY (finance_id) REFERENCES finance_data (id)
                )
            ''')
            cursor.execute('''
                        CREATE TABLE IF NOT EXISTS balance_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            entry TEXT
                        )
                    ''')

    def add_balance(self):
        try:
            amount = float(self.add_balance_input.text())
            self.balance += amount
            self.update_balance_label()
            self.update_statistics()
            self.save_balance_to_database()
            self.update_balance_history(amount)  # Update balance history
            self.update_expenses_list()  # Add this line to update expenses list
        except ValueError:
            self.show_error_message("Invalid amount")

    def update_balance_history(self, amount):
        now = datetime.now()
        entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')}: Added {amount} to balance"
        self.balance_history.append(entry)
        self.update_balance_history_list()
        self.save_balance_history_to_database()

    def update_balance_history_list(self):
        self.balance_history_list.clear()
        for entry in self.balance_history:
            self.balance_history_list.addItem(entry)

    def save_balance_history_to_database(self):
        with self.conn:
            cursor = self.conn.cursor()

            # Clear existing data (optional, depends on your requirements)
            # cursor.execute("DELETE FROM balance_history")

            # Insert new entries
            for entry in self.balance_history:
                cursor.execute("INSERT INTO balance_history (entry) VALUES (?)", (entry,))

    def add_expense(self):
        description = self.expense_description_input.text()
        amount_str = self.expense_amount_input.text()

        if not description or not amount_str:
            self.show_error_message("Please fill in both description and amount.")
            return

        try:
            amount = float(amount_str)
            if amount > self.balance:
                self.show_error_message("Not enough balance.")
                return

            now = datetime.now()
            expense_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')}: {description} - {amount}"

            # Сохранение времени трат в базу данных
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO expenses (finance_id, description, amount, entry_time) VALUES (?, ?, ?, ?)",
                               (1, description, amount, now.strftime('%Y-%m-%d %H:%M:%S')))

            self.expenses.append({"description": description, "amount": amount, "entry": expense_entry})
            self.balance -= amount
            self.update_balance_label()
            self.update_statistics()
            #self.save_expense_to_database(description, amount)
            self.update_expenses_list()
            self.save_balance_to_database()

        except ValueError:
            self.show_error_message("Invalid amount")

    def update_balance_label(self):
        self.balance_label.setText(f"Balance: {self.balance}")

    def update_expenses_list(self):
        self.expenses_list.clear()
        for expense in self.expenses:
            entry_value = expense.get('entry')
            time_str = entry_value if entry_value is not None else 'Unknown'

            if 'entry' in expense:
                self.expenses_list.addItem(f"{expense['entry']}")
            else:
                self.expenses_list.addItem(
                    f"Description: {expense.get('description', '')}, Amount: {expense.get('amount', '')}, Time: {time_str}"
                )

    def update_statistics(self):
        self.ax_pie.clear()
        self.ax_bar.clear()

        labels = [expense["description"] for expense in self.expenses]
        amounts = [expense["amount"] for expense in self.expenses]

        if labels and amounts:
            # Pie Chart
            self.ax_pie.pie(amounts, labels=labels, autopct='%1.1f%%', startangle=90)
            self.ax_pie.axis('equal')  # Equal aspect ratio ensures that the pie is drawn as a circle.

            # Bar Chart
            x = np.arange(len(labels))
            self.ax_bar.bar(x, amounts, color='blue')
            self.ax_bar.set_xticks(x)
            self.ax_bar.set_xticklabels(labels, rotation=45, ha='right')

            self.canvas.draw()

    def update_bar_chart(self):
        self.bar_chart_canvas.figure.clear()
        ax_bar = self.bar_chart_canvas.figure.add_subplot(111)

        categories = [expense["description"] for expense in self.expenses]
        amounts = [expense["amount"] for expense in self.expenses]

        if categories and amounts:
            bars = ax_bar.bar(categories, amounts, color='blue')
            self.bar_chart_label.setText("Expenses Bar Chart:")
            self.bar_chart_canvas.draw()

    def save_balance_to_database(self):
        print(f"Saving balance to database: {self.balance}")  # Добавим вывод для отладки

        # Save the current balance to the database
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE finance_data SET balance = ? WHERE id = (SELECT MAX(id) FROM finance_data)",
                           (self.balance,))

    def save_expense_to_database(self, description, amount):
        # Save the current expense to the database
        with self.conn:
            cursor = self.conn.cursor()

            # Save the expense
            cursor.execute("INSERT INTO expenses (finance_id, description, amount, entry_time) VALUES (?, ?, ?, ?)",
                           (1, description, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

            # Save the updated balance after subtracting the expense
            cursor.execute("UPDATE finance_data SET balance = ? WHERE id = (SELECT MAX(id) FROM finance_data)",
                           (self.balance,))

    def show_error_message(self, message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setText("Error")
        error_box.setInformativeText(message)
        error_box.setWindowTitle("Error")
        error_box.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    finance_manager = FinanceManager()
    finance_manager.load_balance_history_from_database()
    finance_manager.show()
    sys.exit(app.exec_())