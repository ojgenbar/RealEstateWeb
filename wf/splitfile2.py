# -*- coding: UTF-8 -*-

import os


def create(path, length):
    out = ''
    for i in range(length):
        out += 'Строчка №%s\n' % i
    print len(out)
    open(path, 'w').write(out)


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
    # create(r'E:\OneDrive\Programs for Everything\flaskHelloWorld\wf\testIn2.txt', 1000000)
    #
    splitfile(r'E:\OneDrive\Programs for Everything\flaskHelloWorld\wf\splitfile.py',
              r'E:\OneDrive\Programs for Everything\flaskHelloWorld\wf\test',
              5)
