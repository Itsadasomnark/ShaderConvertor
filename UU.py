from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import sys,os

path = os.path.realpath(__file__)
file_name = str(path).split('\\')[-1:]
path_module = str(path).split('\\%s'%flie_name[0])[0]
if not path_module in sys.path:
	sys.path.append(path_module)
import Convertor as con
reload(con)

conv = con.ShaderConvert()

print conv.get_obj()