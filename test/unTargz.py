import tarfile
import os
import shutil

# 模块测试
# update_file = ['updateAI.py', 'main.py', 'main_back.py', 'check_all.py', 'peidianfang.om']
'''
update_path= {
    'updateAI.py': './updateAI.py',
    'main.py': './main.py',
    'main_back.py': './main_back.py',
    'check_all.py': './check_all.py',
    'peidianfang.om': './model/peidianfang.om',
    'model_dir': './model',
    'py_dir': './'
}
'''

update_file = ['updateAI.txt', 'test123.txt', 'main_back.txt', 'check_all.txt', 'peidianfang.om']
update_path = {
    'updateAI.txt': './updateAI.txt',
    'main.txt': './main.txt',
    'main_back.txt': './main_back.txt',
    'check_all.txt': './check_all.txt',
    'peidianfang.om': './model/peidianfang.om',
    'test123.txt':'./test123.txt',
    'model_dir': './model',
    'py_dir': './'
}

try:
    tar = tarfile.open('./update/test123.tar.gz')
    names = tar.getnames()
    print(names)
    for name in names:

        if name == 'peidianfang.om' and name in update_file:
            shutil.copyfile(update_path[name], update_path[name] + '.back')
            print('模型%s已备份' % name)
            tar.extract(name, path=update_path['model_dir'])
            print('模型文件%s已替换' % name)

        elif name in update_file:
            shutil.copyfile(update_path[name], update_path[name] + '.back')
            print('程序文件%s已备份' % name)
            tar.extract(name, path=update_path['py_dir'])
            print('程序文件%s已替换' % name)

    tar.close()
except Exception as e:
    print(e)
