from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore
from shiboken2 import wrapInstance
import maya.cmds as mc
import Convertor as cov
reload(cov)
import ui 
reload(ui)
import editui
reload(editui)
import filenameui
reload(filenameui)

class MainApp(QtWidgets.QMainWindow):
	"""docstring for MainApp"""
	def __init__(self, parent=None):
		super(MainApp, self).__init__(parent=parent)
		self.ui = ui.Ui_ShaderConvertor()
		self.editor_win = None
		self.ui.setupUi(self)
		self.cov = cov.ShaderConvert()
		self.setup_defaults()
		self.button()
	
	def create_preset(self):
		count = self.ui.Preset_combo.count()
		if self.ui.Preset_combo.currentIndex() == count-1:
			self.editor()

	def editor(self):
		combo = self.ui.Preset_combo.currentText()
		try:
			self.editor_win.close()

		except:
			pass
		self.editor_win = Editor(combo,getMayaWindow())
		self.editor_win.show()

	def setup_defaults(self): 
		self.add_presets()
		self.ui.treeWidget.header().setDefaultSectionSize(250)
		self.add_info()
		self.setWindowTitle('ShaderConvertor')

	def add_presets(self): 
		self.ui.Preset_combo.clear()
		persets = self.cov.get_config_file()
		create = ["--Create Preset--"]
		self.ui.Preset_combo.addItems(persets)
		self.ui.Preset_combo.addItems(create)
	
	def add_info(self):
		self.ui.treeWidget.clear()
		info = self.cov.get_obj_shd()
		shader = []
		self.font = QtGui.QFont()
		self.font.setPointSize(10)
		self.ui.treeWidget.headerItem().setFont(0,self.font)
		self.ui.treeWidget.headerItem().setFont(1,self.font)
		for key in info.keys():
			shader.append(key)
		for i in shader:
			obj = ''
			item = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
			item.setText(0,i)
			item.setFont(0,self.font)
			for j in info[i]:
				obj += '%s,'%j
				item.setText(1,obj[:-1])
				item.setFont(1,self.font)

	def get_data(self):
		file_name = self.ui.Preset_combo.currentText()
		data = self.cov.jsonfile_load(file_name)
		return data

	def button(self):
		self.ui.Convert_Button.clicked.connect(self.convert)
		self.ui.reload_button.clicked.connect(self.add_info)
		self.ui.EditPreset_button.clicked.connect(self.editor)
		self.ui.Preset_combo.activated.connect(self.create_preset)
		self.ui.treeWidget.itemSelectionChanged.connect(self.selectobj)

	def selectobj(self):
		text = self.ui.treeWidget.currentItem().text(1)
		obj = text.split(',')
		mc.select(obj)


	def return_combo(self):
		file_name = self.ui.Preset_combo.currentText()
		return file_name

	def convert(self):
		data = self.get_data()
		shader,sg = self.cov.covert(data)
		self.add_info()
		if self.ui.Delete_checkBox.isChecked():
			self.cov.del_old_shd(shader,sg)


class Editor(QtWidgets.QMainWindow):
	"""docstring for Editor"""
	def __init__(self, current,parent=None):
		super(Editor, self).__init__(parent=parent)
		self.current = current
		self.cov_info = []
		self.cov_info_2 = []
		self.info_1_item = []
		self.info_2_item = []
		self.font = QtGui.QFont()
		self.eui = editui.Ui_Editor()
		self.cov = cov.ShaderConvert()
		self.eui.setupUi(self)
		self.setup_defaults()
		self.button()

		if self.current != '--Create Preset--':
			self.load_config()
		self.check_info()

	def setup_defaults(self):
		self.eui.Info_renderer_Tree_1.clear()
		self.setWindowTitle('Editor')
		self.add_renderer()
		self.set_info_1()
		self.set_info_2()
		self.set_Convert_info_tree()
		self.eui.Convert_info_tree.headerItem().setText(1,"out")
		self.eui.Convert_info_tree.headerItem().setText(0,"in")

	def set_Convert_info_tree(self):
		self.eui.Convert_info_tree.clear()
		self.cov_info = []
		self.cov_info_2 = []

	def add_renderer(self):
		self.eui.Renderer_comboBox_1.clear()
		self.eui.Renderer_comboBox_2.clear()
		renderer = self.cov.get_renderers()
		for i in renderer:
			self.eui.Renderer_comboBox_1.addItem(i)

	def button(self):
		self.eui.add_button.clicked.connect(self.add_to_cov)
		self.eui.Clear_all_button.clicked.connect(self.set_Convert_info_tree)
		self.eui.Clear_sl_button.clicked.connect(self.clear_sel)
		self.eui.Convert_info_tree.itemSelectionChanged.connect(self.sel_info)
		self.eui.Save_button.clicked.connect(self.save_config)
		self.eui.add_inverse_button.clicked.connect(self.add_Invesre)
		self.eui.Renderer_comboBox_1.currentIndexChanged.connect(self.set_info_1)
		self.eui.Renderer_comboBox_2.currentIndexChanged.connect(self.set_info_2)
		
	def sel_info(self):
		sel = self.eui.Convert_info_tree.currentItem()
		sel_root = sel.parent()
		info_1 = self.eui.Info_renderer_Tree_1.topLevelItemCount()
		info_2 = self.eui.Info_renderer_Tree_2.topLevelItemCount()
		for item_info1 in range(info_1):
			item = self.eui.Info_renderer_Tree_1.topLevelItem(item_info1)
			child_info1 = item.childCount()
			if item.text(0) == sel_root.text(0):
				for child in range(child_info1):
					if item.child(child).text(0) == sel.text(0):
						self.eui.Info_renderer_Tree_1.setCurrentItem(item.child(child))
		for item_info2 in range(info_2):
			item = self.eui.Info_renderer_Tree_2.topLevelItem(item_info2)
			child_info2 = item.childCount()
			if item.text(0) == sel_root.text(1):
				for child in range(child_info2):
					if item.child(child).text(0) == sel.text(1):
						self.eui.Info_renderer_Tree_2.setCurrentItem(item.child(child))
		
	def clear_sel(self):
		count = self.eui.Convert_info_tree.topLevelItemCount()
		sel = self.eui.Convert_info_tree.currentItem()
		sel_root = sel.parent()
		try:
			child_count = sel_root.childCount()
		except:
			pass
		for j in range(count):
			top = self.eui.Convert_info_tree.topLevelItem(j)
			if top.text(0) == sel.text(0):
				self.eui.Convert_info_tree.takeTopLevelItem(j)
		for i in range(child_count):
			child = sel_root.child(i)
			if child.text(0) == sel.text(0):
				sel_root.takeChild(i)
				
	def add_Invesre(self):
		sel = self.eui.Convert_info_tree.currentItem()
		sel.setText(2,"Inverse")

	def add_to_cov(self):
		self.font = QtGui.QFont()
		self.eui.Convert_info_tree.expandAll()
		info_1 = self.eui.Info_renderer_Tree_1.currentItem()
		info_2 = self.eui.Info_renderer_Tree_2.currentItem()
		root = info_1.parent()
		root_2 = info_2.parent()
		count = self.eui.Convert_info_tree.topLevelItemCount()
		for i in range(count):
			tex = self.eui.Convert_info_tree.topLevelItem(i)
			self.cov_info.append(tex.text(0))
		if root and root_2:
			if root.text(0) in self.info_1_item and root_2.text(0) in self.info_2_item:
				if root.text(0) not in self.cov_info:
					self.font.setPointSize(8)
					self.cov_info.append(root.text(0))
					self.cov_info_2.append(root_2.text(0))
					item = QtWidgets.QTreeWidgetItem(self.eui.Convert_info_tree)
					item.setText(0,root.text(0))
					item.setText(1,root_2.text(0))
					item.setFont(0,self.font)
					child = QtWidgets.QTreeWidgetItem()
					self.font.setPointSize(7)
					child.setText(0,info_1.text(0))
					child.setText(1,info_2.text(0))
					child.setFont(0,self.font)
					item.addChild(child)
					self.eui.Convert_info_tree.expandAll()
				else:
					for i in range(count):
						top = self.eui.Convert_info_tree.topLevelItem(i)
						top_count = top.childCount()
						if root.text(0) == top.text(0) and root_2.text(0) == top.text(1):
							child_count = top.childCount()
							child = QtWidgets.QTreeWidgetItem()
							self.font.setPointSize(7)
							child.setText(0,info_1.text(0))
							child.setText(1,info_2.text(0))
							child.setFont(0,self.font)
							top.addChild(child)
		else:
			if info_1.text(0) in self.info_1_item:
				if info_1.text(0) not in self.cov_info:
					self.font.setPointSize(8)
					self.cov_info.append(info_1.text(0))
					item = QtWidgets.QTreeWidgetItem(self.eui.Convert_info_tree)
					item.setText(0,info_1.text(0))
					item.setText(1,info_2.text(0))
					item.setFont(0,self.font)
					item.setFont(1,self.font)				

	def set_info_1(self):
		renderer = self.cov.get_renderers()
		renderer_cur = self.eui.Renderer_comboBox_1.currentText()
		self.eui.Info_renderer_Tree_1.setHeaderHidden(True)
		plugin = self.cov.get_plugin(renderer_cur)
		shader = self.cov.get_shader_node(plugin)
		self.eui.Info_renderer_Tree_1.clear()
		for i in shader:
			self.info_1_item.append(i)
			self.font.setPointSize(8)
			item = QtWidgets.QTreeWidgetItem(self.eui.Info_renderer_Tree_1)
			item.setText(0,i)
			item.setFont(0,self.font)
			attr_all = self.cov.get_attribute_shader(i)
			for attr in attr_all:
				child = QtWidgets.QTreeWidgetItem(item)
				self.font.setPointSize(7)
				child.setText(0,attr)
				child.setFont(0,self.font)
		self.eui.Renderer_comboBox_2.clear()
		for j in renderer:
			if j != renderer_cur:
				self.eui.Renderer_comboBox_2.addItem(j)

	def set_info_2(self):
		renderer = self.eui.Renderer_comboBox_2.currentText()
		self.eui.Info_renderer_Tree_2.setHeaderHidden(True)
		plugin = self.cov.get_plugin(renderer)
		shader = self.cov.get_shader_node(plugin)
		self.eui.Info_renderer_Tree_2.clear()
		for i in shader:
			self.info_2_item.append(i)
			item = QtWidgets.QTreeWidgetItem(self.eui.Info_renderer_Tree_2)
			self.font.setPointSize(8)
			item.setText(0,i)
			item.setFont(0,self.font)
			attr_all = self.cov.get_attribute_shader(i)
			for attr in attr_all:
				child = QtWidgets.QTreeWidgetItem()
				self.font.setPointSize(7)
				child.setText(0,attr)
				child.setFont(0,self.font)
				item.addChild(child)
	
	def save_config(self):
		renderer_in = self.eui.Renderer_comboBox_1.currentText()
		renderer_out = self.eui.Renderer_comboBox_2.currentText()
		data = {"renderer":[renderer_in,renderer_out]}
		count = self.eui.Convert_info_tree.topLevelItemCount()
		for i in range(count):
			item = self.eui.Convert_info_tree.topLevelItem(i)
			attr = {}
			item_count = item.childCount()
			for j in range(item_count):
				out_attr =[]
				out_attr.append(item.child(j).text(1))
				out_attr.append(item.child(j).text(2))
				attr[item.child(j).text(0)] = out_attr
			shader = []
			shader.append(item.text(1))
			attr[item.text(0)] = shader
			data[item.text(0)] = attr
		if self.current != '--Create Preset--':
			file_name = "%sto%s"%(renderer_in,renderer_out)
			self.cov.jsonfile_save(data,file_name)
		else:
			file_nameui = filename_ui(data,getMayaWindow())
			file_nameui.show()

	def load_config(self):
		data = self.cov.jsonfile_load(self.current)
		shader = data.keys()
		shader.remove('renderer')
		for i in shader:
			item = QtWidgets.QTreeWidgetItem(self.eui.Convert_info_tree)
			item.setText(0,i)
			self.font.setPointSize(8)
			item.setFont(0,self.font)
			item.setFont(1,self.font)
			for vel in data[i].keys():
				if vel != i:
					child = QtWidgets.QTreeWidgetItem()
					child.setText(0,vel)
					child.setText(1,data[i][vel][0])
					child.setText(2,data[i][vel][1])
					self.font.setPointSize(7)
					child.setFont(0,self.font)
					child.setFont(1,self.font)
					item.addChild(child)
					self.eui.Convert_info_tree.expandAll()
				else:
					item.setText(1,data[i][vel][0])
		self.eui.Renderer_comboBox_1.setCurrentText(data['renderer'][0])
		self.eui.Renderer_comboBox_2.setCurrentText(data['renderer'][1])
		self.eui.Renderer_comboBox_1.setEnabled(False)
		self.eui.Renderer_comboBox_2.setEnabled(False)

	def check_info(self):
		count_convert = self.eui.Convert_info_tree.topLevelItemCount()
		count_info1 = self.eui.Info_renderer_Tree_1.topLevelItemCount()
		count_info2 = self.eui.Info_renderer_Tree_2.topLevelItemCount()
		for num in range(count_convert):
			top = self.eui.Convert_info_tree.topLevelItem(num)
			for info1 in range(count_info1):
				item1 = self.eui.Info_renderer_Tree_1.topLevelItem(info1)
				if top.text(0) == item1.text(0):
					self.font.setPointSize(8)
					self.font.setItalic(True)
					item1.setFont(0,self.font)
			for info2 in range(count_info2):
				item2 = self.eui.Info_renderer_Tree_2.topLevelItem(info2)
				if top.text(1) == item2.text(0):
					self.font.setPointSize(8)
					self.font.setItalic(True)
					item2.setFont(0,self.font)

class filename_ui(QtWidgets.QMainWindow):
	"""docstring for filename_ui"""
	def __init__(self,data, parent=None):
		super(filename_ui, self).__init__(parent=parent)
		self.fui = filenameui.Ui_filename()
		self.fui.setupUi(self)
		self.data = data
		self.cov = cov.ShaderConvert()
		self.setWindowTitle('File Name')
		self.button()
	
	def button(self):
		self.fui.ok.clicked.connect(self.save_config)

	def save_config(self):
		file_name = self.fui.file_name.text()
		self.cov.jsonfile_save(self.data,file_name)	
		self.close()

def show():
	global app
	try:
		app.close()
	except:
		pass
	app = MainApp(getMayaWindow())
	app.show()
	
def getMayaWindow(): 
	import maya.OpenMayaUI as mui
	ptr = mui.MQtUtil.mainWindow()
	return wrapInstance(long(ptr), QtWidgets.QWidget)