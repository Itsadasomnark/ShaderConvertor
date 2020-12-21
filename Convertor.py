import maya.cmds as mc
import os
import json
from collections import OrderedDict
render_dic = {'arnold': 'mtoa', 'vray': 'vrayformaya', 'renderman': 'RenderMan_for_Maya','redshift': 'redshift4maya'}
ignore_value = ["message","caching","frozen","isHistoricallyInteresting","nodeState","binMembership"]
ignore_shader = ["VRayPluginNodeMtl","VRayPluginNodeVolume"]
path = os.path.realpath(__file__)
class ShaderConvert():
    
    def __init__(self):
        self.engines = self.get_renderers()
        self.path = self.get_path_module()
        
    def get_renderers(self):
        render_engines = []
        render_name = mc.renderer(query=True, namesOfAvailableRenderers=True)
        for renderers in render_name:
            if renderers in ['arnold','vray','renderman','redshift']:
                render_engines.append(renderers)
        return render_engines
    
    def get_plugin(self,engines):
        plugins = render_dic[engines]
        return plugins
    
    def get_shader_node(self,plugins):
        render_nodes = []
        shader_nodes = mc.listNodeTypes('shader')
        nodes = mc.pluginInfo(plugins, dn=1, query=True)
        for i in shader_nodes:
            if i in nodes:
                render_nodes.append(i)
        for j in ignore_shader:
            try:
                render_nodes.remove(j)
            except:
                pass
        return render_nodes

    def get_attribute_shader(self,render_node):
        attr_dic = {}
        all_attr = mc.attributeInfo(all=True,type=render_node)
        for i in ignore_value:
            all_attr.remove(i)
        return all_attr

    def get_shader_for_obj(self,sl):
        mat_name = []
        if sl:
            for o in sl:
                shape = mc.listRelatives(o, shapes=True,pa=True)
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


    def jsonfile_load(self,file_name):
        file_name += '.json'
        path = self.path + '/config'
        with open('%s/%s'%(path,file_name)) as json_file:
            data = json.load(json_file,object_pairs_hook=OrderedDict)
        return data

    def jsonfile_save(self,data,file_name):
        path = self.path + '/config'
        with open('%s/%s.json'%(path,file_name), 'w') as jsonfile:
            json.dump(data, jsonfile,sort_keys=True,indent=4)

    def get_out_attr(self,node,data,in_attr):
        out_attr = []
        try:
            node_attr = data[node]
            for i in range(len(in_attr)):
                out_attr.append(node_attr[in_attr[i]])
        except:
            pass
        return out_attr
    
    def re_assign(self,sl,shdSG):
        mc.select(sl)
        mc.sets(sl, e=True, forceElement=shdSG)


    def get_obj(self):
        mc.SelectAllGeometry()
        sl = mc.ls(sl=1)
        check = mc.ls(sl=1)
        for i in range(len(sl)):
            shd = mc.listRelatives(sl[i], shapes=True,pa=True)
            w = mc.listConnections(shd,type = 'shadingEngine')
            if w == None:
                check.remove(sl[i])
        return check

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
        objects = []
        for i in range(len(materials)):
            if materials[i] not in shader:
                shader.append(materials[i])
        for e in range(len(sl)):
            shape = mc.listRelatives(sl[e], shapes=True,pa=True)
            shadeEng = mc.listConnections(shape,type = 'shadingEngine')
            mat = mc.ls(mc.listConnections(shadeEng), materials = True)
            for j in range(len(shader)):
                if shader[j] in shader_list:
                    if shader[j] == mat[0]:
                        shader_list[shader[j]].append(sl[e])
                else:
                    if shader[j] == mat[0]:
                        shader_list[shader[j]]=[sl[e]]
        return shader_list
    
    def covert(self,data):
        sl = self.get_obj()
        materials = self.get_shader_for_obj(sl)
        chack_mat = self.get_shader_for_obj(sl)
        node_Type = []
        shader = []
        shdSG_list = []
        new_shader = []
        ######################################## Create shader ############################################################         
        for i in range(len(materials)):
            attr_shader = {}
            node_Type.append(mc.nodeType(materials[i]))
            if node_Type[i] in data.keys():
                print node_Type[i]
                attr_shader = data[node_Type[i]]
                new_name = '%s_%s'%(materials[i],data[node_Type[i]][node_Type[i]][0])
                in_attr = attr_shader.keys()
                out_attr = self.get_out_attr(node_Type[i],data,in_attr)
                shader_his = mc.listHistory(materials[i])
                shader_his.remove(materials[i])
                if materials[i] not in shader:
                    shd = mc.shadingNode(data[node_Type[i]][node_Type[i]][0], asShader=1, name = new_name)
                    shdSG = mc.sets(name='%sSG' % shd, empty=True, renderable=True, noSurfaceShader=True)
                    shdSG_list.append(shdSG)
                    mc.connectAttr('%s.outColor' % shd, '%s.surfaceShader' % shdSG)
                    shader.append(materials[i])
                    new_shader.append(new_name)
                    for g in range(len(in_attr)):
                        if in_attr[g] != node_Type[i]:
                            get_vel = mc.getAttr('%s.%s'%(materials[i],in_attr[g]))
                            if "Inverse" in out_attr[g]:
                                get_vel = 1.0-get_vel
                            try:
                                set_vel = mc.setAttr('%s.%s'%(new_name,out_attr[g][0]),get_vel)
                                if 'redshift' == data['renderer'][1]:
                                    mc.setAttr('%s.refl_fresnel_mode'%new_name,2)
                                    mc.setAttr('%s.refl_brdf'%new_name,1)
                            except:
                                try:
                                    set_vel = mc.setAttr('%s.%s'%(new_name,out_attr[g][0]),get_vel,get_vel,get_vel,type='double3')
                                except:
                                    pass

                            mat_connect = mc.listConnections('%s.%s'%(materials[i],in_attr[g]),d=False, s=True, p=True)
            ################################################# create shader child ################################################
                            if mat_connect != None:
                                for j in range(len(shader_his)):
                                    name_node_con = shader_his[j]
                                    node_connect = mc.listConnections(name_node_con,d=True, s=False, p=True)
                                    Type_node_con = mc.nodeType(name_node_con)
                                    if Type_node_con in data.keys():
                                        attr_shader_in = data[Type_node_con]
                                        in_attr_in = attr_shader_in.keys()
                                        out_attr_in = self.get_out_attr(Type_node_con,data,in_attr_in)
                                        new_name_in = '%s_%s'%(name_node_con,data[Type_node_con][Type_node_con][0])
                                        if name_node_con not in shader:
                                            shd = mc.shadingNode(data[Type_node_con][Type_node_con][0], asShader=1, name = new_name_in)
                                            shdSG = mc.sets(name='%sSG' % shd, empty=True, renderable=True, noSurfaceShader=True)
                                            shdSG_list.append(shdSG)
                                            mc.connectAttr('%s.outColor' % shd, '%s.surfaceShader' % shdSG)
                                            for f in range(len(in_attr_in)):
                                                if in_attr_in[f] != Type_node_con:
                                                    get_vel_in = mc.getAttr('%s.%s'%(name_node_con,in_attr_in[f]))
                                                    if "Inverse" in out_attr_in[f]:
                                                        get_vel_in = 1.0 - get_vel_in
                                                    try:
                                                        set_vel_in = mc.setAttr('%s.%s'%(new_name_in,out_attr_in[f][0]),get_vel_in)
                                                        if 'redshift' == data['renderer'][1]:
                                                            mc.setAttr('%s.refl_fresnel_mode'%new_name_in,2)
                                                            mc.setAttr('%s.refl_brdf'%new_name_in,1)
                                                    except:
                                                        pass
                                                    check_connect = mc.listConnections('%s.%s'%(name_node_con,in_attr_in[f]),d=False, s=True, p=True)
                                            
                                            
                                            new_shader.append(new_name_in)
                                            shader.append(name_node_con)

                    mat_sg = mc.listConnections('%s.outColor'%materials[i], d=True, s=False)
                    sg_type = mc.nodeType(mat_sg[0])
            ############################################### displacement connect#################################################
                    if sg_type == 'shadingEngine':
                        sg_connect = mc.listConnections('%s.displacementShader'%mat_sg[0],  d=False, s=True, p=True)
                        if sg_connect != None:
                            mc.connectAttr(sg_connect[0],'%s.displacementShader'%shdSG )
        
        ##########################connect node##################################################################################

        for old in range(len(shader)):
            n_type = mc.nodeType(shader[old])
            if n_type in data.keys():
                for b in data[n_type]:
                    if b != n_type:
                        con = mc.listConnections('%s.%s'%(shader[old],b),d=False,s=True,p=True)
                        if con != None:
                            n_con = con[0].split('.')[0]
                            for d in range(len(new_shader)):
                                if n_con == shader[d]:
                                    if mc.listConnections('%s.%s'%(new_shader[old],data[n_type][b][0])) == None:
                                        mc.connectAttr('%s.%s'%(new_shader[d],con[0].split('.')[1]) , '%s.%s'%(new_shader[old],data[n_type][b][0]))
                                if n_con not in shader:
                                    if mc.listConnections('%s.%s'%(new_shader[old],data[n_type][b][0])) == None:
                                        if "Inverse" in data[n_type][b]:
                                            reverse = mc.shadingNode('reverse', asUtility=1)
                                            mc.connectAttr('%s'%con[0],'%s.inputX'%reverse)
                                            mc.connectAttr('%s.outputX'%reverse,'%s.%s'%(new_shader[old],data[n_type][b][0]))
                                        else:
                                            mc.connectAttr(con[0],'%s.%s'%(new_shader[old],data[n_type][b][0]))
                                            if 'vray' == data['renderer'][1]:
                                                if data[n_type][b][0] == 'bumpMap':
                                                    bump = mc.listConnections('%s.%s'%(new_shader[old],data[n_type][b][0]))
                                                    bump_con = mc.listConnections(bump,d=False, s=True)
                                                    mc.disconnectAttr(con[0],'%s.%s'%(new_shader[old],data[n_type][b][0]))
                                                    mc.delete(bump[0]) 
                                                    mc.connectAttr('%s.outColor'%bump_con[0],'%s.%s'%(new_shader[old],data[n_type][b][0]))
                                            if 'vray' == data['renderer'][0]:
                                                if b == 'bumpMap':
                                                    bump = mc.listConnections('%s.%s'%(new_shader[old],data[n_type][b][0]))
                                                    bump2d = mc.shadingNode('bump2d',asUtility=1,n='%s_bump2d'%bump[0])
                                                    mc.connectAttr('%s.outAlpha'%bump[0],'%s.bumpValue'%bump2d)
                                                    mc.disconnectAttr(con[0],'%s.%s'%(new_shader[old],data[n_type][b][0]))
                                                    mc.connectAttr('%s.outNormal'%bump2d,'%s.%s'%(new_shader[old],data[n_type][b][0]))
                                    else:
                                        pass

        #######################################################################################################################                                
        for obj in range(len(sl)):
                for j in range(len(shader)):
                    a = mc.listRelatives(sl[obj], shapes=True,pa=True)
                    b = mc.listConnections(a,type = 'shadingEngine')
                    c = mc.ls(mc.listConnections(b), materials = True)
                    if c[0] == shader[j]:
                        self.re_assign(sl[obj],shdSG_list[j])
        sg = []
        for h in shader:
            s = mc.listConnections('%s.outColor'%h,s=False, d=True)
            for e in s:
                if mc.nodeType(e) == 'shadingEngine':
                    sg.append(e)

        return shader,sg

    def get_path_module(self):
        path = os.path.realpath(__file__)
        file_name = str(path).split('\\')[-1:]
        path_module = str(path).split('\\%s'%file_name[0])[0]
        path_module = path_module.replace('\\','/')
        return path_module
    
    def get_config_file(self):
        path = self.get_path_module()
        path += '/config'
        files = os.listdir(path)
        file_name = []
        for file in files:
            file_name.append(file.split('.json')[0])
        return file_name