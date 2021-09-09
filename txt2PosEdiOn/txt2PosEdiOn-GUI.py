#    txt2PosEdiOn-GUI
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

import sys
import codecs
import argparse
import os
import sqlite3

from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askdirectory
from tkinter import messagebox





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
            

def open_source():
    source_file = askopenfilename(initialdir = filepathin, filetypes = (("All files", "*"),("text files","*.txt")))
    E1.delete(0,END)
    E1.insert(0,source_file)
    
def open_rawMT():
    rawMT_file = askopenfilename(initialdir = filepathin, filetypes = (("All files", "*"),("text files","*.txt")))
    E2.delete(0,END)
    E2.insert(0,rawMT_file)

def open_PosEdiOn():
    PosEdiOn_file = asksaveasfilename(initialdir = filepathin, filetypes = (("SQLite files","*.sqlite"),("All files", "*")))
    E3.delete(0,END)
    E3.insert(0,PosEdiOn_file)
    
def clear():
    E1.delete(0,END)
    E2.delete(0,END)
    E3.delete(0,END)
    
            
def go():
    sourcefilename=E1.get()
    rawMTfilename=E2.get()
    if rawMTfilename=="": rawMTfilename=None
    project_name=E3.get()
    create_project(project_name,overwrite=True)
    insert_file(project_name,sourcefilename,rawMTfilename)

filepathin=os.getcwd()

main_window = Tk()
main_window.title("txt2PosEdiOn GUI")
main_window.clipboard_clear()



B1=Button(main_window, text = str("Select source file"), command=open_source,width=15)
B1.grid(row=0,column=0)
E1 = Entry(main_window,  width=50)
E1.grid(row=0,column=1)

B2=Button(main_window, text = str("Select rawMT file"), command=open_rawMT,width=15)
B2.grid(row=1,column=0)
E2 = Entry(main_window,  width=50)
E2.grid(row=1,column=1)

B3=Button(main_window, text = str("Select PosEdiOn file"), command=open_PosEdiOn,width=15)
B3.grid(row=2,column=0)
E3 = Entry(main_window,  width=50)
E3.grid(row=2,column=1)
B4=Button(main_window, text = str("GO!"), command=go,width=15)
B4.grid(row=3,column=1,sticky="E")

B5=Button(main_window, text = str("Clear"), command=clear,width=15)
B5.grid(row=3,column=0,sticky="E")

main_window.mainloop()
