import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QLineEdit
from FinanceManager import FinanceManager
import sqlite3

import os #OMG
#workkkkkkkkkkkkkkk


class WelcomePage(QDialog):
    def __init__(self):
        super(WelcomePage, self).__init__()
        loadUi("welcome.ui", self)
        self.update()

        self.login.clicked.connect(self.gotologin)
        self.signup.clicked.connect(self.gotosignup)
        self.setStyleSheet("background-image: url('welcome2.png');")

    def gotologin(self):
        login = LoginPage()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)


    def gotosignup(self):
        signup = SignupPage()
        widget.addWidget(signup)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class LoginPage(QDialog):
    def __init__(self):
        super(LoginPage, self).__init__()
        loadUi("login.ui", self)
        self.PasswordLine.setEchoMode(QLineEdit.Password)
        self.login_btn.clicked.connect(self.loginfunction)
        self.setStyleSheet("background-image: url('2.png');background-size:800px,600px;")

    def loginfunction(self):
        user = self.EmailLine.text()
        password = self.PasswordLine.text()

        if len(user) == 0 or len(password) == 0:
            self.label_invalid_line.setText("Please input fields.")
        else:
            try:
                conn = sqlite3.connect("coinkeeper.db")
                cur = conn.cursor()
                query = 'SELECT password FROM users WHERE username=\'' + user + "\'"
                cur.execute(query)
                result_pass = cur.fetchone()
                conn.commit()
                conn.close()
                if result_pass and result_pass[0] == password:
                    print("Logged in")

                    # Create an instance of FinanceManager

                    #finance_manager.show()
                    os.system(f"python FinanceManager.py")

                    self.error.setText("")  # Reset error label
                else:
                    self.error.setText("Invalid username or password")
            except sqlite3.Error as e:
                print(f"SQLite error: {e}")

class SignupPage(QDialog):
    def __init__(self):
        super(SignupPage, self).__init__()
        loadUi("signup.ui", self)
        self.Password_line.setEchoMode(QLineEdit.Password)
        self.Password_confirm.setEchoMode(QLineEdit.Password)
        self.create_btn.clicked.connect(self.signupfunction)
        self.setStyleSheet("background-image: url('2.png');")

    def signupfunction(self):
        user = self.Email_line.text()
        password = self.Password_line.text()
        password_con = self.Password_confirm.text()

        if len(user) == 0 or len(password) == 0 or len(password_con) == 0:
            self.label_invalid_line.setText("Please input fields.")
        elif password != password_con:
            self.error.setText("Password do not match.")
        else:
            conn = sqlite3.connect("coinkeeper.db")
            cur = conn.cursor()

            user_info = [user, password]
            cur.execute('INSERT INTO users(username,password) VALUES (?,?)', user_info)
            conn.commit()
            conn.close()
            print("Created")

app = QApplication(sys.argv)
welcome = WelcomePage()
#finance_manager = FinanceManager()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedWidth(800)
widget.setFixedHeight(600)
widget.show()



sys.exit(app.exec_())


