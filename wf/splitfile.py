# -*- coding: UTF-8 -*-

import os


def splitfile(filename, outfolder, step=100000):

    try:
        os.makedirs(outfolder)
    except OSError:
        pass
    filename = os.path.normpath(filename)
    name = os.path.basename(filename)
    name, ext = os.path.splitext(name)
    i = 0
    with open(filename) as f:
        while True:
            out = f.read(step)
            if not out:
                print "End of file"
                break
            else:
                i += 1
                fname = name + str(i) + ext
                savepath = os.path.join(outfolder, fname)
                open(savepath, 'w').write(out)

if __name__ == "__main__":
    # То, что в кавычках замени на свои пути: первый - к файлу (который разбиваем),
    # второй - к папке, куда создать файлы.
    # Число - по сколько символов (100000 норм)
    splitfile(r'E:\OneDrive\Programs for Everything\flaskHelloWorld\wf\testIn.txt',
              r'E:\OneDrive\Programs for Everything\flaskHelloWorld\wf\test',
              100000)
