from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
        QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy, QLineEdit, QComboBox, QPushButton,
                             QHBoxLayout, QVBoxLayout, QWidget)
import PIL
from PIL import Image
import numpy
from dxfwrite import DXFEngine as dxf

class ImgProcessMainWindow(QMainWindow):
    def __init__(self):
        super(ImgProcessMainWindow, self).__init__()

        self.imgNameLbl = QLabel("Название файла")

        self.diaScrewLbl = QLabel("Диаметр шляпки")
        self.diaScrewTxt = QLineEdit("8.7")
        self.diaScrewMmLbl = QLabel("мм")

        self.picSizeLbl = QLabel("Размеры картины")
        self.picWidthTxt = QLineEdit("850")
        self.picWidthMmTxt = QLabel("мм")
        self.picHeightTxt = QLineEdit("850")
        self.picHeightMmTxt = QLabel("мм")

        self.interpolationLbl = QLabel("Вид интерполяции")
        self.interpolationCBox = QComboBox()
        self.interpolationCBox.addItems(["BILINEAR", "NEAREST", "BICUBIC",  "LANCZOS"])

        self.thresholdLbl = QLabel("Порог заполнениял")
        self.thresholdCBox = QComboBox()
        self.thresholdCBox.addItems(["95 %", "50 %", "55 %", "60 %", "65 %", "70 %", "75 %", "80 %", "90 %", "0 %"])

        self.startBtn = QPushButton("Старт")
        self.startBtn.clicked.connect(self.start_clicked)

        self.diamLayout = QHBoxLayout()
        self.diamLayout.addWidget(self.diaScrewLbl)
        self.diamLayout.addWidget(self.diaScrewTxt)
        self.diamLayout.addWidget(self.diaScrewMmLbl)

        self.sizeLayout = QHBoxLayout()
        self.sizeLayout.addWidget(self.picSizeLbl)
        self.sizeLayout.addWidget(self.picWidthTxt)
        self.sizeLayout.addWidget(self.picWidthMmTxt)
        self.sizeLayout.addWidget(self.picHeightTxt)
        self.sizeLayout.addWidget(self.picHeightMmTxt)

        self.interpolationLayout = QHBoxLayout()
        self.interpolationLayout.addWidget(self.interpolationLbl)
        self.interpolationLayout.addWidget(self.interpolationCBox)

        self.thresholdLayout = QHBoxLayout()
        self.thresholdLayout.addWidget(self.thresholdLbl)
        self.thresholdLayout.addWidget(self.thresholdCBox)

        self.btnLayout = QHBoxLayout()
        self.btnLayout.addWidget(self.startBtn)

        self.settingsLayout = QVBoxLayout()
        self.settingsLayout.addWidget(self.imgNameLbl)
        self.settingsLayout.addLayout(self.diamLayout)
        self.settingsLayout.addLayout(self.sizeLayout)
        self.settingsLayout.addLayout(self.interpolationLayout)
        self.settingsLayout.addLayout(self.thresholdLayout)
        self.settingsLayout.addLayout(self.btnLayout)

        self.centralWidget = QWidget(self)
        self.centralWidget.setLayout(self.settingsLayout)
        self.setCentralWidget(self.centralWidget)

        self.create_actions()
        self.create_menus()

        self.setWindowTitle("Шахматная структура изображений")
        #self.resize(500, 400)

        self.inputImage = None

    def create_actions(self):
        self.openAct = QAction("Открыть...", self, triggered=self.open_file)

    def create_menus(self):
        self.fileMenu = QMenu("Файл", self)
        self.fileMenu.addAction(self.openAct)

        self.menuBar().addMenu(self.fileMenu)

    def open_file(self):
        print("Open file")
        fileName, _ = QFileDialog.getOpenFileName(self, "Открыть файл",
                                                  QDir.currentPath())
        print(fileName)
        if fileName:
            self.inputImage = None
            self.inputImage = Image.open(fileName).convert('L')
            if not self.inputImage:
                QMessageBox.information(self, "Ошибка",
                                        "Невозможно загрузить файл: %s" % fileName)
                return

            self.imgNameLbl.setText("Файл: %s, размер: %d x %d px" % (fileName.split("/")[-1],
                                                                      self.inputImage.size[0],
                                                                      self.inputImage.size[1]))
            self.fileName = fileName.split("/")[-1].split(".")[0]

    def start_clicked(self):
        print("start clicked")

        dxfFileName = self.fileName

        try:
            screwDia = float(self.diaScrewTxt.text())
        except:
            QMessageBox.information(self, "Ошибка",
                                    "Неправильный ввод диаметра шляпки")
            return

        try:
            width = float(self.picWidthTxt.text())
            height = float(self.picHeightTxt.text())
        except:
            QMessageBox.information(self, "Ошибка",
                                    "Неправильный ввод размеров картины")
            return

        resampleType = self.interpolationCBox.currentText()

        dxfFileName += " "
        dxfFileName += resampleType

        if resampleType == "BILINEAR":
            resampleType = PIL.Image.BILINEAR
        elif resampleType == "NEAREST":
            resampleType = PIL.Image.NEAREST
        elif resampleType == "BICUBIC":
            resampleType = PIL.Image.BICUBIC
        elif resampleType == "LANCZOS":
            resampleType = PIL.Image.LANCZOS

        thresholdScrew = self.thresholdCBox.currentText()

        dxfFileName += " "
        dxfFileName += thresholdScrew
        dxfFileName += ".dxf"

        thresholdScrew = int(thresholdScrew.split(" ")[0]) / 100

        process_chess_sampling(self.inputImage, screwDia, 2.0, width, height,
                               resampleType, thresholdScrew, dxfFileName)


def process_chess_sampling(img, screwDia, holeDia, width, height, resampleType, thresholdScrew, fileName):
    w = int(round(width / screwDia, 0))
    h = int(round(height / screwDia, 0))
    w = w * 20
    h = h * 20
    BWthreshold = 200

    tempImg = img.resize((w, h), resampleType)
    (w, h) = tempImg.size

    greyscaleMap = list(tempImg.getdata())
    greyscaleMap = numpy.array(greyscaleMap)
    greyscaleMap = greyscaleMap.reshape((h, w))

    img1 = Image.fromarray(numpy.uint8(greyscaleMap), 'L')
    img1.show()

    tempArray = []

    for i in range(h):
        for j in range(w):
            if greyscaleMap[i][j] < BWthreshold:
                greyscaleMap[i][j] = 0
            else:
                greyscaleMap[i][j] = 255

    print("greyscale updated")

    for row in range(0, len(greyscaleMap), 10):
        arr = []
        for col in range(int((row / 10) % 2) * 18, len(greyscaleMap[row]), 36):
            meanImg = 0
            countPoints = 0
            if row == 0:
                if col == 0:
                    for i in range(10):
                        for j in range(10):
                            try:
                                meanImg += greyscaleMap[row+i][col+j]
                                countPoints += 1
                            except:
                                print("r=0, c=0  index [%d][%d] unsolved" % (i, j))
                else:
                    for i in range(10):
                        for j in range(-9, 10, 1):
                            try:
                                meanImg += greyscaleMap[row+i][col+j]
                                countPoints += 1
                            except:
                                print("r=0, c!=0 index [%d][%d] unsolved" % (i, j))
            elif col == 0:
                if row != 0:
                    for i in range(-9, 10, 1):
                        for j in range(10):
                            try:
                                meanImg += greyscaleMap[row+i][col+j]
                                countPoints += 1
                            except:
                                print("r!=0, c=0 index [%d][%d] unsolved" % (i, j))

            elif row == (len(greyscaleMap) - 1):
                if col == (len(greyscaleMap[row]) - 1):
                    for i in range(-9, 1, 1):
                        for j in range(-9, 1, 1):
                            try:
                                meanImg += greyscaleMap[row+i][col+j]
                                countPoints += 1
                            except:
                                print("r=w, c=h index [%d][%d] unsolved" % (i, j))
                else:
                    for i in range(-9, 1, 1):
                        for j in range(-9, 10, 1):
                            try:
                                meanImg += greyscaleMap[row+i][col+j]
                                countPoints += 1
                            except:
                                print("r=w, c!=h index [%d][%d] unsolved" % (i, j))

            elif col == (len(greyscaleMap[row]) - 1):
                if row != (len(greyscaleMap) - 1):
                    for i in range(-9, 1, 1):
                        for j in range(-9, 10, 1):
                            try:
                                meanImg += greyscaleMap[row+i][col+j]
                                countPoints += 1
                            except:
                                print("r!=w, c=h index [%d][%d] unsolved" % (i, j))
            else:
                for i in range(-9, 10, 1):
                    for j in range(-9, 10, 1):
                        try:
                            meanImg += greyscaleMap[row + i][col + j]
                            countPoints += 1
                        except:
                            print("index [%d][%d] unsolved" % (i, j))

            meanImg /= countPoints

            if meanImg / 255 > thresholdScrew:
                arr.append(1)
            else:
                arr.append(0)
        tempArray.append(arr)

    for l in tempArray:
        print(l)


    drawing = dxf.drawing(fileName)

    for row in range(len(tempArray)):
        if row % 2 == 0:
            for col in range(len(tempArray[row])):
                if tempArray[row][col] == 0:
                    drawing.add(dxf.circle(holeDia / 2, (screwDia / 2 * 3.6 * col,
                                                        (-screwDia / 2) * row))
                                )
        else:
            for col in range(len(tempArray[row])):
                if tempArray[row][col] == 0:
                    drawing.add(dxf.circle(holeDia / 2, (screwDia / 2 * 3.6 * col + 1.8 * screwDia / 2,
                                                        (-screwDia / 2) * row))
                                )

    drawing.save()
    print("done")





if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    imgProcessWindow = ImgProcessMainWindow()
    imgProcessWindow.show()
    sys.exit(app.exec_())
