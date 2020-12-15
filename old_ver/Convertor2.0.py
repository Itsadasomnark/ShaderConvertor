import maya.cmds as mc
import os
import json
render_dic = {'arnold': 'mtoa', 'vray': 'vrayformaya', 'renderman': 'RenderMan_for_Maya','redshift': 'redshift4maya'}
#path = os.path.realpath(__file__)
class ShaderConvert():
    
    def __init__(self):
        self.engines = self.get_renderers()
    
    def get_renderers(self):
        render_engines = []
        render_name = mc.renderer(query=True, namesOfAvailableRenderers=True)
        for renderers in render_name:
            if renderers in ['arnold','vray','renderman','redshift']:
                render_engines.append(renderers)
        return render_engines
    
    def get_plugin(self):
    	engines = self.get_renderers()
    	plugins = []
    	for i in engines:
    		plugins.append(render_dic[i])
    	return plugins
    
    def get_shader_node(self,plugins):
    	render_nodes = []
    	shader_nodes = mc.listNodeTypes('shader')
    	nodes = mc.pluginInfo(plugins, dn=1, query=True)
    	for i in shader_nodes:
    		if i in nodes:
    			render_nodes.append(i)
    	return render_nodes

    def get_attribute_shader(self,render_node):
    	attr_dic = {}
    	all_attr = mc.attributeInfo(all=True,type=render_node)
    	return all_attr

    def get_shader_for_obj(self,sl):
    	mat_name = []
    	if sl:
    	    for o in sl:
		        shape = mc.listRelatives(o, shapes=True)
		        shadeEng = mc.listConnections(shape,type = 'shadingEngine')
		        materials = mc.ls(mc.listConnections(shadeEng), materials = True)
		        node_connect = mc.listConnections(materials,d=True, s=False, p=True)
		        for i in materials:
		            node_connect = mc.listConnections(i,d=True, s=False, p=True)
		            if '%s.displacementShader'%shadeEng[0] in node_connect:
		                pass
		            else:
		                mat_name.append(i)
        return mat_name


    def jsonfile_load(self):
    	with open('C:/Users/bossd/Desktop/Thesis/script/config/arnold.json') as json_file:
    		data = json.load(json_file)
    	return data

    def jsonfile_save(self,data):
    	with open('C:/Users/bossd/Desktop/Thesis/script/arnold.json', 'w') as jsonfile:
    		json.dump(data, jsonfile)

	def get_out_attr(self,node,data,in_attr):
    	node_attr = data[node]
    	out_attr = []
    	for i in range(len(in_attr)):
    	    out_attr.append(node_attr[in_attr[i]])
    	return out_attr
	    def re_assign(self,sl,shdSG):
        mc.select(sl)
        mc.sets(sl, e=True, forceElement=shdSG)


    def get_obj(self):
    	mc.SelectAllGeometry()
    	sl = mc.ls(sl=1)
    	return sl

    def del_old_shd(self,shader,sg):
    	mc.select(shader,r=True)
    	mc.delete()
    	mc.select(sg,r=True, ne=True)
    	mc.delete()

    def get_obj_shd(self):
    	sl = self.get_obj()
    	materials = self.get_shader_for_obj(sl)
    	shader = []	
    	shader_list = {}
    	objects_shapes = []
    	for i in range(len(materials)):
    		if materials[i] not in shader:
    			shader.append(materials[i])
    	for i in sl:
    		shape = cmds.listRelatives(i, shapes=True)
	        shadeEng = mc.listConnections(shape,type = 'shadingEngine')
    		self.get_shader_for_obj(i)
    def covert(self):
    	sl = self.get_obj()
    	materials = self.get_shader_for_obj(sl)
    	data = self.jsonfile_load()
    	node_Type = []
    	shader = []
    	num = 0
    	for i in range(len(materials)):
    		node_Type.append(mc.nodeType(materials[i]))
    		if node_Type[i] in data.keys():
    			attr_shader = data[node_Type[i]]
			in_attr = attr_shader.keys()
			out_attr = self.get_out_attr(node_Type[i],data,in_attr)
			new_name = '%s_%s'%(materials[i],data[node_Type[i]][node_Type[i]][0])
    		if materials[i] not in shader:
    			shd = mc.shadingNode(data[node_Type[i]][node_Type[i]][0], asShader=1, name = new_name)
    			shdSG = mc.sets(name='%sSG' % shd, empty=True, renderable=True, noSurfaceShader=True)
    			shdSG_list = []
    			shdSG_list.append(shdSG)
    			mc.connectAttr('%s.outColor' % shd, '%s.surfaceShader' % shdSG)
    			
    			for g in range(len(in_attr)):
    				if in_attr[g] != node_Type[0]:
    					get_vel = mc.getAttr('%s.%s'%(materials[i],in_attr[g])) 



    



a = ShaderConvert()
print a.covert()
