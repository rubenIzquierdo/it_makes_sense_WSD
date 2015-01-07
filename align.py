#!/usr/bin/env python
import sys
l1 = ['its','true','they are', 'offering','money']
ids = ['a','b','c','d','e','f']
l2 = ['its','true','they','are', 'offering','money']

def align_lists(l1,ids,l2):
    """
    Aligns two lists of tokens with different tokenisation.
    l1: is the list of original tokens
    ids1: is the list of ids for the tokens in l1 (len(l1) must be equal to len(l2))
    l2: is the new list of tokens
    Returns: a list of the same len of l2 with the corresponding ids
    l1 = ['its','true','they are', 'offering','money']
    ids = ['a','b','c','d','e','f']
    l2 = ['its','true','they','are', 'offering','money']
    """
    ids2 = []

    pos1 = offset1 = 0
    pos2 = 0
    while True:
        this_ele = l2[pos2]
        ele_to_compare = l1[pos1].replace(' ','')
        string_compare = ele_to_compare[offset1:offset1+len(this_ele)]
        if this_ele != string_compare:
            print>>sys.stderr,'Impossible to match #'+this_ele+'# with #'+string_compare+'#'
            ids2 = None
            break
        print this_ele, ids[pos1], string_compare
        ids2.append(ids[pos1])
      
        offset1 = offset1 + len(this_ele)
        if offset1 >= len(ele_to_compare):
            pos1+=1
            offset1=0
        pos2 += 1
        if pos2 == len(l2):
            break
    return ids2

if __name__ == '__main__':
    
    l1 = ['its','true','they are', 'offering','money']
    ids = ['a','b','c','d','e','f']
    l2 = ['its','true','they','are', 'offering','money']
    ids2 = align_lists(l1,ids,l2)
    print 'L1:',l1
    for n in range(len(l1)):
        print ids[n],'-->',l1[n]
    print 'L2:', l2

    for n in range(len(l2)):
        print l2[n], ids2[n]
    

