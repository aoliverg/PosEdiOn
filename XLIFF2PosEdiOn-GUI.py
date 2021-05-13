#    XLIFF2PosEdiOn
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

from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askdirectory
from tkinter import messagebox




def convert(xliff_file,text_file):
    
    tree = ET.parse(xliff_file)
    root = tree.getroot()

    salida=codecs.open(text_file,"w",encoding="utf-8")
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
                

    for i in range(0,len(sl_segments)):        
        try:
            cont+=1
            id=str(tu_id)+"-"+str(mids[i])
            cadena=str(cont)+"\t"+id+"\t"+sl_segments[i]+"\t"+tl_segments[i]
            salida.write(cadena+"\n")
        except:
            print("ERROR",cont,sys.exc_info())
            

def open_XLIFF():
    XLIFF_file = askopenfilename(initialdir = filepathin, filetypes = (("All files", "*"),("XLIFF files","*.xlf")))
    E1.delete(0,END)
    E1.insert(0,XLIFF_file)

def open_PosEdiOn():
    PosEdiOn_file = asksaveasfilename(initialdir = filepathin, filetypes = (("All files", "*"),("text files","*.txt")))
    E2.insert(0,PosEdiOn_file)
            
def go():
    xliff_file=E1.get()
    PosEdiOn_file=E2.get()
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
