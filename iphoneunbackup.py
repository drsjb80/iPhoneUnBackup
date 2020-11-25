import os
import plistlib
import shutil
import sqlite3
import sys
import time

# https://www.richinfante.com/2017/3/16/reverse-engineering-the-ios-backup#manifestdb

# CREATE TABLE Files (fileID TEXT PRIMARY KEY, domain TEXT, dst TEXT, flags INTEGER, file BLOB);

connection = sqlite3.connect('Manifest.db')
debug = False

for row in connection.execute('SELECT * FROM Files'):
    if debug: print(row)

    plist = plistlib.loads(row[4])
    if debug: print('plist:', plist)

    size = plist['$objects'][1]['Size']
    if debug: print('size:', size)

    birth = plist['$objects'][1]['Birth']
    if debug: print('birth:', time.gmtime(birth))

    dst = row[2]
    if debug: print('dst:', dst)

    if size == 0:
        if dst != '' and not os.path.isdir(dst):
            if debug: print('mkdir', dst)
            os.mkdir(dst)
            os.utime(dst, (birth, birth))
        continue

    dirname = os.path.dirname(dst)
    if dirname != '' and not os.path.isdir(dirname):
        os.mkdir(dirname)
        os.utime(dirname, (birth, birth))

    src = row[0]
    src = src[:2] + '/' + src

    print('copy from:', src, 'to:', dst)
    shutil.copy(src, dst)
    os.utime(dst, (birth, birth))

connection.close()
