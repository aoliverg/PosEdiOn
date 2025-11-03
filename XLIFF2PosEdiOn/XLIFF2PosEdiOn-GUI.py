#    XLIFF2PosEdiOn-GUI
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

import xml.etree.ElementTree as ET
import sys
import codecs
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

def convert(xliff_file,project_name):
    
    conn=sqlite3.connect(project_name)
    cur = conn.cursor()
    
    tree = ET.parse(xliff_file)
    root = tree.getroot()
    cont=0
    sl_segments=[]
    tl_segments=[]
    mids=[]
    for tu in root.iter('{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
        childtags=[]
        tu_id=tu.attrib['id']
        for child in tu:
            childtags.append(child.tag)
        #segmented
        if "{urn:oasis:names:tc:xliff:document:1.2}seg-source" in childtags:
            #source
            for para in tu.findall('{urn:oasis:names:tc:xliff:document:1.2}seg-source'):
                for child in para.iter():
                    if child.tag=="{urn:oasis:names:tc:xliff:document:1.2}mrk":
                        sl_segments.append(child.text.rstrip())
                        mids.append(child.attrib['mid'])
            #target
            for para in tu.findall('{urn:oasis:names:tc:xliff:document:1.2}target'):
                for child in para.iter():
                    if child.tag=="{urn:oasis:names:tc:xliff:document:1.2}mrk":
                        tl_segments.append(child.text.rstrip())
        #not segmented
        else:
            #source
            mid=tu_id
            mids.append(mid)
            for para in tu.findall('{urn:oasis:names:tc:xliff:document:1.2}source'):
                sl_segments.append(para.text.rstrip())
                
            #target
            for para in tu.findall('{urn:oasis:names:tc:xliff:document:1.2}target'):
                tl_segments.append(para.text.rstrip())
                
    data=[]
    for i in range(0,len(sl_segments)):        
        try:
            cont+=1
            record=[]
            record.append(cont)
            record.append(sl_segments[i])
            record.append(tl_segments[i])
            data.append(record)
        except:
            print("ERROR",cont,sys.exc_info())
    cur.executemany("INSERT INTO segments (segment_id, slsegment, rawMT) VALUES (?,?,?)",data)
    conn.commit()          

def open_XLIFF():
    XLIFF_file = askopenfilename(initialdir = filepathin, filetypes = (("All files", "*"),("XLIFF files","*.xlf")))
    E1.delete(0,END)
    E1.insert(0,XLIFF_file)

def open_PosEdiOn():
    PosEdiOn_file = asksaveasfilename(initialdir = filepathin, filetypes = (("SQLite files","*.sqlite"),("All files", "*")))
    E2.insert(0,PosEdiOn_file)
            
def go():
    xliff_file=E1.get()
    PosEdiOn_file=E2.get()
    create_project(PosEdiOn_file,overwrite=True)
    convert(xliff_file,PosEdiOn_file)

filepathin=os.getcwd()

main_window = Tk()
main_window.title("XLIFF2PosEdiOn GUI")
main_window.clipboard_clear()



B1=Button(main_window, text = str("Select XLIFF file"), command=open_XLIFF,width=15)
B1.grid(row=0,column=0)
E1 = Entry(main_window,  width=50)
E1.grid(row=0,column=1)
B2=Button(main_window, text = str("Select PosEdiOn file"), command=open_PosEdiOn,width=15)
B2.grid(row=1,column=0)
E2 = Entry(main_window,  width=50)
E2.grid(row=1,column=1)
B3=Button(main_window, text = str("GO!"), command=go,width=15)
B3.grid(row=2,column=1,sticky="E")

main_window.mainloop()
