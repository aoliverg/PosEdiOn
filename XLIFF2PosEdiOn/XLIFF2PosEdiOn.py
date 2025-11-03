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
import argparse
import os
import sqlite3


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


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Program to convert XLIFFs to PosEdiOn files.')
    parser.add_argument('-i','--in', action="store", dest="inputfile", help='The input TMX file.',required=True)
    parser.add_argument('-o','--out', action="store", dest="project_name", help='The output TMX file.',required=True)

    args = parser.parse_args()

    xliff_file=args.inputfile
    project_name=args.project_name
    create_project(project_name,overwrite=True)
    convert(xliff_file,project_name)
