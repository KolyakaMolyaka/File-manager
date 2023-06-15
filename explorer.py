import os
import shutil # копиравание
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QAction, QInputDialog, QMessageBox,
                             QListWidget,QMenu, QToolButton, QActionGroup, QListWidgetItem)
from PyQt5.QtGui import QIcon
from explorerView import ExplorerView
import resources # файл ресурсов с иконками

from PyQt5.QtCore import Qt, QEvent

class Explorer(QMainWindow):
    """Класс проводник, главное окно программы"""


    def __init__(self):
        super().__init__()
        self._initUI()

        self.copyBuffer = None # путь до файла/папки для копирования
        self.cutBuffer = None # путь до файла/папки для перемещения
        self.mostDeepFolder = os.getcwd() # путь до самой вложенной папки, до которой досмотрел пользователь
        self.nextFolderAct.setDisabled(True) # изначально пользователь находится в самом глубоком просмотренном каталоге
        self.ascendingTypeSort = True # изначально сортировка по возрастанию

        self.view.itemDoubleClicked.connect(self.open) # двойное нажатие по папке/файлу открывает её/его

        self.installEventFilter(self) # создание контекстного меню


    def _initUI(self):
        """Базовый UI"""

        # компоновщик
        self.hbox = QHBoxLayout(self)

        # представление
        self.view = ExplorerView()

        # создание тул-бара
        self._createToolBar()

        # включение пунктов тул-бара при выбоке пользователем папки/файла
        self.view.itemSelectionChanged.connect(lambda: self.openAct.setEnabled(True))
        self.view.itemSelectionChanged.connect(lambda: self.cutAct.setEnabled(True))
        self.view.itemSelectionChanged.connect(lambda: self.renameAct.setEnabled(True))
        self.view.itemSelectionChanged.connect(lambda: self.copyAct.setEnabled(True))
        self.view.itemSelectionChanged.connect(lambda: self.removeAct.setEnabled(True))

        # компановка виджетов
        self.hbox.addWidget(self.view)

        # настройка окна проводника
        self._windowConfiguration()


    def _windowConfiguration(self):
        """Базовая конфигурация главного окна проводника"""

        self.setWindowTitle("File manager")
        self.setWindowIcon(QIcon(":logo.png"))
        self.setGeometry(300, 300, 550, 350)

        # отображение окна
        self.ui = QWidget(self)
        self.ui.setLayout(self.hbox)
        self.setCentralWidget(self.ui)
        self.show()


    def _createToolBar(self):
        """Создание тул-бара"""

        self._createActions() # создание пуктов тул-бара

        # тул-бар
        self.toolBar = self.addToolBar("ToolBar")
        self.toolBar.setContextMenuPolicy(Qt.CustomContextMenu) # запретить закрыть тул-бар
        self.toolBar.setMovable(False) # запретить перемещать тул-бар

        # стрелочки вперёд, назад
        self.toolBar.addAction(self.prevFolderAct)
        self.toolBar.addAction(self.nextFolderAct)
        self.toolBar.addSeparator()

        # пункты открыть, переименовать
        self.toolBar.addAction(self.openAct)
        self.toolBar.addAction(self.renameAct)
        self.toolBar.addSeparator()

        # пункт обновить
        self.toolBar.addAction(self.refreshAct)
        self.toolBar.addSeparator()

        # пункты создать файл/папку
        self.toolBar.addAction(self.createFileAct)
        self.toolBar.addAction(self.createFolderAct)
        self.toolBar.addSeparator()

        # пункт удалить
        self.toolBar.addAction(self.removeAct)
        self.toolBar.addSeparator()

        # пункты копировать, вырезать, вставить
        self.toolBar.addAction(self.copyAct)
        self.toolBar.addAction(self.cutAct)
        self.toolBar.addAction(self.pasteAct)
        self.toolBar.addSeparator()

        # пункт поиска
        self.toolBar.addAction(self.searchAct)
        self.toolBar.addSeparator()


        # пункт сортировки
        self.sortBtn = QToolButton(self)
        self.sortBtn.setToolTip("Sort")
        self.sortBtn.setIcon(QIcon(":sort.png"))
        self.sortBtn.setPopupMode(QToolButton.MenuButtonPopup)
        self.sortMenu = QMenu()
        self.sortBtn.setMenu(self.sortMenu)
        self.sortMenu.addAction(self.sortByNameAct)
        self.sortMenu.addAction(self.sortBySizeAct)
        self.sortMenu.addAction(self.sortByTypeAct)
        self.sortMenu.addSeparator()
        self.sortMenu.addAction(self.sortByAscendingAct)
        self.sortMenu.addAction(self.sortByDescendingAct)
        self.toolBar.addWidget(self.sortBtn)


    def _createActions(self):
        """Создание пунктов меню, установка иконок, связывание со слотами"""
        self.createFileAct = QAction(self)
        self.createFolderAct = QAction(self)
        self.removeAct = QAction(self)
        self.copyAct = QAction(self)
        self.openAct = QAction(self)
        self.pasteAct = QAction(self)
        self.renameAct = QAction(self)
        self.refreshAct = QAction(self)
        self.cutAct = QAction(self)
        self.searchAct = QAction(self)
        self.prevFolderAct = QAction(self)
        self.nextFolderAct = QAction(self)


        self.sortByDescendingAct = QAction(self)
        self.sortByAscendingAct = QAction(self)
        self.sortByDescendingAct.setCheckable(True)
        self.sortByAscendingAct.setCheckable(True)
        self.sortByAscendingAct.setChecked(True)
        # группа Des/Asc
        self.sortByTypeAscDesGroup = QActionGroup(self)
        self.sortByTypeAscDesGroup.addAction(self.sortByDescendingAct)
        self.sortByTypeAscDesGroup.addAction(self.sortByAscendingAct)
        self.sortByTypeAscDesGroup.setExclusive(True)

        self.sortByNameAct = QAction(self)
        self.sortBySizeAct = QAction(self)
        self.sortByTypeAct = QAction(self)
        self.sortByNameAct.setCheckable(True)
        self.sortBySizeAct.setCheckable(True)
        self.sortByTypeAct.setCheckable(True)
        self.sortByNameAct.setChecked(True)
        # группа sortType
        self.sortByTypeFormatGroup = QActionGroup(self)
        self.sortByTypeFormatGroup.addAction(self.sortByNameAct)
        self.sortByTypeFormatGroup.addAction(self.sortBySizeAct)
        self.sortByTypeFormatGroup.addAction(self.sortByTypeAct)
        self.sortByTypeFormatGroup.setExclusive(True)

        self._customizeActions()
        self._createActionsConnections()


    def _createActionsToolTips(self):
        """Создание подсказок при наведении на пункт меню"""

        self.openAct.setToolTip("Open")
        self.createFolderAct.setToolTip("Create folder")
        self.createFileAct.setToolTip("Create file")
        self.removeAct.setToolTip("Delete")
        self.refreshAct.setToolTip("Update")
        self.pasteAct.setToolTip("Paste")
        self.copyAct.setToolTip("Copy")
        self.renameAct.setToolTip("Rename")
        self.cutAct.setToolTip("Cut")
        self.searchAct.setToolTip("Search")


    def _customizeActions(self):
        """Настройка внешнего вида пунктов меню"""

        # создание подсказок при наведении на пункты тул-барa
        self._createActionsToolTips()

        # иконки для стрелочек вперёд, назад
        self.prevFolderAct.setIcon(QIcon(":left-arrow.png"))
        self.nextFolderAct.setIcon(QIcon(":right-arrow.png"))

        # иконка открыть файл/папку, по умолчанию отключено (пока пользователь не выберет файл/папку)
        self.openAct.setIcon(QIcon(":open.png"))
        self.openAct.setDisabled(True)

        # иконки поиска, создания файла/папки, обновление содержимого проводника (в случае с поиском позволяет
        # отобразить содержимое папки вновь
        self.searchAct.setIcon(QIcon(":search.png"))
        self.createFileAct.setIcon(QIcon(":new-file.png"))
        self.createFolderAct.setIcon(QIcon(":new-folder.png"))
        self.refreshAct.setIcon(QIcon(":refresh.png"))

        # иконка вставить, по умолчанию отключено (пока пользователь не выберет файл/папку)
        self.pasteAct.setIcon(QIcon(":paste.png"))
        self.pasteAct.setDisabled(True)

        # иконка удалить, по умолчанию отключено (пока пользователь не выберет файл/папку)
        self.removeAct.setIcon(QIcon(":remove.png"))
        self.removeAct.setDisabled(True)

        # иконка копировать, по умолчанию отключено (пока пользователь не выберет файл/папку)
        self.copyAct.setIcon(QIcon(":copy.png"))
        self.copyAct.setDisabled(True)

        # иконка вставить, по умолчанию отключено (пока пользователь не скопирует или вырежет файл)
        self.cutAct.setIcon(QIcon(":cut.png"))
        self.cutAct.setDisabled(True)

        # иконка переименовать, по умолчанию отключено (пока пользователь не выберет файл/папку)
        self.renameAct.setIcon(QIcon(":rename.png"))
        self.renameAct.setDisabled(True)

        # иконка и название сортировки по возрастанию и убыванию
        self.sortByAscendingAct.setText("Ascending")
        self.sortByAscendingAct.setIcon(QIcon(":sort-ascending.png"))
        self.sortByDescendingAct.setText("Descending")
        self.sortByDescendingAct.setIcon(QIcon(":sort-descending.png"))

        # иконка и название сортировки по имени, размеру, типу файла
        self.sortByNameAct.setText("Name")
        self.sortByNameAct.setIcon(QIcon(":sort-name.png"))
        self.sortBySizeAct.setText("Size")
        self.sortBySizeAct.setIcon(QIcon(":sort-size.png"))
        self.sortByTypeAct.setText("Type")
        self.sortByTypeAct.setIcon(QIcon(":sort-type.png"))


    def _createActionsConnections(self):
        """Связывание пунктов меню с обработчиками"""

        self.openAct.triggered.connect(self.open)
        self.removeAct.triggered.connect(self.remove)
        self.createFolderAct.triggered.connect(self.createFolder)
        self.createFileAct.triggered.connect(self.createFile)
        self.copyAct.triggered.connect(self.copy)
        self.pasteAct.triggered.connect(self.paste)
        self.renameAct.triggered.connect(self.rename)
        self.refreshAct.triggered.connect(self.sort)
        self.cutAct.triggered.connect(self.cut)
        self.searchAct.triggered.connect(self.search)
        self.prevFolderAct.triggered.connect(self.openPrevFolder)
        self.nextFolderAct.triggered.connect(self.openNextFolder)
        self.sortByNameAct.triggered.connect(self.sort)
        self.sortBySizeAct.triggered.connect(self.sort)
        self.sortByAscendingAct.triggered.connect(self.sort)
        self.sortByDescendingAct.triggered.connect(self.sort)
        self.sortByTypeAct.triggered.connect(self.sort)


    def _disableToolBarMenuActions(self):
        """Отключение пунктов меню (используется при переходе в новую директорию)"""

        self.openAct.setDisabled(True)
        self.removeAct.setDisabled(True)
        self.copyAct.setDisabled(True)
        self.cutAct.setDisabled(True)
        self.renameAct.setDisabled(True)


    def openPrevFolder(self):
        """Открытие предыдущей папки"""

        prevFolder, curFolder = os.path.split(os.getcwd())
        os.chdir(prevFolder)

        # если перешли на каталог выше, то активируем кнопку перехода в следующий каталог
        if self._getMaxPath(os.getcwd(), self.mostDeepFolder) == self.mostDeepFolder:
            self.nextFolderAct.setDisabled(False)

        # если дошли до корневого каталога системы, отключаем кнопку перехода в предыдущий каталог
        up = os.path.abspath(os.path.join(os.getcwd(), "../")) # получение каталога выше
        if os.getcwd() == up:
            self.prevFolderAct.setDisabled(True)

        # обновление представления
        self.view.display()

        # отключение пунктов меню, которые нельзя использовать, пока пользователь не выберет файл/папку
        self._disableToolBarMenuActions()


    def openNextFolder(self):
        """Открытие следующей папки"""

        # список [путь до самой глубокой просмотренной папки]
        normMostDeepPath = os.path.normpath(self.mostDeepFolder).split(os.sep)

        normCurPath = os.path.normpath(os.getcwd()).split(os.sep) # список [путь до текущего файла]
        normCurPath = [part for part in normCurPath if part] # для крайнего случая ['C:', ''] (очистка пустых значений)

        nextFolder = normMostDeepPath[:len(normCurPath)+1] # путь до следующей папки
        os.chdir(f"{os.sep}".join(nextFolder)) # переходим в новую директорию
        self.view.display() # обновление списка файлов

        # если перешли на каталог ниже, то активируем кнопку перехода на предыдущий каталог
        self.prevFolderAct.setDisabled(False)

        # если перешли на самый нижний каталог, то деактивируем кнопку перехода в следующий каталог
        if os.getcwd() == self.mostDeepFolder:
            self.nextFolderAct.setDisabled(True)

        # отключение пунктов меню, которые нельзя использовать, пока пользователь не выберет файл/папку
        self._disableToolBarMenuActions()


    def _getMaxPath(self, path1, path2):
        """Возвращает максимально вложенный путь между path1 и path2"""
        return [path2, path1][len(path1.split(os.sep)) > len(path2.split(os.sep))]


    def sort(self):
        """Сортировка файлов/папок проводника"""

        def get_size(start_path=os.getcwd()):
            """Получение размера папки в байтах"""
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    # skip if it is symbolic link
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)

            return total_size

        sender = self.sender()

        key = self.sortByTypeFormatGroup.checkedAction()
        keyF = None

        reverse = False if self.sortByTypeAscDesGroup.checkedAction() is self.sortByAscendingAct else True

        if key is self.sortByNameAct:
            keyF = lambda f: f
        elif key is self.sortBySizeAct:
            keyF = lambda f: os.path.getsize(f) if os.path.isfile(f) else get_size(f)
        elif key is self.sortByTypeAct:
            keyF = lambda f: os.path.splitext(f)[1]

        sortion = {"key": keyF, "reverse": reverse}
        self.view.display(sortion=sortion)

    def open(self):
        """Открытие выбранного файла/папки"""

        item = self.view.selectedItems()
        text = item[0].text() # имя выбранной папки / выбранного файла

        if os.path.isfile(text):
            # запуск файла
            os.startfile(text)
        else:
            # открытие файла
            folder = os.path.join(os.getcwd(), text)
            os.chdir(folder)

            # проверка какой путь глубже: бывший или текущий
            if self.mostDeepFolder.startswith(os.getcwd()) and self.mostDeepFolder != os.getcwd():
                # бывший
                self.mostDeepFolder = self._getMaxPath(self.mostDeepFolder, os.getcwd())
            else:
                # текущий
                self.mostDeepFolder = os.getcwd()
                # отключение переключателя перехода в следующую папку, т.к текущая наиболее грубокая
                self.nextFolderAct.setDisabled(True)
                # включение переключателя перехода в предыдущую папку, т.к был переход в более глубокую
                self.prevFolderAct.setEnabled(True)

            # обновление представления
            self.view.display()

            # отключение пунктов меню, которые нельзя использовать, пока пользователь не выберет файл/папку
            self._disableToolBarMenuActions()


    def remove(self):
        """
        Удаление выбранного файла или выбранной папки.
        В случае с папками, вложенные файлы и папки тоже будут удалены.
        """

        def createDeletePopup():
            """Диалоговое окно с подтверждением удалить файл"""

            name = 'folder' if os.path.isdir(text) else 'file'
            title = f"Delete {name}"
            message = f'Are you sure you want to delete {name} "{text}"?'
            btns = QMessageBox.Ok | QMessageBox.Cancel

            return QMessageBox.question(self, title, message, btns)

        item = self.view.selectedItems()[:1]
        if not item:
            return

        text = item[0].text()

        # диалог с пользователем, удалять ли файл
        sure = createDeletePopup() == QMessageBox.Ok
        if not sure: return

        if os.path.isfile(text): # удаление файла
            os.remove(os.path.join(os.getcwd(), text))
        else: # рекурсивное удаление папки
            shutil.rmtree(text)

        # обновление представления
        self.view.display()


    def createFolder(self):
        """Создание директории"""

        folder, ok = QInputDialog.getText(self, "Create folder", "Enter folder name:")
        if ok and folder:
            if os.path.exists(folder):
                # если папка уже существует, предупреждаем пользователя и ничего не делаем
                what = "Folder" if os.path.isdir(folder) else "File" # уже существует папка или файл?
                QMessageBox.warning(self,
                                    "Warning",
                                    f'{what} with the same name"{folder} is already exists',
                                    QMessageBox.Ok)
                return
            else:
                # если папка не существует, создаем папку
                os.mkdir(folder)

                # обновление представления
                self.view.display()

        elif not folder and ok:
            # если пользователь ничего не ввёл, выдаем ошибку
            QMessageBox.critical(self,
                                 "Error",
                                 f"Folder with the empty name can't be created",
                                 QMessageBox.Ok
            )


    def createFile(self):
        """Создание файла"""

        filename, ok = QInputDialog.getText(self, "Create file", "Enter file name:")
        if ok and filename:
            # проверка есть ли файлы с таким же именем
            if os.path.exists(filename):
                # если файл существует, предупреждаем пользователя и ничего не делаем
                what = "Folder" if os.path.isdir(filename) else "File" # уже существует папка или файл?
                QMessageBox.warning(self,
                                    "Warning",
                                    f'{what} with the same name "{filename}" is already exists',
                                    QMessageBox.Ok)
                return

            # создание нового файла
            f = open(filename, "x")
            f.close()

            # обновление списка файлов
            self.view.display()

        elif not filename and ok:
            # если пользователь не ввел название файла и нажал ок, выдаем ошибку
            QMessageBox.critical(self,
                                 "Error",
                                 f"File with the empty name can't be created",
                                 QMessageBox.Ok
            )


    def search(self):
        """Поиск файла"""

        name, ok = QInputDialog.getText(self, "Search", "Find:")
        if ok and name:

            # файлы и папки, которые начинаются на то, что ввел пользователь
            matched = [f for f in os.listdir() if f.startswith(name)]

            if not matched:
                # если нет подходящих папок, оповещаем пользователя
                QMessageBox.information(self,
                                        "Information",
                                        f'Not found files/folders which starts with "{name}"',
                                        QMessageBox.Ok)
            else:
                # если есть подходящие файлы и папки, выводим их
                if not matched:
                    return
                else:
                    # скрываем старые папки и файлы и отображаем подходящие (искомые) пользователем
                    self.view.clear()

                for file in matched:
                    filename, extension = os.path.splitext(file)
                    item = QListWidgetItem()
                    item.setText(file)
                    if not extension:
                        if os.path.isdir(file):
                            item.setIcon(QIcon(":folder.png"))
                    else:
                        icon = extension[1:]  # убираем точку из расширения
                        item.setIcon(QIcon(f":{icon}.svg"))
                    self.view.addItem(item)


    def copy(self):
        """Сохранение пути до файла копирования в буфер обмена"""

        item = self.view.selectedItems()[:1]
        if not item:
            # не выбран файл/папка для копирования
            return

        text = item[0].text()
        self.copyBuffer = os.path.join(os.getcwd(), text)

        # активация кнопки вставить
        self._activatePasteAction()


    def _activatePasteAction(self):
        """Активация кнопки вставить"""

        self.pasteAct.setEnabled(True) # в тул-баре


    def paste(self):
        """Вставка скопированного или вырезанного файла"""

        # отсутствуют файлы для вставки
        if not self.copyBuffer and not self.cutBuffer:
            return

        # перемещение файла/папки(рекурсивно)
        if self.cutBuffer:
            path, file = os.path.split(self.cutBuffer)

            if path == os.getcwd():
                # перемещение в ту же папку не требуется
                return

            # перемещение файла (вырезка, вставка)
            os.rename(src=self.cutBuffer, dst=os.path.join(os.getcwd(), file))

            # очистка буфера
            self.cutBuffer = None


        if self.copyBuffer:
            copySign = " - copy"

            path, file = os.path.split(self.copyBuffer)

            name, extension = os.path.splitext(file)


            if os.path.isdir(file):
                folders = [f for f in os.listdir() if os.path.isdir(f)]
                # есть ли у папки копии
                hasCopies = any(f == name + copySign + "1" for f in folders)
                if not hasCopies: # у папки еще нет копий
                    copyMarkedFolder = name + copySign + "1"
                    shutil.copytree(src=self.copyBuffer, dst=os.path.join(path, copyMarkedFolder))
                else: # у папки есть копии
                    def getNextCopyFolderNum():
                        copyNum = 1
                        for f in folders:
                            if f.startswith(name  + copySign):
                                num = int(f.split(copySign)[-1])
                                copyNum = num if num > copyNum else copyNum
                        return copyNum+1
                    copyMarkedFolder = name + copySign + str(getNextCopyFolderNum())
                    shutil.copytree(src=self.copyBuffer, dst=os.path.join(path, copyMarkedFolder))


            else:
                files = [f for f in os.listdir() if not os.path.isdir(f)]
                # проверяем есть ли у файла копии
                hasCopies = False
                for f in files:
                    fname, fextension = os.path.splitext(f)
                    if fname == name + copySign + "1":
                        hasCopies = True
                        break
                # копирование файла
                if not hasCopies: # у файла еще нет копий с постфиксом "<<copySign>>1"
                    copyMarkedFile = name + copySign + "1" + extension
                    shutil.copyfile(src=self.copyBuffer, dst=os.path.join(path, copyMarkedFile))
                else: # у файла ЕСТЬ копии с постфиксом "<<copySign>>1"
                    def getNextCopyNum():
                        # поиск последнего номера копии
                        copyNum = 1
                        for f in files:
                            fname, fext = os.path.splitext(f)
                            if fname.startswith(name + copySign):
                                num = int(fname.split(copySign)[-1])
                                copyNum = num if num > copyNum else copyNum
                        return copyNum+1 # номер след. копии

                    copyMarkedFile = name + copySign + str(getNextCopyNum()) + extension
                    shutil.copyfile(src=self.copyBuffer, dst=os.path.join(path, copyMarkedFile))



        # была произведена вставка/копирование файла
        self.view.display()
        self.pasteAct.setDisabled(True)


    def rename(self):
        """Переименование файла/папки"""

        item = self.view.selectedItems()[:1]
        if not item:
            return

        text = item[0].text() # название файла для переименования

        name = "folder" if os.path.isdir(text) else "file" # переименовываем файл или папку?

        # спрашиваем у пользователя, на что переименовать
        newName, ok = QInputDialog.getText(self, f"Rename {name}", f"Enter new {name} name:")
        if ok and text != newName and newName: # если имя не такое же и вообще есть имя
            # переименование папки
            os.rename(src=text, dst=newName)

            # обновление списка файлов
            self.view.display()


    def cut(self):
        """Сохранение файла в буфер обмена"""

        item = self.view.selectedItems()[:1]
        if not item:
            return

        text = item[0].text() # имя файла
        self.cutBuffer = os.path.join(os.getcwd(), text)

        # активация кнопки вставить
        self._activatePasteAction()

    def eventFilter(self, source, event):
        """Создание контекстного меню при нажатии на область просмотра проводника"""

        if event.type() == QEvent.ContextMenu and source is self:
            pos = event.globalPos() # позиция клика
            item = self.view.itemAt(QWidget.mapFromGlobal(self.view, pos)) # файл/папка, где произошел клик
            if not item:
                self._execFreeSpaceContextMenu(globalPos=event.globalPos()) # контекстное меню на пустом месте
            else:
                self._execContextMenu(globalPos=event.globalPos()) # контекстное меню на выбранном файле или папке
            return True
        return super().eventFilter(source, event) # проброс обработки событий выше


    def _execContextMenu(self, globalPos):
        """Создание контекстного меню на выбранном файле или выбранной папке"""

        self._createContextMenu().exec_(globalPos)


    def _customizeContextActions(self):
        """Настройка внешнего вида пунктов меню"""
        
        self.openContextAct.setIcon(QIcon(":open.png"))
        self.openContextAct.setText("Open")

        self.searchContextAct.setIcon(QIcon(":search.png"))
        self.searchContextAct.setText("Search")

        self.createFileContextAct.setIcon(QIcon(":new-file.png"))
        self.createFileContextAct.setText("Create file")

        self.createFolderContextAct.setIcon(QIcon(":new-folder.png"))
        self.createFolderContextAct.setText("Create folder")

        self.removeContextAct.setIcon(QIcon(":remove.png"))
        self.removeContextAct.setText("Delete")

        self.copyContextAct.setIcon(QIcon(":copy.png"))
        self.copyContextAct.setText("Copy")

        self.renameContextAct.setIcon(QIcon(":rename.png"))
        self.renameContextAct.setText("Rename")

        self.refreshContextAct.setIcon(QIcon(":refresh.png"))
        self.refreshContextAct.setText("Refresh")

        self.pasteContextAct.setIcon(QIcon(":paste.png"))
        self.pasteContextAct.setText("Paste")
        self.pasteContextAct.setEnabled(self.pasteAct.isEnabled()) # отключаем пункт, пока пользователь не захочет скопировать/вставить

        self.cutContextAct.setIcon(QIcon(":cut.png"))
        self.cutContextAct.setText("Cut")


    def _createContextActions(self):
        """Создание пунктов контекстного меню на выбранной папке или файле"""

        self.createFileContextAct = QAction(self)
        self.createFolderContextAct = QAction(self)
        self.removeContextAct = QAction(self)
        self.copyContextAct = QAction(self)
        self.openContextAct = QAction(self)
        self.pasteContextAct = QAction(self)
        self.renameContextAct = QAction(self)
        self.refreshContextAct = QAction(self)
        self.cutContextAct = QAction(self)
        self.searchContextAct = QAction(self)

        # настройка внешнего вида пунктов меню
        self._customizeContextActions()

        # соединение пунктов меню с обработчиками
        self._createContextActionsConnections()


    def _createContextActionsConnections(self):
        """Обработчики пунктов контекстного меню на выбранной папке или выбранном файле"""

        self.createFileContextAct.triggered.connect(self.createFile)
        self.createFolderContextAct.triggered.connect(self.createFolder)
        self.removeContextAct.triggered.connect(self.remove)
        self.copyContextAct.triggered.connect(self.copy)
        self.openContextAct.triggered.connect(self.open)
        self.pasteContextAct.triggered.connect(self.paste)
        self.renameContextAct.triggered.connect(self.rename)
        self.refreshContextAct.triggered.connect(self.sort)
        self.cutContextAct.triggered.connect(self.cut)
        self.searchContextAct.triggered.connect(self.search)


    def _execFreeSpaceContextMenu(self, globalPos):
        """Создание контекстного меню при клике пустое место в проводнике"""

        # создание пунктов
        self._createContextActions()

        # добавление пунктов в меню
        self.contextMenu = QMenu(self)
        self.contextMenu.addAction(self.createFileContextAct)
        self.contextMenu.addAction(self.createFolderContextAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.pasteContextAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.searchContextAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.refreshContextAct)

        self.contextMenu.exec_(globalPos)


    def _createContextMenu(self):
        """Создание контекстного меню на выбранной папке или выбранном файле"""

        # создание пунктов меню
        self._createContextActions()

        # добавление пунктов в меню
        self.contextMenu = QMenu(self)
        self.contextMenu.addAction(self.openContextAct)
        self.contextMenu.addAction(self.renameContextAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.createFileContextAct)
        self.contextMenu.addAction(self.createFolderContextAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.removeContextAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.copyContextAct)
        self.contextMenu.addAction(self.cutContextAct)
        self.contextMenu.addAction(self.pasteContextAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.searchContextAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.refreshContextAct)

        return self.contextMenu
