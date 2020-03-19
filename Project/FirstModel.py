import os
from os.path import isfile, join
import shutil as shu
import random


def cut_test_doc(src_folder='Collection_cs276', folder='Collection', num_per_index=50, randomly=False):
    cur_dir = os.getcwd()
    src_dir = cur_dir + '\\' + src_folder + '\\'
    new_dir = cur_dir + '\\' + folder + '\\'
    print(cur_dir)
    try:
        if os.path.exists(new_dir):
            go_on = ''
            while go_on not in {'y', 'n'}:
                go_on = input('folder exists, continue? y/n')
            if go_on == 'y':
                try:
                    shu.rmtree(new_dir)
                    print('old folder deleted:', not os.path.exists(new_dir))
                except OSError:
                    print('delete folder failed')
            else:
                print('Execution interrupted.')
                return
        os.mkdir(new_dir)
        for i in range(10):
            os.mkdir(new_dir + str(i))
        print('empty folder is ready')
    except OSError:
        print("path not found error")
    #
    for i in range(10):
        onlyfiles = [f for f in os.listdir(src_dir + str(i)) if isfile(join(src_dir + str(i), f))]
        for j in range(min(len(onlyfiles), num_per_index)):
            if randomly:
                random_index = random.randint(0, len(onlyfiles))
                onlyfiles.pop(random_index)
            else:
                random_index = j
            shu.copy(src_dir + str(i) + '\\' + onlyfiles[random_index],
                     new_dir + str(i) + '\\' + onlyfiles[random_index])
    print('new folder created')


if __name__ == '__main__':
    cut_test_doc()