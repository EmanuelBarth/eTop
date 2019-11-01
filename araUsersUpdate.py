#!/home/mu42cuq/programs/Python-3.6.2/bin/python3.6
#-*- coding: utf-8 -*-

import pickle
import subprocess
import re

araUsers = pickle.load(open('/home/mu42cuq/scripts/araUsers.pydict', 'rb'))

newDict = {}
for userID in set(re.findall('[a-z][a-z]\d\d[a-z][a-z][a-z]', subprocess.getoutput('ssh mu42cuq@ara-login01.rz.uni-jena.de squeue | iconv --to-code utf-8//IGNORE'))):
    print(f'Checking User {userID}', end='\r')
    try:
        newDict[userID] = subprocess.getoutput(f'finger {userID}').split('\t\t\tName: ')[1].split('\n')[0]
    except:
        newDict[userID] = userID
print('')
araUsers.update(newDict)
pickle.dump(araUsers, open('/home/mu42cuq/scripts/araUsers.pydict', 'wb'))
if subprocess.getstatusoutput('scp /home/mu42cuq/scripts/araUsers.pydict ara-login01.rz.uni-jena.de:/home/mu42cuq/araUsers.pydict')[0] != 0:
    print('Could not save araUsers.pydict to ARA. Something wrong with the connection?')
