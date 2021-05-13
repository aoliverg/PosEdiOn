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
            print(cadena)
            salida.write(cadena+"\n")
        except:
            print("ERROR",cont,sys.exc_info())


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Program to convert XLIFFs to PosEdiOn files.')
    parser.add_argument('-i','--in', action="store", dest="inputfile", help='The input TMX file.',required=True)
    parser.add_argument('-o','--out', action="store", dest="outputfile", help='The output TMX file.',required=True)

    args = parser.parse_args()

    xliff_file=args.inputfile
    text_file=args.outputfile
    convert(xliff_file,text_file)
