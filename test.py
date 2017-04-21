#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
from PyQt5.QtWidgets import QApplication
from MagicViewer import ImageViewer


app = QApplication(sys.argv)
viewer = ImageViewer()
viewer.open("C:\\Users\\youth_lee\Desktop\\newimage.png")
sys.exit(app.exec_())
