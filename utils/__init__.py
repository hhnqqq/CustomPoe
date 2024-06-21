'''
@author: hhn
@comment：一些常用函数，直接导入这个文件夹会导致导入一些没有用的东西，尽量只导入子文件
'''

import sys
import os
sys.path.append(os.path.curdir)
# 存放调用各种api的代码
from .api import *
# 存放各种templates
from .constant import *
# 存放各种小工具
from .utils import *
