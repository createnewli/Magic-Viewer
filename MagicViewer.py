#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
图片浏览器
'''
__version__ = 0.3
import os
import sys
import os.path
from functools import partial
from PyQt5.QtGui import QPixmap, QTransform, QIcon, QFont
from PyQt5.QtWidgets import (QFileDialog, QMainWindow, QApplication, QGraphicsScene,
                             QGraphicsView, QMenu, QMessageBox, QPushButton)
from PyQt5.QtCore import QDir, QFileInfo, Qt


class ImageViewer(QMainWindow):

    def __init__(self):
        super().__init__()

        self.formats = ('.png', '.jpg', '.jpeg', '.gif', '.bmp',
                        '.pbm', '.pgm', '.ppm', '.xbm', '.xpm')
        self.rotval = 0     # 旋转方向
        self.rotvals = (0, -90, -180, -270)
        self.file_path = QDir.currentPath()     # 获取当前文件路径

        self.resize(1000, 800)
        self.setWindowTitle("Magic Viewer")

        self.btn = QPushButton("打开图片", self)
        self.btn.resize(200, 80)
        self.btn.move((self.width() - self.btn.width()) / 2, (self.height() - self.btn.height()) / 2)
        self.btn.setFont(QFont("", 20, QFont.Bold))
        self.btn.clicked.connect(self.btnClicked)

        self.show()

    def btnClicked(self):

        self.open()

    def open(self, file=None):
        if file is None:
            self.chooseFile()
        else:
            self.key = file.replace("\\", "/")

        # 获取图像列表
        if self.key:
            self.btn.setEnabled(False)      # 选择了文件按钮消失
            self.imgfiles = []  # 如果选择了文件则则重新获取图像列表
            self.file_path = os.path.dirname(self.key)      # 获取文件路径
            try:
                for file in os.listdir(self.file_path):
                    if os.path.splitext(file)[1].lower() in self.formats:
                        self.imgfiles.append(self.file_path + "/" + file)
                self.count = len(self.imgfiles)     # 图像列表总数量
                self.index = self.imgfiles.index(self.key)  # 当前图像在图像列表中位置
            except FileNotFoundError:
                print("文件目录不存在！")

        self.showImage()

    def chooseFile(self):
        # 选择图片文件
        self.key, _ = QFileDialog.getOpenFileName(self,
                                                  "选择文件", self.file_path,
                                                  "图片文件 (*.bmp *.jpg *.jpeg *.png *.gif)")

    def showImage(self):

        if self.key:
            self.img = QPixmap(self.key)
            if self.img.isNull():
                QMessageBox.information(
                    self, "Magic Viewer", "不能打开文件：%s！" % self.key)
                return

            self.scene = QGraphicsScene()
            self.view = QGraphicsView(self.scene)
            self.view.setDragMode(QGraphicsView.ScrollHandDrag)
            # self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            # self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

            self.scene.clear()
            self.view.resetTransform()
            self.scene.addPixmap(self.img)

            self.zoom = 1   # 缩放系数
            self.rotate = 0  # 旋转系数

            # 如果图片尺寸＞窗口尺寸，计算缩放系数进行缩放
            if self.img.width() > self.width() or self.img.height() > self.height():
                self.zoom = min(self.width() / self.img.width(),
                                self.height() / self.img.height()) * 0.995

            width = self.img.width()
            height = self.img.height()

            # self.scene.setSceneRect(0, 0, width - 2, height - 2)
            self.view.resize(width, height)
            self.setCentralWidget(self.view)
            self.updateView()
            self.show()

    # 获取文件大小
    def fileSize(self, file):
        size = QFileInfo(file).size()

        if size < 1024:
            return str(size), "B"
        elif 1024 <= size < 1024 * 1024:
            return str(round(size / 1024, 2)), "KB"
        else:
            return str(round(size / 1024 / 1024, 2)), "MB"

    # 全屏
    def toggleFullscreen(self):

        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_F11:
            self.toggleFullscreen()
        elif event.key() == Qt.Key_Up or event.key() == Qt.Key_W:
            self.zoomIn()
        elif event.key() == Qt.Key_Down or event.key() == Qt.Key_S:
            self.zoomOut()
        elif event.key() == Qt.Key_1:
            self.zoomReset()
        elif event.key() == Qt.Key_E:
            self.rotateImg(-1)
        elif event.key() == Qt.Key_R:
            self.rotateImg(1)
        elif event.key() == Qt.Key_F:
            self.fitView()
        elif event.key() == Qt.Key_Right or event.key() == Qt.Key_Space:
            self.dirBrowse(1)
        elif event.key() == Qt.Key_Left or event.key() == Qt.Key_B:
            self.dirBrowse(-1)
        elif event.key() == Qt.Key_Q or event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_O:
            self.btnClicked()

    def mouseDoubleClickEvent(self, event):

        self.toggleFullscreen()

    def zoomIn(self):

        self.zoom *= 1.05
        self.updateView()

    def zoomOut(self):

        self.zoom /= 1.05
        self.updateView()

    def zoomReset(self):

        self.zoom = 1
        self.updateView()

    def rotateImg(self, clock):

        self.rotval += clock
        if self.rotval == 4:
            self.rotval = 0
        elif self.rotval < 0:
            self.rotval = 3
        self.rotate = self.rotvals[self.rotval]
        self.updateView()

    def fitView(self):

        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        if self.rotate == 0:
            self.zoom = self.view.transform().m11()
        elif self.rotate == -90:
            self.zoom = (self.view.transform().m12()) * -1
        elif self.rotate == -180:
            self.zoom = (self.view.transform().m11()) * -1
        else:
            self.zoom = self.view.transform().m12()

    def updateView(self):

        self.view.setTransform(QTransform().scale(
            self.zoom, self.zoom).rotate(self.rotate))
        # 更新标题信息
        self.title = os.path.basename(self.key)
        size = self.fileSize(self.key)
        self.setWindowTitle("%s(%sx%s,%s %s) - Magic Viewer - 第%s/%s张 %.2f%%" % (
            self.title, self.img.width(), self.img.height(), size[0], size[1],
            self.index + 1, self.count, self.zoom * 100))

    def dirBrowse(self, direc):

        if self.count > 1:
            self.index += direc
            # 最后一张后跳到第一张，第一张前跳到最后一张
            if self.index > self.count - 1:
                self.index = 0
            elif self.index < 0:
                self.index = self.count - 1

            self.key = self.imgfiles[self.index]

            self.showImage()

    def wheelEvent(self, event):
        # 鼠标滚动
        moose = event.angleDelta().y() / 120
        if moose > 0:
            self.zoomIn()
        elif moose < 0:
            self.zoomOut()

    def contextMenuEvent(self, event):
        # 邮件菜单
        menu = QMenu()
        menu.addAction(QIcon('image\\zoom_in.png'),
                       '放大          Scorll Up, W', self.zoomIn)
        menu.addAction(QIcon('image\\zoom_out.png'),
                       '缩小          Scroll Down, S', self.zoomOut)
        menu.addAction(QIcon('image\\full.png'),
                       '全屏          F11', self.toggleFullscreen)
        menu.addAction(QIcon('image\\rotate_right.png'),
                       '右转90°     R', partial(self.rotateImg, 1))
        menu.addAction(QIcon('image\\rotate_left.png'),
                       '左转90°     E', partial(self.rotateImg, -1))
        menu.addAction(QIcon('image\\next.png'),
                       '下一张       Right, SPACE', partial(self.dirBrowse, 1))
        menu.addAction(QIcon('image\\previous.png'),
                       '上一张       Left, B', partial(self.dirBrowse, -1))
        menu.addAction('适合屏幕    F', self.fitView)
        menu.addAction('实际尺寸    1', self.zoomReset)
        menu.addSeparator()
        menu.addAction('打开          O', self.open)
        menu.addAction('退出          Q, ESC', self.close)
        menu.addSeparator()
        menu.addAction('关于Magic Viewer', self.about)

        menu.exec_(event.globalPos())

    def about(self):
        QMessageBox.about(self, "关于Magic Viewer",
                          "<b>Magic Viewer</b>是一个基于PyQt5的开源图片浏览器。"
                          "Aurth : Youth Lee\n"
                          "Version : Ver 0.3\n"
                          "URL : https://github.com/createnewli/Magic-Viewer#magic-viewer")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    viewer = ImageViewer()
    sys.exit(app.exec_())
