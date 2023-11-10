from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout,  \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
    QVBoxLayout, QComboBox, QTextEdit, QMessageBox, QStatusBar
from PyQt6.QtGui import QAction
import sys
from datetime import datetime
from dbconnection import DBConnection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Tracker System")
        self.setMinimumSize(400, 500)

        file_menu_item = self.menuBar().addMenu("&File")

        add_time_action = QAction("Add Time", self)
        add_time_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_time_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Project", "Date", "Time Spent"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Add status bar with elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

        self.load_data()

    def load_data(self):
        # DB Connection
        connection = DBConnection().connect()
        result = connection.execute("select ID, project, date, time_spent from recorded_time")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for col_number, col_data in enumerate(row_data):
                self.table.setItem(row_number, col_number, QTableWidgetItem(str(col_data)))
        connection.close()
        self.table.hideColumn(0)

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def cell_clicked(self, row, column):
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit)
        delete_button = QPushButton("Remove")
        delete_button.clicked.connect(self.delete)
        status_button = QPushButton("Mark as invoiced")
        status_button.clicked.connect(self.status)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)
        self.statusbar.addWidget(status_button)

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def status(self):
        dialog = StatusDialog()
        dialog.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Time")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get clients and list out
        self.client = QComboBox()
        connection = DBConnection().connect()
        result = connection.execute("select id, client_name from clients")
        for row_number, row_data in enumerate(result):
            self.client.addItem(row_data[1], row_data[0])

        layout.addWidget(self.client)

        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("Project")
        layout.addWidget(self.project_name)

        self.time_spent = QLineEdit()
        self.time_spent.setPlaceholderText("Time Spent")
        layout.addWidget(self.time_spent)

        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Notes")
        layout.addWidget(self.notes)

        button = QPushButton("Add Time")
        button.clicked.connect(self.add_time)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_time(self):
        client_id = self.client.currentData()
        name = self.project_name.text()
        time_spent = self.time_spent.text()
        notes = self.notes.toPlainText()

        connection = DBConnection().connect()
        connection.execute("INSERT INTO recorded_time (client_id, project, time_spent, notes) VALUES (?, ?, ?, ?)",
                       (client_id, name, time_spent, notes))
        connection.commit()
        connection.close()
        tracker_system.load_data()
        self.client.setCurrentIndex(0)
        self.project_name.setText('')
        self.time_spent.setText('')
        self.notes.setPlainText('')

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Time Entry")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        row_index = tracker_system.table.currentRow()

        # Get time ID from current row and pull data from db
        self.time_id = tracker_system.table.item(row_index, 0).text()

        connection = DBConnection().connect()
        result = connection.execute("select client_id, project, date, time_spent, notes from recorded_time where ID=?", (self.time_id, ))

        edit_entry = result.fetchone()

        # Get clients and list out
        self.client = QComboBox()
        connection = DBConnection().connect()
        result = connection.execute("select id, client_name from clients")
        current_client_index = 0
        for row_number, row_data in enumerate(result):
            self.client.addItem(row_data[1], row_data[0])
            # If this is the same client id as in our data then set the index id as row_number
            if row_data[0] == edit_entry['client_id']:
                current_client_index = row_number
        layout.addWidget(self.client)
        self.client.setCurrentIndex(current_client_index)

        self.project_name = QLineEdit(edit_entry['project'])
        layout.addWidget(self.project_name)

        self.time_spent = QLineEdit(str(edit_entry['time_spent']))
        layout.addWidget(self.time_spent)

        self.notes = QTextEdit()
        self.notes.setPlainText(edit_entry['notes'])
        layout.addWidget(self.notes)

        button = QPushButton("Update")
        button.clicked.connect(self.update_timeentry)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_timeentry(self):
        connection = DBConnection().connect()
        connection.execute("UPDATE recorded_time SET client_id = ?, project = ?, time_spent = ?, notes = ? WHERE ID = ?",
                       (self.client.currentData(), self.project_name.text(), self.time_spent.text(),
                        self.notes.toPlainText(), self.time_id))
        connection.commit()
        connection.close()
        tracker_system.load_data()
        self.close()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Time Entry")

        layout = QGridLayout()
        confirmation_message = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation_message, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_entry)

    def delete_entry(self):
        row_index = tracker_system.table.currentRow()

        # Get time ID from current row
        time_id = tracker_system.table.item(row_index, 0).text()

        connection = DBConnection().connect()
        connection.execute('DELETE FROM recorded_time WHERE id = ?', (time_id, ))
        connection.commit()
        connection.close()
        tracker_system.load_data()

        self.close()

        confirmation_message = QMessageBox()
        confirmation_message.setWindowTitle("Success")
        confirmation_message.setText(f"Your entry was deleted successfully")
        confirmation_message.exec()


class StatusDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Set time recording as invoiced")

        layout = QGridLayout()
        confirmation_message = QLabel("Are you sure you want to set this as invoiced?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation_message, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.update_invoice_status)

    def update_invoice_status(self):
        row_index = tracker_system.table.currentRow()

        # Get time ID from current row
        time_id = tracker_system.table.item(row_index, 0).text()

        connection = DBConnection().connect()
        connection.execute('UPDATE recorded_time SET invoiced=1 WHERE id = ?', (time_id, ))
        connection.commit()
        connection.close()
        tracker_system.load_data()

        self.close()

        confirmation_message = QMessageBox()
        confirmation_message.setWindowTitle("Success")
        confirmation_message.setText(f"Your time entry was updated as Invoiced")
        confirmation_message.exec()

sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook


app = QApplication(sys.argv)
tracker_system = MainWindow()
tracker_system.show()
sys.exit(app.exec())