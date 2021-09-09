#    txt2PosEdiOn
#    Copyright (C) 2021  Antoni Oliver
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import codecs
import os
import sqlite3
import argparse

def create_project(project_name,overwrite=False):
    '''Opens a project. If the project already exists, it raises an exception. To avoid the exception use overwrite=True. To open existing projects, use the open_project method.'''
    if os.path.isfile(project_name) and not overwrite:
            raise Exception("This file already exists")
    
    else:
        if os.path.isfile(project_name) and overwrite:
            os.remove(project_name)
        conn=sqlite3.connect(project_name)
        cur = conn.cursor() 
        with conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE segments(segment_id INTEGER PRIMARY KEY, slsegment TEXT, rawMT TEXT, postED TEXT, status TEXT)")
            conn.commit()
            cur.execute("CREATE TABLE actions(id INTEGER PRIMARY KEY AUTOINCREMENT, tipus TEXT, segment_id INTEGER, datetime timestamp, key_pressed TEXT, position TEXT, len_posted INT, edit_mode TEXT)")
            conn.commit()
            
def insert_file(project_name,sourcefilename,rawMTfilename):
    file1=codecs.open(sourcefilename,"r",encoding="utf-8")
    if not rawMTfilename==None: file2=codecs.open(rawMTfilename,"r",encoding="utf-8")
    conn=sqlite3.connect(project_name)
    cur = conn.cursor()


    cont=1
    data=[]

    while 1:
        linia1=file1.readline()
        if not linia1:
            break
        linia1=linia1.rstrip().replace("\t"," ")
        if not rawMTfilename==None:
            linia2=file2.readline()
            linia2=linia2.rstrip().replace("\t"," ")
        else:
            linia2=""
        record=[]
        record.append(cont)
        record.append(linia1)
        record.append(linia2)
        data.append(record)
        cont+=1
        
    cur.executemany("INSERT INTO segments (segment_id, slsegment, rawMT) VALUES (?,?,?)",data)
    conn.commit()



parser = argparse.ArgumentParser(description='createPosEdiOnProject: a command-line program to create projects for PosEdiOn')
parser.add_argument('--source', dest='sourcefilename', help='The source language text file name.', action='store',required=True)
parser.add_argument('--rawMT', dest='rawMTfilename', help='The raw machine translated text file.', action='store',required=False)
parser.add_argument('--project', dest='project_name', help='The name of the project (sqlite3 file)', action='store',required=True)
args = parser.parse_args()

sourcefilename=args.sourcefilename
rawMTfilename=args.rawMTfilename
project_name=args.project_name

create_project(project_name,overwrite=True)
insert_file(project_name,sourcefilename,rawMTfilename)

