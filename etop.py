#!/home/mu42cuq/python_3.6/Python-3.6.0/bin/python3.6
#-*- coding: utf-8 -*-

import time
import pickle
import subprocess
from random import randint

araUsers = pickle.load(open('/home/mu42cuq/araUsers.pydict', 'rb'))

partition = {x: {'tot': 0, 'run': 0, 'pen': 0} for x in
             ['s_standard', 's_fat', 'b_standard', 'b_fat', 'gpu_p100', 'gpu_v100']}

currUsers = {}

lastNodeName = ''
for lin in subprocess.getoutput('scontrol show partition').split('\n'):
    if 'PartitionName=' in lin:
        lastNodeName = lin.split('PartitionName=')[1].strip()
    elif 'TotalNodes=' in lin and lastNodeName in partition:
        partition[lastNodeName]['tot'] = int(lin.split('TotalNodes=')[1].split()[0])


for lin in subprocess.getoutput('squeue | iconv --to-code utf-8//IGNORE').split('\n')[1:]:
    nil = lin.strip().split()
    if 'standar' in nil[1]:
        nil[1] = f'{nil[1]}d'
    if nil[3] not in currUsers:
        currUsers[nil[3]] = {x: {'run': 0, 'pen': 0} for x in
                             ['s_standard', 's_fat', 'b_standard', 'b_fat', 'gpu_p100', 'gpu_v100']}
    if nil[1] in ['s_standard', 's_fat', 'b_standard', 'b_fat', 'gpu_p100', 'gpu_v100']:
        if nil[4] == 'R':
            currUsers[nil[3]][nil[1]]['run'] += 1
            partition[nil[1]]['run'] += 1
        elif nil[4] == 'PD':
            currUsers[nil[3]][nil[1]]['pen'] += 1
            partition[nil[1]]['pen'] += 1

print('\n\n¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯\n')

print(f'{time.asctime()}\n')
print('partition\t\trunning\t\t\tpending')
print('---------\t\t-------\t\t\t-------')

for par in ['s_standard', 's_fat', 'b_standard', 'b_fat', 'gpu_p100', 'gpu_v100']:
    if 'fat' in par:
        print(f"{par}\t\t\t{partition[par]['run']}/{partition[par]['tot']} ({round(partition[par]['run']/partition[par]['tot']*100,1)}%)\t\t{partition[par]['pen']}")
    else:
        print(f"{par}\t\t{partition[par]['run']}/{partition[par]['tot']} ({round(partition[par]['run']/partition[par]['tot']*100,1)}%)\t\t{partition[par]['pen']}")

print('\n\nID\t|s_std\ts_fat\tb_std\tb_fat\tGp100\tGv100\tuser name')
print('--\t|-----\t-----\t-----\t-----\t-----\t-----\t---------')

for usr in sorted(currUsers):
    print(f"{usr}", end='\t|')
    for par in ['s_standard', 's_fat', 'b_standard', 'b_fat', 'gpu_p100', 'gpu_v100']:
        print(f"{currUsers[usr][par]['run'] if currUsers[usr][par]['run'] != 0 else '-'}", end='')
        if currUsers[usr][par]['pen'] != 0:
            print(f"({currUsers[usr][par]['pen']})", end='\t')
        else:
            print("", end='\t')
    print(f"{araUsers.get(usr, usr)[:20]:<20}")
print('\n¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯\n\n')



#test = subprocess.getoutput('ssh mu42cuq@ara-login01.rz.uni-jena.de squeue | iconv --to-code utf-8//IGNORE') 
