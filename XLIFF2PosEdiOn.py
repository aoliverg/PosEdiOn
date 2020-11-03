#    XLIFF2PosEdiOn
#    Copyright (C) 2020  Antoni Oliver
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

xliff_file=sys.argv[1]
text_file=sys.argv[2]

tree = ET.parse(xliff_file)
root = tree.getroot()

salida=codecs.open(text_file,"w",encoding="utf-8")
cont=0
for tu in root.iter('{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
    sl_segments=[]
    tl_segments=[]
    mids=[]
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
                    sl_segments.append(child.text)
                    mids.append(child.attrib['mid'])
        #target
        for para in tu.findall('{urn:oasis:names:tc:xliff:document:1.2}target'):
            for child in para.iter():
                if child.tag=="{urn:oasis:names:tc:xliff:document:1.2}mrk":
                    tl_segments.append(child.text)
    #not segmented
    else:
        #source
        for para in tu.findall('{urn:oasis:names:tc:xliff:document:1.2}source'):
            sl_segments.append(para.text)
        #target
        for para in tu.findall('{urn:oasis:names:tc:xliff:document:1.2}target'):
            tl_segments.append(para.text)
    
    for i in range(0,len(sl_segments)):
        
        try:
            cont+=1
            id=str(tu_id)+"-"+str(mids[i])
            cadena=str(cont)+"\t"+id+"\t"+sl_segments[i]+"\t"+tl_segments[i]
            salida.write(cadena+"\n")
        except:
            print("ERROR",cont,sys.exc_info())

