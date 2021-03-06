import os

import maya.cmds as cmds

path = os.path.dirname(__file__)

for f in os.listdir(path):

    if not f.startswith('__init__'):
        cmds.loadPlugin(os.path.join(path, f), qt=True)
