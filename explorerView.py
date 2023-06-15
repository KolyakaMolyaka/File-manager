from PyQt5.QtWidgets import QListWidget, QAction, QMenu, QListWidgetItem, QMessageBox
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon
import os

class ExplorerView(QListWidget):
    def __init__(self):

        super().__init__()
        self.display()

    def display(self, sortion=None):
        if not sortion:
            sortion = {"key": lambda f: os.path.isdir(f), "reverse": True}

        try:
            files = os.listdir(os.getcwd())
        except PermissionError:
            # недостаточно прав, чтобы открыть папку
            QMessageBox.critical(self,
                                 "Critial",
                                 "Access denied",
                                 QMessageBox.Ok)
            os.chdir("../")
            return

        self.clear() # очистка прошлых файлов
        files.sort(key=sortion["key"], reverse=sortion["reverse"])

        for file in files:
            filename, extension = os.path.splitext(file)
            item = QListWidgetItem()
            item.setText(file)
            if not extension:
                if os.path.isdir(file):
                    item.setIcon(QIcon(":folder.png"))
            else:
                icon = extension[1:] # убираем точку из расширения
                item.setIcon(QIcon(f":{icon}.svg"))

            self.addItem(item)


