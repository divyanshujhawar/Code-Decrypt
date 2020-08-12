#!/usr/local/bin/python3
# CSCI B551 Fall 2019
#
# Authors: Divyanshu Jhawar - djhawar, Vamsi Bushan - vbushan, Manuja Bandal - msbandal 
#
# based on skeleton code by D. Crandall, 11/2019
#
# ./break_code.py : attack encryption
#


import random
from random import shuffle
import math
import copy 
import sys
import time
import encode

# put your code here!
def break_code(string, corpus):

    doc = []

    # seconds for each interval
    duration = 75

    # Creating probability distribution from corpus
    mat = create_prob_mat(corpus)

    for itr in range(8):

        st = time.time()

        rep_table = create_replacement_table()

        rea_table = create_rearrangement_table()

        d = encode.encode(string,rep_table,rea_table)
        p_d = calculate_score(d,mat)

        best_set = [-1, ""]

        changed = 0

        i = 0

        while i < 6000 and (time.time()-st < duration):

            ran = random.random()

            # 0.5 Prob to choose either change in replacement or rearrangement table
            if ran >= 0.5:
                new_rep_table = change_replacement_table(rep_table)
                new_rea_table = rea_table

            else:
                new_rep_table = rep_table
                new_rea_table = change_rearrangement_table(rea_table)

            
            # Updating only when we update the tables
            if changed:
                d = encode.encode(string,rep_table,rea_table)
                p_d = calculate_score(d,mat)
    

            d_dash = encode.encode(string, new_rep_table, new_rea_table)
            p_d_dash = calculate_score(d_dash,mat)


            # Metropolis-Hastings Algo
            if p_d_dash > p_d:
                rep_table = new_rep_table
                rea_table = new_rea_table
                changed = 1

            else:

                ratio = p_d_dash - p_d

                ran = random.random()

                if ran <= ratio:
                    rep_table = new_rep_table
                    rea_table = new_rea_table
                    changed = 1


            if best_set[0] < p_d_dash:
                best_set[0] = p_d_dash
                best_set[1] = d_dash
            
            i+=1

        doc.append(best_set)

        best = max(doc)[1]

    return best

# To calculate the likelihood
def calculate_score(string,mat):

    score = 0

    space = ' '

    temp = ' '

    for ch in string:

        if ch == space:

            if temp == space:
                score += mat[26][26]
            else:
                score += mat[26][ord(temp)-97]
        else:

            if temp == space:
                score += mat[ord(ch)-97][26]
            else:
                score += mat[ord(ch)-97][ord(temp)-97]
        
        temp = ch

    return score

# Initialization
def create_replacement_table():

    temp1 = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',' ']
    temp2 = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',' ']

    shuffle(temp2)

    rep_table = {}

    for i in range(27):
        rep_table[temp1[i]] = (temp2[i])
    return rep_table

def create_rearrangement_table():

    rea_table = [2,0,1,3]
    shuffle(rea_table)

    return rea_table

# This function makes update to replacement table
def change_replacement_table(rep_table):

    temp = random.sample(set(['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',' ']), 2)

    var = {}

    for key in rep_table:
        var[key] = rep_table[key]

    t = var[temp[0]]

    var[temp[0]] = var[temp[1]]

    var[temp[1]] = t

    return var

# This function makes update to replacement table
def change_rearrangement_table(rea_table):

    t = []
    for i in rea_table:

        t.append(i)

    temp = random.sample(range(0,4), 2)

    t[temp[0]],t[temp[1]]  =  t[temp[1]],t[temp[0]]

    return t

# Creating initial probability distribution
def create_prob_mat(corpus):


    mat = [[0 for i in range(27)] for j in range(27)]

    space = ' '
    flag = 1
    temp = ' '

    for ch in corpus:

        if ch == space:

            if temp == space:
                mat[26][26] += 1
            else:
                mat[26][ord(temp)-97] += 1
        else:
            if temp == space:
                mat[ord(ch)-97][26] += 1
            else:
                mat[ord(ch)-97][ord(temp)-97] += 1
        

        temp = ch

    for i in range(len(mat)):
        
        # Just a large number for proportion
        m = 10000

        for x in range(len(mat[0])):
            mat[i][x] = math.log((mat[i][x]/m) + 1)

    return mat

# Main Function
if __name__== "__main__":

    if(len(sys.argv) != 4):
        raise Exception("usage: ./break_code.py coded-file corpus output-file")

    encoded = encode.read_clean_file(sys.argv[1])
    corpus = encode.read_clean_file(sys.argv[2])
    
    decoded = break_code(encoded, corpus)

    with open(sys.argv[3], "w") as file:
        print(decoded,file=file)