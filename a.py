import os,sys
import unittest

import rec
rec.TMP_DIR = 'tmp'

def printf(f):
    with open(f.filename) as f:
        print(f.read())
    print("")

if __name__ == "__main__":
    f = rec.PyFile('aaa/b.py')

    '''
    # replace, unreplace
    f.replace(4, r'print("c0")')
    printf(f)
    f.unreplace(4)
    printf(f)
    # insert, uninsert
    f.insert(4, r'print("c1")')
    printf(f)
    f.uninsert(4)
    printf(f)
    # insert, uninsert (back)
    f.insert(9, r'print("c2")', back=True)
    printf(f)
    f.uninsert(9, back=True)
    printf(f)
    # insert (diff indent)
    f.insert(1, 'a = 1')
    printf(f)
    f.insert(2, 'a = 2')
    printf(f)
    f.insert(3, 'a = 3')
    printf(f)
    f.uninsert(1)
    f.uninsert(2)
    f.uninsert(3)
    printf(f)
    # comment, uncomment
    f.comment(5)
    printf(f)
    f.uncomment(5)
    printf(f)
    # comment, uncomnet (unavailable)
    f.comment(11)
    printf(f)
    f.uncomment(3)
    printf(f)
    # comment, uncomnet (block)
    f.comment((4,6))
    printf(f)
    f.uncomment((4,6))
    printf(f)
    # comment, uncomnet (block,unavailable)
    f.comment((11,12))
    printf(f)
    f.uncomment((8,10))
    printf(f)
    # gather, reset
    f.replace(8, 'c = 2')
    printf(f)
    f.insert(8, 'a = 1')
    printf(f)
    f.insert(8, 'b = 3', back=True)
    printf(f)
    f.comment(8)
    printf(f)
    f.reset()
    printf(f)
    '''
    
    '''
    # iter replace
    for i in f.iter_replace(8, r"print('b+{}')", (20,22,24)):
        print(i)
        printf(f)
    printf(f)

    # iter insert
    for i in f.iter_insert(2, r"a = {}", (1,2,3)):
        print(i)
        printf(f)
    printf(f)
    for i in f.iter_insert(3, r"b = {}", (2,3), back=True):
        print(i)
        printf(f)
    printf(f)
    
    # iter if replace 
    for i in f.iter_if_replace(4, r"c = 3"):
        print(i)
        printf(f)
    printf(f)

    # iter if insert
    for i in f.iter_if_insert(9, r"a = 1"):
        for j in f.iter_if_insert(9, r"b = 3", back=True):
            print(i,j)
            printf(f)
    printf(f)

    # iter if comment
    for i in f.iter_if_comment(4):
        for j in f.iter_if_comment((11,12)):
            print(i,j)
            printf(f)
    printf(f)
    
    # iter if do
    ite = f.iter_if_do().replace(8, 'c = 2') \
                        .insert(8, 'a = 1') \
                        .insert(8, 'b = 3', back=True) \
                        .comment(8)
    for i in ite:
        print(i)
        printf(f)
    printf(f)
    '''

    rec.PyFile.close_all()