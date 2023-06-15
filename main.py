import sys
from PyQt5.QtWidgets import QApplication
from explorer import Explorer


def main():
    app = QApplication(sys.argv)
    explorer = Explorer()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()