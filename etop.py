#!/home/go96bix/miniconda3/bin/python
#-*- coding: utf-8 -*-
# original Emanuel Barth, updated by Florian Mock

import time
import pickle
import subprocess
import curses
import sys

araUsers = pickle.load(open('/home/mu42cuq/araUsers.pydict', 'rb'))

def renaming_nodes_short(partion_names_list):
    short_names_list = []
    for name in partion_names_list:
        name_short = name[:5] # more complex namespace possible
        short_names_list.append(name_short)
    return short_names_list

def report_usage():
    stdscr.clear()
    out_multiline = ""

    partition = {}
    currUsers = {}
    currUsers_multi_partitions = {}

    lastNodeName = ''
    for lin in subprocess.getoutput('scontrol show partition').split('\n'):     #This Loop gets all the installed partitions and the corresponding available notes
        if 'PartitionName=' in lin:
            lastNodeName = lin.split('PartitionName=')[1].strip()
        elif 'TotalNodes=' in lin and not lastNodeName.endswith("_test"):                #However, only nodes from the predefined partition list are stored, to exclude all the test_nodes, which can not be accessed by the normal users anyway
            partition.update({lastNodeName:{'tot':int(lin.split('TotalNodes=')[1].split()[0]), 'run': 0, 'pen': 0}})

    partion_names_list = sorted([i for i in partition.keys() if not i.startswith('gpu')])
    partion_names_list.extend(sorted([i for i in partition.keys() if i.startswith('gpu')])) # make gpu nodes at the end

    nodes_used = set()
    for lin in subprocess.getoutput('squeue -o "%i %P %u %t %M %D %R"| iconv --to-code utf-8//IGNORE').split('\n')[1:]:      #get the current running and queued jobs along with the respective user IDs; the iconv command is needed if some dumbass uses some weird non-Unicode code points in his/her job names
        nil = lin.strip().split()
        nil.append(nil[1])
        nil[1] = nil[1].split(",")[0]        # some gpu jobs have a , at the end of PartitionName like gpu_v100,

        if nil[2] not in currUsers:
            currUsers[nil[2]] = {x: {'run': 0, 'pen': 0} for x in partion_names_list}
            currUsers_multi_partitions[nil[2]] = {x: {'run': 0, 'pen': 0} for x in partion_names_list}
        if nil[1] in partion_names_list:
            nodes = int(nil[5]) # one job can run on multiple nodes, this line fixes the issue that it always looked as if ara wasn't used fully
            if nil[3] == 'R':
                currUsers[nil[2]][nil[1]]['run'] += nodes
                nodes_this_job = nil[6][len("node"):].strip("[]").split(",") # one note can have multiple jobs, so we need to check how many new nodes are used by this job
                nodes_this_job = set([int(k) for j in nodes_this_job for k in range(int(j.split("-")[0]),int(j.split("-")[-1])+1)])
                new_nodes_used = nodes_this_job.difference(nodes_used)
                nodes_used.update(new_nodes_used)
                partition[nil[1]]['run'] += len(new_nodes_used)
            elif nil[3] == 'PD':
                currUsers[nil[2]][nil[1]]['pen'] += nodes
                if "," in nil[-1]:
                    for i in nil[-1].split(","):
                        if i in partion_names_list:
                            currUsers_multi_partitions[nil[2]][i]['pen'] += nodes
                partition[nil[1]]['pen'] += nodes

    out_multiline += '\n\n\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/\n'
    out_multiline += f'{time.asctime()}\n'
    out_multiline += 'partition\trunning\tpending\n'.expandtabs(22)  #expandtabs provides much better handling of strings with unequal length
    out_multiline += '---------\t-------\t-------\n'.expandtabs(22)

    for par in partion_names_list:
        running = f"{partition[par]['run']}/{partition[par]['tot']}\t({round(partition[par]['run']/partition[par]['tot']*100,1)}%)".expandtabs(8)
        out_multiline += f"{par}\t{running}\t{partition[par]['pen']}\n".expandtabs(22)

    partion_names_short = "".join([i+"\t" for i in renaming_nodes_short(partion_names_list)])
    out_multiline += f'\n\nID\t|{partion_names_short}user name\n'.expandtabs(9)   #These two print commands could be generalized to avoid manual correction if new partitions are added to ARA... but at the moment I'm to lazy to do it...
    out_multiline += '--\t|-----\t-----\t-----\t-----\t-----\t-----\t---------\n'.expandtabs(9)

    multi_partitions = False
    for usr in sorted(currUsers):
        out = f"{usr[:7]}\t|"
        for par in partion_names_list:
            out += f"{currUsers[usr][par]['run'] if currUsers[usr][par]['run'] != 0 else '-'}"

            if currUsers[usr][par]['pen'] == 0:
                if currUsers_multi_partitions[usr][par]['pen'] ==0:
                    out += "\t"
                else:
                    out += f"({currUsers_multi_partitions[usr][par]['pen']}*)\t"
                    multi_partitions = True
            else:
                if currUsers_multi_partitions[usr][par]['pen'] ==0:
                    out += f"({currUsers[usr][par]['pen']})\t"
                else:
                    out += f"({currUsers[usr][par]['pen']}*)\t"
                    multi_partitions = True

        out += f"{araUsers.get(usr, usr)[:16]:<16}\n"     #Cut user names to 17 characters, for style reasons
        out_multiline += out.expandtabs(9)         #Cut user names to 20 characters, for style reason

    if multi_partitions:
        out_multiline += "* job pending on multiple partitions\n"
    out_multiline += '\n\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/¯¯\_(ツ)_/\n\n'

    stdscr.addstr(out_multiline)
    return out_multiline

if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.resizeterm(100, 100)
    curses.noecho()
    curses.cbreak()

    if len(sys.argv) >1:
        sleep_s= int(sys.argv[1]) #quite hacky

        try:
            while True:
                report_usage()
                stdscr.addstr("press ctrl+c to leave this live mode")
                stdscr.refresh()
                time.sleep(sleep_s)
        except (KeyboardInterrupt):
            curses.echo()
            curses.nocbreak()
            curses.endwin()
    else:
        out = report_usage()
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        print(out)
