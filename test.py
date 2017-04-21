#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-04-20 18:20:29
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$


import sys
from PyQt5.QtWidgets import QApplication
from MagicViewer import ImageViewer


app = QApplication(sys.argv)
viewer = ImageViewer()
viewer.open("C:\\Users\\李杨\Desktop\\新建脑图.png")
sys.exit(app.exec_())
