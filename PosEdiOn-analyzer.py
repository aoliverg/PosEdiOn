#    PosEdiOn-analyzer v 1.1
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

import argparse

import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import tkinter.scrolledtext as scrolledtext


import codecs
import datetime

from nltk.metrics import edit_distance
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.bleu_score import corpus_bleu

import statistics

import importlib

import numpy as np

import subprocess as sp
import os.path
import codecs

import subprocess

def showprint(a,b):
    global sortida_resultats
    if b=="":
        print(a)
        sortida_resultats.write(str(a)+"\n")
    else:
        print(a,b)
        sortida_resultats.write(str(a)+"\t"+str(b)+"\n")

def to_hms(seconds):
    h=int(seconds//3600)
    
    
    rsec=seconds-h*3600
    m=int(rsec//60)
    
    s=round((rsec-m*60),0)
    s=int(s)
    return(h,m,s)

    
def open_project_dir():
    folder_selected = filedialog.askdirectory(initialdir = config['Filepath']['path_in'])
    E1.delete(0,END)
    E1.insert(0,folder_selected)
    
    

def open_results_file():
    resultsfile = filedialog.asksaveasfilename(initialdir = filepathin, filetypes = (("All files", "*"),("txt files","*.txt")))
    E2.delete(0,END)
    E2.insert(0,resultsfile)
    return
    
def ter_segment(referencesTOK,hypothesisTOK):
    terlist=[]
    shyp=codecs.open("hyp.txt","w",encoding="utf-8")
    srefs=codecs.open("refs.txt","w",encoding="utf-8")
    cadena=hypothesisTOK+" (SEG-1)"
    shyp.write(cadena+"\n")
    cadena=referencesTOK+" (SEG-1)"
    srefs.write(cadena+"\n")
    shyp.close()
    srefs.close()

    p = subprocess.Popen("java -jar tercom-0.10.0.jar -r refs.txt -h hyp.txt -N -o sum -n hter", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    ter=None
      
    entradater=codecs.open("hter.sum","r",encoding="utf-8")
    for linia in entradater:
        linia=linia.strip()
        camps=linia.split("|")
        if camps[0].startswith("TOTAL"):
            ter=float(camps[-1].replace(",",".").strip())/100
            
    return(ter)


def ter_corpus(referencesTOK,hypothesisTOK):
    terdict={}
    shyp=codecs.open("hyp.txt","w",encoding="utf-8")
    srefs=codecs.open("refs.txt","w",encoding="utf-8")
    for segmentID in hypothesisTOK:
        mt=hypothesisTOK[segmentID]
        cadena=mt+" "+"(SEG-"+str(segmentID)+")"
        shyp.write(cadena+"\n")
        for reference in referencesTOK[segmentID]:
            pe=reference
            cadena=pe+" "+"(SEG-"+str(segmentID)+")"
            srefs.write(cadena+"\n")
    shyp.close()
    srefs.close()

    p = subprocess.Popen("java -jar tercom-0.10.0.jar -r refs.txt -h hyp.txt -N -o sum -n hter", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    ter=None
    terdict={}
    entradater=codecs.open("hter.sum","r",encoding="utf-8")
    for linia in entradater:
        linia=linia.strip()
        camps=linia.split("|")
        if len(camps)>5 and not camps[0].startswith("TOTAL"):
            
            try:
                segmentID=int(camps[0].strip().replace("SEG-","").split(":")[0])
                terparcial=float(camps[-1].replace(",",".").strip())/100
                terdict[segmentID]=terparcial
            except:
                pass
        if camps[0].startswith("TOTAL"):
            ter=float(camps[-1].replace(",",".").strip())/100
            
    return(ter,terdict)


  
def go():
    sortida_resultats=E2.get()
    havereferences=False
    projectdir=E1.get()
    if projectdir=="":
        messagebox.showerror("error", "The path to the project should be given.")
    outfile=E2.get()
    if outfile=="":
        messagebox.showerror("error", "A name of a output results file should be given.")

        
        
    yamlfullname=projectdir+"/"+"config.yaml"
    stream = open(yamlfullname, 'r')
    configproj=yaml.load(stream,Loader=yaml.FullLoader)
    filename_work=projectdir+"/"+configproj['Text']['file']
    filename_actions=projectdir+"/"+configproj['Actions']['file']
    sllang=configproj['Languages']['source']
    tllang=configproj['Languages']['target']
    
    sltokenizer = importlib.import_module("MTUOC_tokenizer_gen","tokenize")
    tltokenizer = importlib.import_module("MTUOC_tokenizer_gen","tokenize")
    try:
        sltokenizername="MTUOC_tokenizer_"+tllang
        sltokenizer = importlib.import_module(sltokenizername,"tokenize")
    except:
        pass

    try:
        tltokenizername="MTUOC_tokenizer_"+tllang
        ttlokenizer = importlib.import_module(tltokenizername,"tokenize")
    except:
        pass
        
    entrada_work=codecs.open(filename_work,"r",encoding="utf-8")
    entrada_actions=codecs.open(filename_actions,"r",encoding="utf-8")
    sortida_resultats=codecs.open(outfile,"w",encoding="utf-8")
        
    segmentSL={}
    segmentTLRaw={}
    segmentTLPostEd={}
    segmentConttoID={}
    for linia_w in entrada_work:
        linia_w=linia_w.rstrip()
        camps_w=linia_w.split("\t")
        contsegment=int(camps_w[0])
        idsegment=camps_w[1]
        segmentConttoID[contsegment]=idsegment
        segmentSL[contsegment]=camps_w[2]
        if len(camps_w)>=3:
            segmentTLRaw[contsegment]=camps_w[3]
        else:
            segmentTLRaw[contsegment]=""
        if len(camps_w)>=4:
            segmentTLPostEd[contsegment]=camps_w[4]
        else:
            segmentTLPostEd[contsegment]=""
    
    TIME={}
    for s in segmentSL.keys():
        TIME[s]=0
    
    KEYSTROKES={}
    for s in segmentSL.keys():
        KEYSTROKES[s]=0
    
    cont=0
    for linia_a in entrada_actions:
        cont+=1
        linia_a=linia_a.rstrip()
        camps=linia_a.split("\t")
        try:
            tipus=camps[0]
            segmentcont=int(camps[1])
            segmentID=camps[2]
            date_string=camps[3]
        
            if cont==1 or tipus=="IN" or tipus=="START" or tipus=="RESTART":
                timestart=datetime.datetime.strptime(date_string,'%Y-%m-%d %H:%M:%S.%f')
            elif tipus=="OUT" or tipus=="PAUSE" or tipus=="EXIT":
                timesend=datetime.datetime.strptime(date_string,'%Y-%m-%d %H:%M:%S.%f')
                seconds=(timesend-timestart).total_seconds()
                TIME[segmentcont]+=seconds
                
            elif tipus=="K": KEYSTROKES[segmentcont]+=1
        except:
            pass

    refTOK={}
    hypTOK={}
    refTOKpruned={}
    hypTOKpruned={}
    normdict={}
    timenorm={}
    Knorm={}
    #noves mesures
    
    TIME_NORM_CHARS={}
    TIME_NORM_TOKENS={}
    KEYSTROKES_NORM_CHARS={}
    KEYSTROKES_NORM_TOKENS={}
    
    for segmentID in segmentSL:
        if segmentID in segmentTLPostEd and segmentID in segmentTLRaw and segmentID in TIME and segmentID in KEYSTROKES:
            
            sTLRaw=segmentTLRaw[segmentID]
            sTLPost=segmentTLPostEd[segmentID]    
            ref=sTLPost
            hyp=sTLRaw
            
            reftok=tltokenizer.tokenize(ref).split(" ")
            refreftok=[]
            refreftok.append(reftok)
            
            hyptok=tltokenizer.tokenize(hyp).split(" ")
            numtokens=len(hyptok)
            numchars=len(hyp)
            
            TIME_NORM_CHARS[segmentID]=TIME[segmentID]/numchars
            TIME_NORM_TOKENS[segmentID]=TIME[segmentID]/numtokens
            
            KEYSTROKES_NORM_CHARS[segmentID]=KEYSTROKES[segmentID]/numchars
            KEYSTROKES_NORM_TOKENS[segmentID]=KEYSTROKES[segmentID]/numtokens
            
    mean_TIME_NORM_CHARS=statistics.mean(TIME_NORM_CHARS.values())
    stdv_TIME_NORM_CHARS=statistics.pstdev(TIME_NORM_CHARS.values())
    
    mean_TIME_NORM_TOKENS=statistics.mean(TIME_NORM_TOKENS.values())
    stdv_TIME_NORM_TOKENS=statistics.pstdev(TIME_NORM_TOKENS.values())
    
    mean_KEY_NORM_CHARS=statistics.mean(KEYSTROKES_NORM_CHARS.values())
    stdv_KEY_NORM_CHARS=statistics.pstdev(KEYSTROKES_NORM_CHARS.values())
    
    mean_KEY_NORM_TOKENS=statistics.mean(KEYSTROKES_NORM_TOKENS.values())
    stdv_KEY_NORM_TOKENS=statistics.pstdev(KEYSTROKES_NORM_TOKENS.values())
                
    prunetime=mean_TIME_NORM_CHARS+2*stdv_TIME_NORM_CHARS
    prunekey=mean_KEY_NORM_CHARS+2*stdv_KEY_NORM_CHARS
    HBLEU={}
    HED={}
    HTER={}
    pruned={}
    contsegment=0
    contsegmentpruned=0
    totaltime=0
    totaltimepruned=0
    totalkeys=0
    totalkeyspruned=0
    sumchars=0
    sumcharspruned=0
    sumhed=0
    sumhedpruned=0
    refsrefs=[]
    refsrefspruned=[]
    hypstoks=[]
    hypstokspruned=[]
    for segmentID in segmentSL:
        if segmentID in TIME_NORM_CHARS and segmentID in KEYSTROKES_NORM_CHARS and segmentID in segmentTLPostEd and segmentID in segmentTLRaw and segmentID in TIME and segmentID in KEYSTROKES:
        
            
            sTLRaw=segmentTLRaw[segmentID]
            sTLPost=segmentTLPostEd[segmentID]    
            ref=sTLPost
            hyp=sTLRaw
            
            reftok=tltokenizer.tokenize(ref).split(" ")
            refreftok=[]
            refreftok.append(reftok)
            
            hyptok=tltokenizer.tokenize(hyp).split(" ")
            numtokens=len(hyptok)
            numchars=len(hyp)
            
            hbleu=sentence_bleu(refreftok,hyptok)
            HBLEU[segmentID]=hbleu
            
            
            
            hed=edit_distance(ref,hyp)
            HEditDistance=100*(hed/numchars)
            HED[segmentID]=HEditDistance
            
            mt=" ".join(tltokenizer.tokenize(sTLRaw).split(" "))
            pe=" ".join(tltokenizer.tokenize(sTLPost).split(" "))
            
            if TIME_NORM_CHARS[segmentID]<=prunetime and KEYSTROKES_NORM_CHARS[segmentID]<=prunekey:
                contsegment+=1
                contsegmentpruned+=1
                totaltime+=TIME_NORM_CHARS[segmentID]
                totalkeys+=KEYSTROKES_NORM_CHARS[segmentID]
                totaltimepruned+=TIME_NORM_CHARS[segmentID]
                totalkeyspruned+=KEYSTROKES_NORM_CHARS[segmentID]
                sumchars+=numchars
                sumcharspruned+=numchars
                sumhed+=hed
                sumhedpruned+=hed
                refsrefs.append(refreftok)
                refsrefspruned.append(refreftok)
                hypstoks.append(hyptok)
                hypstokspruned.append(hyptok)
                pruned[segmentID]=False
                refTOK[segmentID]=[pe]
                hypTOK[segmentID]=mt
                refTOKpruned[segmentID]=[pe]
                hypTOKpruned[segmentID]=mt
            else:
                contsegment+=1
                sumchars+=numchars
                sumhed+=hed
                refsrefs.append(refreftok)
                hypstoks.append(hyptok)
                pruned[segmentID]=True
                refTOK[segmentID]=[pe]
                hypTOK[segmentID]=mt
                totaltime+=TIME_NORM_CHARS[segmentID]
                totalkeys+=KEYSTROKES_NORM_CHARS[segmentID]
                
            
    
            
            
            
    (TER,HTER)=ter_corpus(refTOK,hypTOK)
    (TERpruned,HTERpruned)=ter_corpus(refTOKpruned,hypTOKpruned)
    cadena="Count\tID\tPruned\tTime\tKeys\tHBLEU\tHEd\tHTER"
    sortida_resultats.write(cadena+"\n")
    cadena="\t\tPruned\tTime\tKeys\tHBLEU\tHEd\tHTER"
    results_frame_text.insert(INSERT, cadena)
    results_frame_text.insert(INSERT, "\n")
    for segmentID in HED:
        cadena=str(segmentID)+"\t"+str(segmentConttoID[segmentID])+"\t"+str(pruned[segmentID])+"\t"+str(round(TIME_NORM_CHARS[segmentID]*100,1))+"\t"+str(round(KEYSTROKES_NORM_CHARS[segmentID]*100,1))+"\t"+str(round(HBLEU[segmentID],round_hBLEU))+"\t"+str(round(HED[segmentID],round_hEd))+"\t"+str(round(HTER[segmentID],round_hTER))
        sortida_resultats.write(cadena+"\n")
    cadena="------------------------------------------------------------------------"
    sortida_resultats.write(cadena+"\n")
    hedtotal=100*sumhed/sumchars
    hedtotalpruned=100*sumhedpruned/sumcharspruned
    HBLEUTOTAL=corpus_bleu(refsrefs,hypstoks)
    HBLEUTOTALPRUNED=corpus_bleu(refsrefspruned,hypstokspruned)
    cadena="Total\t\tFalse\t"+str(round(totaltime*100/contsegment,1))+"\t"+str(round(totalkeys*100/contsegment,1))+"\t"+str(round(HBLEUTOTAL,round_hBLEU))+"\t"+str(round(hedtotal,round_hEd))+"\t"+str(round(TER,round_hTER))
    sortida_resultats.write(cadena+"\n")
    results_frame_text.insert(INSERT, cadena)
    results_frame_text.insert(INSERT, "\n")
    cadena="Total\t\tTrue\t"+str(round(totaltimepruned*100/contsegmentpruned,1))+"\t"+str(round(totalkeyspruned*100/contsegmentpruned,1))+"\t"+str(round(HBLEUTOTALPRUNED,round_hBLEU))+"\t"+str(round(hedtotalpruned,round_hEd))+"\t"+str(round(TERpruned,round_hTER))
    sortida_resultats.write(cadena+"\n")
    results_frame_text.insert(INSERT, cadena)
    results_frame_text.insert(INSERT, "\n")
if __name__ == "__main__":
    
    if not os.path.isfile("config-analyzer.yaml"):
        messagebox.showerror("ERROR:", "No config-analyzer.yaml file.")
        sys.exit()
    
    stream = open('config-analyzer.yaml', 'r',encoding="utf-8")
    config=yaml.load(stream,Loader=Loader)

    filepathin=config['Filepath']['path_in']
    filepathout=config['Filepath']['path_out']
   
    round_time=int(config['Measures']['round_time'])
    round_keys=int(config['Measures']['round_keys'])
    round_hTER=int(config['Measures']['round_hTER'])
    round_hBLEU=int(config['Measures']['round_hBLEU'])
    round_hEd=int(config['Measures']['round_hEd'])
    round_other=int(config['Measures']['round_other'])
    
    resultsfile=config['Files']['results']
   

    main_window = Tk()
    main_window.title("PosEdiOn Analyzer")

    notebook = ttk.Notebook(main_window)

    files_frame = Frame(notebook)
    B1=Button(files_frame, text = str("Open project dir"), command=open_project_dir,width=15)
    B1.grid(row=0,column=0)
    E1 = Entry(files_frame,  width=50)
    E1.grid(row=0,column=1)
    B2=Button(files_frame, text = str("Results file"), command=open_results_file,width=15)
    B2.grid(row=1,column=0)
    E2 = Entry(files_frame,  width=50)
    E2.grid(row=1,column=1)
    E2.delete(0,END)
    E2.insert(0,resultsfile)
    #B3=Button(files_frame, text = str("References file"), command=open_references_file,width=15)
    #B3.grid(row=2,column=0)
    #E3 = Entry(files_frame,  width=50)
    #E3.grid(row=2,column=1)

    B4=Button(files_frame, text = str("Analyze"), command=go,width=15)
    B4.grid(row=3,column=1)
    
    

    measures_frame = Frame(notebook)
    cbHTER = Checkbutton(measures_frame, text="HTER")
            
    results_frame = Frame(notebook)
    results_frame_text=scrolledtext.ScrolledText(results_frame,height=7)
    results_frame_text.grid(row=0,column=0)


    notebook.add(files_frame, text="Files", padding=30)
    notebook.add(results_frame, text="Results", padding=30)

    notebook.pack()
    notebook.pack_propagate(0) #Don't allow the widgets inside to determine the frame's width / height
    notebook.pack(fill=BOTH, expand=1)
    main_window.mainloop()

