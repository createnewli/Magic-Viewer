#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
图片浏览器
'''

import os
import sys
import os.path
from functools import partial
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QTransform, QIcon
from PyQt5.QtWidgets import (QFileDialog, QMainWindow, QApplication, QGraphicsScene,
                             QGraphicsView, QMenu, QMessageBox)
from PyQt5.QtCore import QDir, QFileInfo


class ImageView(QGraphicsView):

    def wheelEvent(self, event):

        moose = event.angleDelta().y() / 120
        if moose > 0:
            viewer.zoomIn()
        elif moose < 0:
            viewer.zoomOut()

    def contextMenuEvent(self, event):

        menu = QMenu()
        menu.addAction(QIcon('image\\zoom_in.png'),
                       '放大          Up, W', viewer.zoomIn)
        menu.addAction(QIcon('image\\zoom_out.png'),
                       '缩小          Down, S', viewer.zoomOut)
        menu.addAction(QIcon('image\\full.png'),
                       '全屏          F11', viewer.toggleFullscreen)
        menu.addAction(QIcon('image\\rotate_right.png'),
                       '右转90°     R', partial(viewer.rotateImg, 1))
        menu.addAction(QIcon('image\\rotate_left.png'),
                       '左转90°     E', partial(viewer.rotateImg, -1))
        menu.addAction(QIcon('image\\next.png'),
                       '下一张       Right, SPACE', partial(viewer.dirBrowse, 1))
        menu.addAction(QIcon('image\\previous.png'),
                       '上一张       LEFT, BACKSPACE', partial(viewer.dirBrowse, -1))
        menu.addAction('适合屏幕    F', viewer.fitView)
        menu.addAction('实际尺寸    1', viewer.zoomReset)
        # menu.addAction('About ImageViewer', viewer.about)
        menu.addAction('打开          O', viewer.open)
        menu.addAction('退出          Q, ESC', viewer.close)

        menu.exec_(event.globalPos())


class ImageViewer(QMainWindow):

    def __init__(self):
        super().__init__()

        self.formats = ('.png', '.jpg', '.jpeg', '.gif', '.bmp',
                        '.pbm', '.pgm', '.ppm', '.xbm', '.xpm')
        self.rotval = 0     # 旋转方向
        self.rotvals = (0, -90, -180, -270)
        self.file_path = QDir.currentPath()     # 获取当前文件路径
        self.key = ""

        self.scene = QGraphicsScene()
        self.img = QPixmap(self.key)
        self.scene.addPixmap(self.img)
        self.view = ImageView(self.scene, self)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        # self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.resize(1000, 800)
        self.setCentralWidget(self.view)

        self.open()

    def open(self):
        self.chooseFile()
        self.showImage()

    def chooseFile(self):
        # 选择图片文件

        self.key, _ = QFileDialog.getOpenFileName(self,
                                                  "选择文件", self.file_path,
                                                  "图片文件 (*.bmp *.jpg *.jpeg *.png *.gif)")
        if self.key:
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

    def showImage(self):

        if self.key:
            self.img = QPixmap(self.key)
            if self.img.isNull():
                QMessageBox.information(
                    self, "Magic Viewer", "不能打开文件：%s！" % self.key)
                return

            self.scene.clear()
            self.view.resetTransform()
            self.scene.addPixmap(self.img)

            self.zoom = 1
            self.rotate = 0
            # self.resize(self.img.size())
            self.scene.setSceneRect(0, 0, self.img.width() + 2, self.img.height() + 2)
            self.view.resize(self.img.width() + 2, self.img.height() + 2)
            self.setCentralWidget(self.view)
            self.show()

            self.title = os.path.basename(self.key)
            self.setWindowTitle(str(self.title) + " - Magic Viewer")

            self.fitView()

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

        if event.key() == QtCore.Qt.Key_F11:
            self.toggleFullscreen()
        elif event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_W:
            self.zoomIn()
        elif event.key() == QtCore.Qt.Key_Down or event.key() == QtCore.Qt.Key_S:
            self.zoomOut()
        elif event.key() == QtCore.Qt.Key_1:
            self.zoomReset()
        elif event.key() == QtCore.Qt.Key_E:
            self.rotateImg(-1)
        elif event.key() == QtCore.Qt.Key_R:
            self.rotateImg(1)
        elif event.key() == QtCore.Qt.Key_F:
            self.fitView()
        elif event.key() == QtCore.Qt.Key_Direction_R or event.key() == QtCore.Qt.Key_Space:
            self.dirBrowse(1)
        elif event.key() == QtCore.Qt.Key_Backspace or event.key() == QtCore.Qt.Key_Left:
            self.dirBrowse(-1)
        elif event.key() == QtCore.Qt.Key_Q or event.key() == QtCore.Qt.Key_Escape:
            self.close()

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

        self.view.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
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


if __name__ == '__main__':

    app = QApplication(sys.argv)
    viewer = ImageViewer()
    sys.exit(app.exec_())
