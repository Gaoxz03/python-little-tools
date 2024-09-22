import os
import shutil

# root Dir 
Root_Dir = os.path.abspath('.')

print(Root_Dir)

# item in root dir
Item_List = os.listdir(Root_Dir)

print(Item_List)

for i in range(0, len(Item_List)):
    path = os.path.join(Root_Dir,Item_List[i])
    if os.path.isdir(path):
        for item in os.listdir(path):
            # 一级子路径
            Sub_Dir_Name = os.path.join(Root_Dir,Item_List[i])
            # 完整的文件、文件夹路径
            File_Full_Path = os.path.join(Sub_Dir_Name,item)
            # 移动的目标路径
            Target_Path = Root_Dir
            
            shutil.move(File_Full_Path, Target_Path)
            shutil.rmtree(Sub_Dir_Name)
            print("Move File : " + File_Full_Path +" ==> " + Target_Path)