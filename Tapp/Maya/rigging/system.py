import Tapp.Maya.rigging.builds as mrb
reload(mrb)
import Tapp.Maya.rigging.system_utils as mrs
reload(mrs)

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler=logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(funcName)s - LINE: %(lineno)d - %(message)s'))
log.addHandler(handler)

class system(object):
    
    def __init__(self,obj,method='default'):
        
        self.chain=mrs.buildChain(obj)
        self.method=method
        self.builds=self.getBuilds()
        
    def __repr__(self):
        
        result=''
        
        for build in self.builds:
            
            if build.executeDefault:
                
                result+=build.__str__()
        
        return result
    
    def getBuilds(self):
        
        result=[]
        
        for cls in mrb.base.__subclasses__():
            temp=cls()
            temp.chain=self.chain
            
            if self.method=='default':
                if temp.executeDefault:
                    
                    result.append(temp)
            else:
                if self.method==temp.__class__.__name__:
                    
                    result.append(temp)
        
        return result

print system('|clavicle',method='guide')
'''
    def blend(self,node,control):
        
        prefix=node.name.split('|')[-1]+'_bld_'
        
        #create socket
        socket=cmds.spaceLocator(name=prefix+'socket')[0]
        
        #setup socket
        mru.Snap(None, socket,translation=node.translation,rotation=node.rotation)
        
        data=node.data
        data['name']=node.name
        metaNode=node.system.addSocket(socket,boundData={'data':data})
        if node.parent:
            metaParent=meta.r9Meta.MetaClass(node.parent.socket['blend'])
            metaParent=metaParent.getParentMetaNode()
            
            metaParent.connectChildren([metaNode],'guideChildren', srcAttr='guideParent')
        
        cmd='cmds.parentConstraint('
        for s in node.socket:
            cmd+='\''+node.socket[s]+'\','
        cmd+='\''+socket+'\')'
        con=eval(cmd)[0]
        
        for s in node.socket:
            attr=control+'.'+s
            if not cmds.objExists(attr):
                cmds.addAttr(control,ln=s,at='float',keyable=True,
                             min=0,max=1)
        
            for count in range(0,len(node.socket)):
                target=cmds.listConnections(con+'.target[%s].targetParentMatrix' % count)
                if target[0]==node.socket[s]:
                    cmds.connectAttr(control+'.'+s,con+'.'+
                                     node.socket[s]+'W%s' % count,force=True)
        
        node.socket['blend']=socket
        
        cmds.parent(socket,node.root['master'])
        
        if node.children:
            for child in node.children:
                self.blend(child,control)
    
    def switch(self,node):
        
        if len(node.control)>1:
            for control in node.control:
                
                mNode=meta.r9Meta.MetaClass(node.control[control])
                mNode=mNode.getParentMetaNode()
                
                otherControls=[]
                for c in node.control:
                    if c!=control:
                        
                        otherControl=meta.r9Meta.MetaClass(node.control[c])
                        otherControl=otherControl.getParentMetaNode()
                        otherControls.append(otherControl)
                
                mNode.connectChildren(otherControls,'switch')
        
        if node.children:
            for child in node.children:
                self.switch(child)
    
    def rootParent(self,node):
        
        for key in node.root:
            if key!='master':
                if node.parent:
                    cmds.parentConstraint(node.parent.socket['blend'],node.root[key],maintainOffset=True)
        
        if node.children:
            for child in node.children:
                self.rootParent(child)
    
    def build(self,methods=['fk','ik','spline'],blend=True,deleteSource=True):
        
        #if methods is a string
        if isinstance(methods,str):
            checkList=['fk','ik','joints','spline','guide']
            if not methods in checkList:
                self.log.error('build: methods input string invalid!')
                return
            else:
                methods=[methods]
        
        #checking input type
        if not isinstance(methods,list):
            self.log.error('build: methods is a not a list!')
            return
        
        #delete source
        if deleteSource:
            
            if self.chain.root:
                
                log.debug('deleting the source: %s' % self.chain.root['master'])
                
                cmds.delete(self.chain.root['master'])
                self.chain.root['master']=None
            
            if self.chain.system:
                for control in self.chain.system.getChildren(cAttrs='controls'):
                    meta.r9Meta.MetaClass(control).delete()
                    
                for socket in self.chain.system.getChildren(cAttrs='sockets'):
                    meta.r9Meta.MetaClass(socket).delete()
                
                log.debug('deleting the system: %s' % self.chain.system)
                
                self.chain.system.delete()
                self.chain.system=None
        
        #adding root and system
        if ['guide','joints'] not in methods:
            #rig asset
            #asset=cmds.container(n='rig',type='dagContainer')
            asset=cmds.group(empty=True,n='rig')
            attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz']
            mru.ChannelboxClean(asset, attrs)
            
            self.chain.addRoot(asset,'master')
            
            #meta rig
            system=meta.MetaSystem()
            
            system.root=asset
            
            self.chain.addSystem(system)
        
        #build methods
        for method in methods:
            if method=='fk':
                for c in self.fk_chains:
                    mrb.fk_build(c)
            
            if method=='ik':
                for c in self.ik_chains:
                    mrb.ik_build(c)
            
            if method=='joints':
                mrb.joints_build(self.chain)
            
            if method=='guide':
                mrb.guide_build(self.chain)
        
        #blending
        if blend and ['guide','joints'] not in methods:
            
            #create extra control
            cnt=mru.Pin('extra_cnt')
            
            #create blend sockets
            self.blend(self.chain,cnt)
            
            #setup extra control
            mru.Snap(None,cnt,translation=self.chain.translation,rotation=self.chain.rotation)
            
            cmds.parent(cnt,self.chain.socket['blend'])
            cmds.rotate(0,90,0,cnt,r=True,os=True)
            
            if cmds.objExists(asset+'.ik_stretch'):
                cmds.addAttr(cnt,ln='ik_stretch',at='float',k=True,
                             min=0,max=1)
                
                cmds.connectAttr(cnt+'.ik_stretch',asset+'.ik_stretch')
            
            system.addControl(cnt,'extra')
            
            #parenting roots
            self.rootParent(self.chain)
        
        #switching
        self.switch(self.chain)
        '''

'''
need to have args* on all
need to treat chain as the data container it is! still need to be able to build a system directly from a node, instead of having to build the chain first
    chain should not container anything to do with the system or build
should treat the system as an overall system container, and have no operations specific to a build
plugs!
build spline
possibly need to not have one attr for activating systems, and go to each socket and activate the system if its present
hook up controls visibility to blend control
better inheritance model
place guides like clusters tool
    if multiple verts, use one of them to align the guide towards
'''