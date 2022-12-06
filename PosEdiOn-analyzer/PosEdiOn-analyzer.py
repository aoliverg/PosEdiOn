#    PosEdiOn-analyzer v 2.0
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
from nltk.translate.nist_score import corpus_nist
from nltk.translate.nist_score import sentence_nist

import numpy

import statistics

import importlib

import numpy as np

import subprocess as sp
import os.path
import codecs

import subprocess
import sqlite3
import sys

import xlsxwriter
import difflib

def completeid(nid):
    nid=str(nid)
    if len(nid)==1: nid="000000"+nid
    elif len(nid)==2: nid="00000"+nid
    elif len(nid)==3: nid="0000"+nid
    elif len(nid)==4: nid="000"+nid
    elif len(nid)==5: nid="00"+nid
    elif len(nid)==6: nid="0"+nid
    return(nid)

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

    
def open_project_file():
    project_file = filedialog.askopenfilename(initialdir = filepathin)
    E1.delete(0,END)
    E1.insert(0,project_file)
    
    

def open_results_file():
    resultsfile = filedialog.asksaveasfilename(initialdir = filepathin, filetypes = (("All files", "*"),("MS Excel files","*.xlsx"),("txt files","*.txt")))
    E2.delete(0,END)
    E2.insert(0,resultsfile)
    return
    
def differences(a,b):
    d = difflib.Differ()
    diff = d.compare(a, b)
    cont=0
    result=[]
    for d in diff:
        d.strip()
        accio=d[0]
        lletra=d[-1]
        if accio=="":
            cadena=lletra
            result.append(cadena)
        elif accio=="+":
            cadena=lletra+"\u0332"
            result.append(cadena)
        elif accio=="-":
            cadena=lletra+"\u0336"
            result.append(cadena)
        else:
            result.append(lletra)
    amod="".join(result)
    return(amod)

def differencesExcel(a,b,blue,red,bold):
    
    d = difflib.Differ()
    diff = d.compare(a, b)
    cont=0
    string_parts=[]
    for d in diff:
        d.strip()
        accio=d[0]
        lletra=d[-1]
        if accio=="":
            string_parts.append(lletra)
        elif accio=="+":
            string_parts.append(blue)
            string_parts.append(lletra)
            
        elif accio=="-":
            string_parts.append(red)
            string_parts.append(lletra)
            
        else:
            string_parts.append(lletra)
    
    return(string_parts)

def ter_corpus(referencesTOK,hypothesisTOK):
    terlist=[]
    shyp=codecs.open("hyp.txt","w",encoding="utf-8")
    srefs=codecs.open("refs.txt","w",encoding="utf-8")
    for posicio in range(0,len(hypothesisTOK)):
        #mt=hypothesisTOK[posicio]
        mt=" ".join(hypothesisTOK[posicio])
        cadena=mt+" "+"(SEG-"+str(posicio)+")"
        shyp.write(cadena+"\n")
        for reference in referencesTOK[posicio]:
            #pe=reference
            pe=" ".join(reference)
            cadena=pe+" "+"(SEG-"+str(posicio)+")"
            srefs.write(cadena+"\n")
    shyp.close()
    srefs.close()
    p = subprocess.Popen("java -jar tercom-0.10.0.jar -r refs.txt -h hyp.txt -o txt -N -o sum -n hter", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    ter=None
    results={}
    entradater=codecs.open("hter.sum","r",encoding="utf-8")
    for linia in entradater:
        linia=linia.strip()
        camps=linia.split("|")
        camps = [s.strip() for s in camps]
        
        if camps[0].startswith("SEG") or camps[0].startswith("TOTAL"):
            result={}
            if camps[0].startswith("SEG"):
                numseg=int(camps[0].split(":")[0].replace("SEG-",""))+1
            elif camps[0].startswith("TOTAL"):
                numseg="TOTAL"
            result["Ins"]=float(camps[1].replace(",","."))
            result["Del"]=float(camps[2].replace(",","."))
            result["Sub"]=float(camps[3].replace(",","."))
            result["Shft"]=float(camps[4].replace(",","."))
            result["WdSh"]=float(camps[5].replace(",","."))
            result["NumErr"]=float(camps[6].replace(",","."))
            result["NumWd"]=float(camps[7].replace(",","."))
            result["TER"]=float(camps[8].replace(",","."))/100
            results[numseg]=result
        if camps[0].startswith("TOTAL"):
            ter=float(camps[8].replace(",","."))/100           
    return(results)

def ter_corpus_old(referencesTOK,hypothesisTOK):
    terlist=[]
    shyp=codecs.open("hyp.txt","w",encoding="utf-8")
    srefs=codecs.open("refs.txt","w",encoding="utf-8")
    for posicio in range(0,len(hypothesisTOK)):
        mt=" ".join(hypothesisTOK[posicio])
        cadena=mt+" "+"(SEG-"+str(posicio)+")"
        shyp.write(cadena+"\n")
        for reference in referencesTOK[posicio]:
            pe=" ".join(reference)
            cadena=pe+" "+"(SEG-"+str(posicio)+")"
            srefs.write(cadena+"\n")
    shyp.close()
    srefs.close()

    p = subprocess.Popen("java -jar tercom-0.10.0.jar -r refs.txt -h hyp.txt -o txt -N -o sum -n hter", stdout=subprocess.PIPE, shell=True)
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

def wer_score(ref, hyp):
    """ 
    code from: https://github.com/gcunhase/NLPMetrics
    Calculation of WER with Levenshtein distance.
    Time/space complexity: O(nm)
    Source: https://martin-thoma.com/word-error-rate-calculation/
    :param ref: reference text (separated into words)
    :param hyp: hypotheses text (separated into words)
    :return: WER score
    Modified to return the value divide by the number of words of the reference
    $ WER = \frac{S+D+I}{N} = \frac{S+D+I}{S+D+C} $
    S: number of substitutions, D: number of deletions, I: number of insertions, C: number of the corrects, N: number of words in the reference ($N=S+D+C$)
    """

    # Initialization
    d = numpy.zeros([len(ref) + 1, len(hyp) + 1], dtype=numpy.uint8)
    for i in range(len(ref) + 1):
        for j in range(len(hyp) + 1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i


    # Computation
    for i in range(1, len(ref) + 1):
        for j in range(1, len(hyp) + 1):
            if ref[i - 1] == hyp[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                substitution = d[i - 1][j - 1] + 1
                insertion = d[i][j - 1] + 1
                deletion = d[i - 1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)

    return d[len(ref)][len(hyp)]/len(ref)
    
def wer_corpus(references,hypothesis):
    cont=0
    weracu=0
    for posicio in range(0,len(hypothesis)):
        werpos=[]
        cont+=1
        for reference in references[posicio]:
            
            wer=wer_score(reference,hypothesis[posicio])
            werpos.append(wer)
        wer=min(werpos)
        weracu+=wer
    wer=weracu/cont
    return(wer)
  
def go():
    global timeprunelowerlimit
    global timepruneupperlimit
    global meantime
    global stdevtime
    selectedtokenizer=combo_tokenizers.get()
    if not selectedtokenizer.endswith(".py"): selectedtokenizer=selectedtokenizer+".py"
    spec = importlib.util.spec_from_file_location('', selectedtokenizer)
    tokenizermod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tokenizermod)
    tokenizer=tokenizermod.Tokenizer()
    
    data={}
    projecfile=E1.get()
    if projecfile=="":
        messagebox.showerror("error", "A project file should be given.")
    outfile=E2.get()
    if outfile=="":
        messagebox.showerror("error", "A name of a output results file should be given.")
    conn=sqlite3.connect(projecfile)
    cur = conn.cursor() 
    cur.execute('SELECT segment_id, slsegment, rawMT, postEd, status FROM segments')
    results=cur.fetchall()
    for result in results:
        ident=int(completeid(result[0]))
        source=result[1]
        rawMT=result[2]
        postEd=result[3]
        if postEd==None: postEd=rawMT
        status=result[4]
        data[ident]={}
        source=source.strip()
        rawMT=rawMT.strip()
        postEd=postEd.strip()
        
        data[ident]["source"]=source
        rawMT_tok=tokenizer.tokenize(rawMT).split(" ") 
        data[ident]["rawMT"]=rawMT
        data[ident]["rawMT_tok"]=rawMT_tok
        data[ident]["postED"]=postEd
        postEd_tok=tokenizer.tokenize(postEd).split(" ") 
        data[ident]["postED_tok"]=postEd_tok
        
        if not "TIME" in data[ident]: data[ident]["TIME"]=0
        if not "KEYSTROKES" in data[ident]: data[ident]["KEYSTROKES"]=0
        if not "MOUSEACTIONS" in data[ident]: data[ident]["MOUSEACTIONS"]=0
        if not "TIME_NORM" in data[ident]: data[ident]["TIME_NORM"]=0
        if not "KEYSTROKES_NORM" in data[ident]: data[ident]["KEYSTROKES_NORM"]=0
        if not "MOUSEACTIONS_NORM" in data[ident]: data[ident]["MOUSEACTIONS_NORM"]=0
        if not "INSERTIONS" in data[ident]: data[ident]["INSERTIONS"]=0
        if not "SUBSTITUTIONS" in data[ident]: data[ident]["SUBSTITUTIONS"]=0
        if not "DELETIONS" in data[ident]: data[ident]["DELETIONS"]=0
        if not "REORDERING" in data[ident]: data[ident]["REORDERING"]=0
        #if not "" in data[ident]: data[ident][""]=0
        #if not "INITIAL_PAUSE" in data[ident]: data[ident]["INITIAL_PAUSE"]=0
        #if not "FINAL_PAUSE" in data[ident]: data[ident]["FINAL_PAUSE"]=0
        if not "LONG_PAUSES" in data[ident]: data[ident]["LONG_PAUSES"]=sum_additional_pause
    
    cur.execute('SELECT * FROM actions')
    results=cur.fetchall()
    cont=0
    lenprev=0
    controlX=False
    controlV=False
    prevident=""
    date_string=results[0][3]
    prev_time=datetime.datetime.strptime(date_string,'%Y-%m-%d %H:%M:%S.%f')
    for result in results:
        cont+=1
        action_id=result[0]
        tipus=result[1]
        ident=int(completeid(result[2]))
        date_string=result[3]
        key_pressed=result[4]
        position=result[5]
        len_posted=result[6]
        edit_mode=result[7]
        chars=len(data[ident]["rawMT"])
        tokens=len(data[ident]["rawMT_tok"])
        normfactor=1
        if normalization=="char": normfactor=chars
        elif normalization=="token":  normfactor=tokens
        
        if cont==1 or tipus=="IN" or tipus=="START" or tipus=="RESTART":
            timestart=datetime.datetime.strptime(date_string,'%Y-%m-%d %H:%M:%S.%f')
            lenprev=len_posted
            controlX=False
            controlV=False
            prevident=ident
        elif tipus=="OUT" or tipus=="PAUSE" or tipus=="EXIT":
            controlX=False
            controlV=False
            timesend=datetime.datetime.strptime(date_string,'%Y-%m-%d %H:%M:%S.%f')
            seconds=(timesend-timestart).total_seconds()
            if ident==prevident:
                data[ident]["TIME"]+=seconds
                data[ident]["TIME_NORM"]+=seconds/normfactor
                #if normalization=="char": data[ident]["TIME_NORM"]+=seconds/chars
                #elif normalization=="token":  data[ident]["TIME_NORM"]+=seconds/tokens
                #elif normalization=="segment":  data[ident]["TIME_NORM"]+=seconds
        elif tipus=="K": 
            data[ident]["KEYSTROKES"]+=1
            now_time=datetime.datetime.strptime(date_string,'%Y-%m-%d %H:%M:%S.%f')
            pause=(now_time-prev_time).total_seconds()
            prev_time=now_time
            if pause>=min_pause_msec:
                data[ident]["LONG_PAUSES"]+=1
            #if normalization=="char": data[ident]["KEYSTROKES_NORM"]+=1/chars
            #elif normalization=="token":  data[ident]["KEYSTROKES_NORM"]+=1/tokens
            #elif normalization=="segment":  data[ident]["KEYSTROKES_NORM"]+=1
            if edit_mode=="Insert":
                if key_pressed.startswith("Key.letter") or key_pressed.startswith("Key.number") or key_pressed.startswith("Key.space") or key_pressed.startswith("Key.punctuation") or key_pressed.startswith("Key.mathematical") or key_pressed.startswith("Key.symbol"):
                    data[ident]["INSERTIONS"]+=1
            elif edit_mode=="Overwrite":
                if key_pressed.startswith("Key.letter") or key_pressed.startswith("Key.number") or key_pressed.startswith("Key.space") or key_pressed.startswith("Key.punctuation") or key_pressed.startswith("Key.mathematical") or key_pressed.startswith("Key.symbol"):
                    try:
                        if len_posted>len_prev:
                            data[ident]["INSERTIONS"]+=1
                        elif len_posted==len_prev:
                            data[ident]["SUBSTITUTIONS"]+=1
                    except:
                        pass
            if key_pressed in ["Key.46.Delete","Key.8.Backspace"]:
                data[ident]["DELETIONS"]+=1
        elif tipus=="M": 
            data[ident]["MOUSEACTIONS"]+=1
            now_time=datetime.datetime.strptime(date_string,'%Y-%m-%d %H:%M:%S.%f')
            pause=(now_time-prev_time).total_seconds()
            prev_time=now_time
            if pause>=min_pause_msec:
                data[ident]["LONG_PAUSES"]+=1
        elif tipus=="C":
            now_time=datetime.datetime.strptime(date_string,'%Y-%m-%d %H:%M:%S.%f')
            pause=(now_time-prev_time).total_seconds()
            prev_time=now_time
            if pause>=min_pause_msec:
                data[ident]["LONG_PAUSES"]+=1
            if key_pressed.startswith("Command.CtrlX"):
                controlX=True
            if key_pressed.startswith("Command.CtrlV") and controlX:
                data[ident]["REORDERING"]+=1
                controlX=True            
        len_prev=len_posted        
    timelist=[]

    for ident in data.keys():
        timelist.append(data[ident]["TIME_NORM"])        
    meantime=statistics.mean(timelist)
    stdevtime=statistics.stdev(timelist)    
    timepruneupperlimit=meantime+2*stdevtime
    timeprunelowerlimit=meantime-2*stdevtime  
    calculate_all(data)

def safediv(x,y):
    try:
        return x/y
    except ZeroDivisionError:
        return None      
    
def calculate_all(data):
    global timeprunelowerlimit
    global timepruneupperlimit
    global meantime
    global stdevtime
     
    cont=0
    equals=0
    toktotal=0
    chartotal=0
    toktotal_pruned=0
    chartotal_pruned=0
    tokequal=0
    timetotal=0
    keystrokestotal=0
    mouseactionstotal=0
    keystrokestotal_pruned=0
    mouseactionstotal_pruned=0
    insertionstotal=0
    insertionstotal_pruned=0
    deletionstotal=0
    deletionstotal_pruned=0
    substitutionstotal=0
    substitutionstotal_pruned=0
    reorderingtotal=0
    reorderingtotal_pruned=0

    #calculate ALL
    controlrepeated={}
    references=[]
    references_tok=[]
    hypothesis=[]
    hypothesis_tok=[]
    
    ident=sorted(list(data.keys()))
    references=[]
    references_tok=[]
    hypothesis=[]
    hypothesis_tok=[]
    references_pruned=[]
    references_tok_pruned=[]
    hypothesis_pruned=[]
    hypothesis_tok_pruned=[]
    total_long_pauses=0
    total_long_pauses_pruned=0
    for i in ident:
        cont+=1
        source=data[i]["source"]
        rawMT=data[i]["rawMT"]
        rawMT_tok=data[i]["rawMT_tok"]
        toktotal+=len(rawMT_tok)
        chartotal+=len(rawMT)
        postED=data[i]["postED"]
        postED_tok=data[i]["postED_tok"]
        hypothesis.append(rawMT)
        hypothesis_tok.append(rawMT_tok)
        references.append([postED])
        references_tok.append([postED_tok])
        total_long_pauses+=data[i]["LONG_PAUSES"]
        if data[i]["TIME_NORM"]>=timeprunelowerlimit and data[i]["TIME_NORM"]<=timepruneupperlimit:
            data[i]["PRUNED"]=False
            hypothesis_pruned.append(rawMT)
            hypothesis_tok_pruned.append(rawMT_tok)
            references_pruned.append([postED])
            references_tok_pruned.append([postED_tok])
            toktotal_pruned+=len(rawMT_tok)
            chartotal_pruned+=len(rawMT)
            keystrokestotal_pruned+=data[i]["KEYSTROKES"]
            mouseactionstotal_pruned+=data[i]["MOUSEACTIONS"]
            insertionstotal_pruned+=data[i]["INSERTIONS"]
            deletionstotal_pruned+=data[i]["DELETIONS"]
            substitutionstotal_pruned+=data[i]["SUBSTITUTIONS"]
            reorderingtotal_pruned+=data[i]["REORDERING"]
            total_long_pauses_pruned+=data[i]["LONG_PAUSES"]
        else:
            data[i]["PRUNED"]=True
    
        
        timetotal+=data[i]["TIME"]
        keystrokestotal+=data[i]["KEYSTROKES"]
        mouseactionstotal+=data[i]["MOUSEACTIONS"]
        insertionstotal+=data[i]["INSERTIONS"]
        deletionstotal+=data[i]["DELETIONS"]
        substitutionstotal+=data[i]["SUBSTITUTIONS"]
        reorderingtotal+=data[i]["REORDERING"]
        
        
         
        if rawMT==postED: 
            equals+=1
            tokequal+=len(rawMT_tok)
        if Detailed_results_BLEU:
            try:
                BLEU_sentence=round(sentence_bleu([postED_tok],rawMT_tok),round_BLEU)
                data[i]["BLEU"]=BLEU_sentence
            except:
                data[i]["BLEU"]=None
        
        if Detailed_results_NIST:    
            try:
                NIST_sentence=round(sentence_nist([postED_tok],rawMT_tok),round_NIST)
                data[i]["NIST"]=NIST_sentence
            except:
                data[i]["NIST"]=None

        
        if Detailed_results_WER:
            try:
                WER_sentence=round(wer_score(postED_tok,rawMT_tok),round_WER)
                data[i]["WER"]=WER_sentence 
            except:
                data[i]["WER"]=None    
        
        if Detailed_results_Ed:
            try:
                ed_sentence=edit_distance(" ".join(postED_tok)," ".join(rawMT_tok))
                ed_sentence=100*ed_sentence/len(" ".join(rawMT_tok))
                ed_sentence=round(ed_sentence,round_Ed)
                data[i]["EditDistance"]=ed_sentence
            except:
                data[i]["EditDistance"]=None
        
        if Detailed_results_KSR:
            try:
                data[i]["KSR"]=round((data[i]["KEYSTROKES"]/len(rawMT)),round_KSR)
            except:
                print("ERROR KSR ",sys.exc_info())
                data[i]["KSR"]=None
        
        if Detailed_results_MAR:
            try:
                data[i]["MAR"]=round(data[i]["MOUSEACTIONS"]/len(rawMT),round_MAR)
            except:
                print("ERROR MAR ",sys.exc_info())
                data[i]["MAR"]=None
        
        if Detailed_results_KSRM:
            try:
                data[i]["KSRM"]=round(data[i]["KSR"]+data[i]["MAR"],round_KSRM)
            except:
                print("ERROR KSRM ",sys.exc_info())
                data[i]["KSRM"]=None
    
    if SHOW_HTER or SHOW_HTER_details:
        TERDICT=ter_corpus(references_tok,hypothesis_tok)
        for i in ident:
            i2=int(i)
            data[i]["Ins"]=round(TERDICT[i2]["Ins"],round_TER)
            data[i]["Del"]=round(TERDICT[i2]["Del"],round_TER)
            data[i]["Sub"]=round(TERDICT[i2]["Sub"],round_TER)
            data[i]["Shft"]=round(TERDICT[i2]["Shft"],round_TER)
            data[i]["WdSh"]=round(TERDICT[i2]["WdSh"],round_TER)
            data[i]["NumErr"]=round(TERDICT[i2]["NumErr"],round_TER)
            data[i]["NumWd"]=round(TERDICT[i2]["NumWd"],round_TER)
            data[i]["TER"]=round(TERDICT[i2]["TER"],round_TER)
        
        TER=round(TERDICT["TOTAL"]["TER"],round_TER)
        INS=round(TERDICT["TOTAL"]["Ins"],round_TER)
        DEL=round(TERDICT["TOTAL"]["Del"],round_TER)
        SUB=round(TERDICT["TOTAL"]["Sub"],round_TER)
        SHFT=round(TERDICT["TOTAL"]["Shft"],round_TER)
        WDSH=round(TERDICT["TOTAL"]["WdSh"],round_TER)
        NUMERR=round(TERDICT["TOTAL"]["NumErr"],round_TER)
        NUMWD=round(TERDICT["TOTAL"]["NumWd"],round_TER)
    
    #GLOBAL RESULTS
    results_frame_text.delete('1.0', END)
    totalsegments=len(hypothesis_tok)
    
    try:
        percentequalsegment=round(100*equals/cont,round_other)
    except:
        percentequalsegment=None
    
    try:
        percentequaltokens=round(100*tokequal/toktotal,round_other)
    except:
        percentequaltokes=None
    
       
    normfactor=1
    if normalization=="char": 
        normalizationstring="per char"
        normfactor=chartotal
    elif normalization=="token": 
        normalizationstring="per token"
        normfactor=toktotal
    elif normalization=="segment": 
        normalizationstring="per segment"
        normfactor=totalsegments
    ntimetotal=timetotal/normfactor
    td=str(datetime.timedelta(seconds=timetotal))
    tdl=td.split(":")
    timetotal=":".join(tdl[:-1])+":"+str(int(round(float(tdl[-1]),0)))
    ntimetotal=round(ntimetotal,round_time)
    
    
    nkeystrokestotal=safediv(keystrokestotal,normfactor)
    nmouseactionstotal=safediv(mouseactionstotal,normfactor)
    
    
    
    nkeystrokestotal=round(nkeystrokestotal,round_keys)
    nmouseactionstotal=round(nmouseactionstotal,round_mouse)
    if SHOW_KSR:
        try:
            KSR=round((keystrokestotal/chartotal),round_KSR)
        except:
            print("ERROR KSR ",sys.exc_info())
            KSR=None
    if SHOW_MAR:
        try:
            MAR=round(mouseactionstotal/len(rawMT),round_MAR)
        except:
            print("ERROR MAR ",sys.exc_info())
            MAR=None
    if SHOW_KSRM:
        try:
            KSRM=round(KSR+MAR,round_KSRM)
        except:
            print("ERROR KSRM ",sys.exc_info())
            KSRM=None
    if SHOW_HBLEU:    
        try:
            BLEU=corpus_bleu(references_tok,hypothesis_tok)
            BLEU=round(BLEU,round_BLEU)
        except:
            print("ERROR BLEU ",sys.exc_info())
            BLEU=None
    if SHOW_HNIST:
        try:
            NIST=corpus_nist(references_tok,hypothesis_tok)
            NIST=round(NIST,round_NIST)
        except:
            print("ERROR NIST ",sys.exc_info())
            NIST=None
    if SHOW_HWER:
        try:
            WER=wer_corpus(references_tok,hypothesis_tok)
            WER=round(WER,round_WER)
        except:
            print("ERROR WER ",sys.exc_info())
            WER=None
    if SHOW_HEd:
        try:
            edtotal=0
            for i in range(0,len(hypothesis)):
                editmin=100000000
                for h in references[i]:
                    ed=edit_distance(hypothesis[i],h)
                    if ed<editmin:
                        editmin=ed
                edtotal+=editmin
            
            EditDistance=100*(edtotal/chartotal)        
            EditDistance=round(EditDistance,round_Ed)  
        except:
            print("ERROR EditDistance ",sys.exc_info())
            EditDistance=None
    
    if Calculate_pruned:
    #PRUNED GLOBAL VALUES
        if SHOW_KSR:
            try:
                KSR_pruned=keystrokestotal_pruned/chartotal
                KSR_pruned=round(KSR_pruned,round_KSR)
            except:
                KSR_pruned=None
        if SHOW_MAR:
            try:
                MAR_pruned=mouseactionstotal_pruned/len(rawMT)
                MAR_pruned=round(MAR_pruned,round_MAR)
            except:
                MAR_pruned=None
        if SHOW_KSRM:
            try:
                KSRM_pruned=KSR_pruned+MAR_pruned
                KSRM_pruned=round(KSRM_pruned,round_KSRM)
            except:
                KSRM_pruned=None
        if SHOW_HBLEU:
            try:
                BLEU_pruned=corpus_bleu(references_tok_pruned,hypothesis_tok_pruned)
                BLEU_pruned=round(BLEU_pruned,round_BLEU)
            except:
                BLEU_pruned=None
        if SHOW_HNIST:
            try:
                NIST_pruned=corpus_nist(references_tok_pruned,hypothesis_tok_pruned)
                NIST_pruned=round(NIST_pruned,round_NIST)
            except:
                NIST_pruned=None
        if SHOW_HTER or SHOW_HTER_details:
            try:
                TERDICT_PRUNED=ter_corpus(references_tok_pruned,hypothesis_tok_pruned)
                TER_pruned=round(TERDICT_PRUNED["TOTAL"]["TER"],round_TER)
                INS_pruned=round(TERDICT_PRUNED["TOTAL"]["Ins"],round_TER)
                DEL_pruned=round(TERDICT_PRUNED["TOTAL"]["Del"],round_TER)
                SUB_pruned=round(TERDICT_PRUNED["TOTAL"]["Sub"],round_TER)
                SHFT_pruned=round(TERDICT_PRUNED["TOTAL"]["Shft"],round_TER)
                WDSH_pruned=round(TERDICT_PRUNED["TOTAL"]["WdSh"],round_TER)
                NUMERR_pruned=round(TERDICT_PRUNED["TOTAL"]["NumErr"],round_TER)
                NUMWD_pruned=round(TERDICT_PRUNED["TOTAL"]["NumWd"],round_TER)
            except:
                TER_pruned=None
                INS_pruned=None
                DEL_pruned=None
                SUB_pruned=None
                SHFT_pruned=None
                WDSH_pruned=None
                NUMERR_pruned=None
                NUMWD_pruned=None
        if SHOW_HWER:
            try:
                WER_pruned=wer_corpus(references_tok_pruned,hypothesis_tok_pruned)
                WER_pruned=round(WER_pruned,round_WER)
            except:
                WER_pruned=None
        if SHOW_HEd:
            try:
                edtotal=0
                chartotal=0
                for i in range(0,len(hypothesis)):
                    editmin=100000000
                    chartotal+=len(hypothesis[i])
                    for h in references[i]:
                        ed=edit_distance(hypothesis[i],h)
                        if ed<editmin:
                            editmin=ed
                    edtotal+=editmin
                
                EditDistance_pruned=100*(edtotal/chartotal)
                
                EditDistance_pruned=round(EditDistance_pruned,round_Ed)  
            except:
                EditDistance_pruned=None

    #RESULTS TAB
    
    cadena="TOTAL EVALUATED SEGMENT PAIRS: "+str(totalsegments)+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="EQUAL SEGMENTS: "+str(equals)+" OF "+str(totalsegments)+" SEGMENTS - "+str(percentequalsegment)+" %"+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="EQUAL TOKENS: "+str(tokequal)+" OF "+str(toktotal)+" - "+str(percentequaltokens)+" %"+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="TOTAL TIME: "+str(timetotal)+" NORM TIME: "+str(ntimetotal)+" "+normalizationstring+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="TOTAL KEYSTROKES: "+str(keystrokestotal)+" NORM KEYSTROKES: "+str(nkeystrokestotal)+" "+normalizationstring+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="TOTAL MOUSE ACTIONS: "+str(mouseactionstotal)+" NORM MOUSE ACTIONS: "+str(nmouseactionstotal)+" "+normalizationstring+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    if SHOW_LONG_PAUSES:
        ntotal_long_pauses=safediv(total_long_pauses,normfactor)
        cadena="TOTAL LONG PAUSES: "+str(total_long_pauses)+" NORM LONG PAUSES: "+str(round(ntotal_long_pauses,round_other))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
    
    if SHOW_INSERTIONS:
        cadena="TOTAL INSERTIONS: "+str(insertionstotal)+" NORM INSERTIONS: "+str(round(safediv(insertionstotal,normfactor),round_other))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
    if SHOW_DELETIONS:
        cadena="TOTAL DELETIONS: "+str(deletionstotal)+" NORM DELETIONS: "+str(round(safediv(deletionstotal,normfactor),round_other))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
    if SHOW_SUBSTITUTIONS:
        cadena="TOTAL SUBSTITUTIONS: "+str(substitutionstotal)+" NORM SUBSTITUTIONS: "+str(round(safediv(substitutionstotal,normfactor),round_other))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
    if SHOW_REORDERING:
        cadena="TOTAL REORDERING: "+str(reorderingtotal)+" NORM REORDERING: "+str(round(safediv(reorderingtotal,normfactor),round_other))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
    if SHOW_KSR:
        cadena="KSR: "+str(KSR)+"\n"
        results_frame_text.insert(INSERT, cadena)
    if SHOW_MAR:
        cadena="MAR: "+str(MAR)+"\n"
        results_frame_text.insert(INSERT, cadena)
    if SHOW_KSR:
        cadena="KSRM: "+str(KSRM)+"\n"
        results_frame_text.insert(INSERT, cadena)
    if SHOW_HBLEU:
        cadena="BLEU: "+str(BLEU)+"\n"
        results_frame_text.insert(INSERT, cadena)
    if SHOW_HNIST:
        cadena="NIST: "+str(NIST)+"\n"
        results_frame_text.insert(INSERT, cadena)
    if SHOW_HTER:
        cadena="TER: "+str(TER)+"\n"
        results_frame_text.insert(INSERT, cadena)
    if SHOW_HWER:
        cadena="WER: "+str(WER)+"\n"
        results_frame_text.insert(INSERT, cadena)
    if SHOW_HTER_details:
        cadena="Ins: "+str(INS)+" NORM Ins: "+str(round(safediv(INS,normfactor),round_other))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
        
        cadena="Del: "+str(DEL)+" NORM Del: "+str(round(safediv(DEL,normfactor),round_other))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
        
        cadena="Sub: "+str(SUB)+" NORM Sub: "+str(round(safediv(SUB,normfactor),round_other))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
        
        cadena="Shft: "+str(SHFT)+" NORM Shft: "+str(round(safediv(SHFT,normfactor),round_other))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
        
        cadena="WdSh: "+str(WDSH)+" NORM WdSh: "+str(round(safediv(WDSH,normfactor),round_other))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
        
        cadena="NumErr: "+str(NUMERR)+" NORM NumErr: "+str(round(safediv(NUMERR,normfactor),round_other))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
        
        cadena="NumWd: "+str(NUMWD)+" NORM NumWd: "+str(round(safediv(NUMWD,normfactor),round_other))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
        
    if SHOW_HEd:
        cadena="%EdDist: "+str(EditDistance)+"\n"
        results_frame_text.insert(INSERT, cadena)
    
    if Calculate_pruned:

        cadena="PRUNED VALUES: \n"
        results_frame_text.insert(INSERT, cadena)
        
        cadena="mean time: "+str(round(meantime,round_time))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
        
        cadena="st. dev. time: "+str(round(stdevtime,round_time))+" "+normalizationstring+"\n"
        results_frame_text.insert(INSERT, cadena)
        
        if SHOW_LONG_PAUSES:
            ntotal_long_pauses_pruned=safediv(total_long_pauses_pruned,normfactor)
            cadena="TOTAL LONG PAUSES PRUNED: "+str(total_long_pauses_pruned)+" NORM LONG PAUSES: "+str(round(ntotal_long_pauses_pruned,round_other))+" "+normalizationstring+"\n"
            results_frame_text.insert(INSERT, cadena)
            
        if SHOW_INSERTIONS:
            cadena="TOTAL INSERTIONS: "+str(insertionstotal_pruned)+" NORM INSERTIONS: "+str(round(safediv(insertionstotal_pruned,normfactor),round_other))+" "+normalizationstring+"\n"
            results_frame_text.insert(INSERT, cadena)
        if SHOW_DELETIONS:
            cadena="TOTAL DELETIONS: "+str(deletionstotal_pruned)+" NORM DELETIONS: "+str(round(safediv(deletionstotal_pruned,normfactor),round_other))+" "+normalizationstring+"\n"
            results_frame_text.insert(INSERT, cadena)
        if SHOW_SUBSTITUTIONS:
            cadena="TOTAL SUBSTITUTIONS: "+str(substitutionstotal_pruned)+" NORM SUBSTITUTIONS: "+str(round(safediv(substitutionstotal_pruned,normfactor),round_other))+" "+normalizationstring+"\n"
            results_frame_text.insert(INSERT, cadena)
        if SHOW_REORDERING:
            cadena="TOTAL REORDERING: "+str(reorderingtotal_pruned)+" NORM REORDERING: "+str(round(safediv(reorderingtotal_pruned,normfactor),round_other))+" "+normalizationstring+"\n"
            results_frame_text.insert(INSERT, cadena)
        if SHOW_KSR:
            cadena="KSR: "+str(KSR_pruned)+"\n"
            results_frame_text.insert(INSERT, cadena)
        if SHOW_MAR:
            cadena="MAR: "+str(MAR_pruned)+"\n"
            results_frame_text.insert(INSERT, cadena)
        if SHOW_KSRM:
            cadena="KSRM: "+str(KSRM_pruned)+"\n"
            results_frame_text.insert(INSERT, cadena)
        if SHOW_HBLEU:
            cadena="BLEU: "+str(BLEU_pruned)+"\n"
            results_frame_text.insert(INSERT, cadena)
        if SHOW_HNIST:
            cadena="NIST: "+str(NIST_pruned)+"\n"
            results_frame_text.insert(INSERT, cadena)
        if SHOW_HTER:
            cadena="TER: "+str(TER_pruned)+"\n"
            results_frame_text.insert(INSERT, cadena)
        if SHOW_HTER_details:
            cadena="Ins: "+str(INS_pruned)+" NORM Ins: "+str(round(safediv(INS_pruned,normfactor),round_other))+" "+normalizationstring+"\n"
            results_frame_text.insert(INSERT, cadena)
            
            cadena="Del: "+str(DEL_pruned)+" NORM Del: "+str(round(safediv(DEL_pruned,normfactor),round_other))+" "+normalizationstring+"\n"
            results_frame_text.insert(INSERT, cadena)
            
            cadena="Sub: "+str(SUB_pruned)+" NORM Sub: "+str(round(safediv(SUB_pruned,normfactor),round_other))+" "+normalizationstring+"\n"
            results_frame_text.insert(INSERT, cadena)
            
            cadena="Shft: "+str(SHFT_pruned)+" NORM Shft: "+str(round(safediv(SHFT_pruned,normfactor),round_other))+" "+normalizationstring+"\n"
            results_frame_text.insert(INSERT, cadena)
            
            cadena="WdSh: "+str(WDSH_pruned)+" NORM WdSh: "+str(round(safediv(WDSH_pruned,normfactor),round_other))+" "+normalizationstring+"\n"
            results_frame_text.insert(INSERT, cadena)
            
            cadena="NumErr: "+str(NUMERR_pruned)+" NORM NumErr: "+str(round(safediv(NUMERR_pruned,normfactor),round_other))+" "+normalizationstring+"\n"
            results_frame_text.insert(INSERT, cadena)
            
            cadena="NumWd: "+str(NUMWD_pruned)+" NORM NumWd: "+str(round(safediv(NUMWD_pruned,normfactor),round_other))+" "+normalizationstring+"\n"
            results_frame_text.insert(INSERT, cadena)
            
        if SHOW_HWER:
            cadena="WER: "+str(WER_pruned)+"\n"
            results_frame_text.insert(INSERT, cadena)
        if SHOW_HEd:
            cadena="%EdDist: "+str(EditDistance_pruned)+"\n"
            results_frame_text.insert(INSERT, cadena)
    
    
    if Create_excel or Create_tabbedtext:
        fileresults=E2.get()
        if fileresults.endswith(".txt"): fileresults=fileresults.replace(".txt","")
        if fileresults.endswith(".xlsx"): fileresults=fileresults.replace(".xlsx","")
        nomexcelfile=fileresults+".xlsx"
        nomtextfile=fileresults+".txt"
        sortida=codecs.open(nomtextfile,"w",encoding="utf-8")
        workbook = xlsxwriter.Workbook(nomexcelfile)
        sheetAll = workbook.add_worksheet("All")
        sheetDetailed = workbook.add_worksheet("Detailed")
        sheetDetailed.set_column(1, 4, 30)
        bold = workbook.add_format({'bold': True})
        red = workbook.add_format({'color': 'red'})
        red.set_font_strikeout()
        blue = workbook.add_format({'color': 'blue'})
        text_wrap = workbook.add_format({'text_wrap': 1, 'valign': 'top'})

        bgred = workbook.add_format()
        bgred.set_pattern(1)  
        bgred.set_bg_color('red')

        sheetAll.set_column(0, 0, 20)
        filera=0
        sheetAll.write(filera,0,"EVALUATED SEGMENTS")
        sheetAll.write(filera,1,totalsegments)
        filera+=1
        
        sheetAll.write(filera,0,"EQUAL SEGMENTS")
        sheetAll.write(filera,1,equals)
        filera+=1
        
        sheetAll.write(filera,0,"% EQUAL SEGMENTS")
        sheetAll.write(filera,1,percentequalsegment)
        filera+=1
        
        sheetAll.write(filera,0,"TOTAL TOKENS")
        sheetAll.write(filera,1,toktotal)
        filera+=1
        
        sheetAll.write(filera,0,"EQUAL TOKENS")
        sheetAll.write(filera,1,tokequal)
        filera+=1
        
        sheetAll.write(filera,0,"% EQUAL TOKENS")
        sheetAll.write(filera,1,percentequaltokens)
        filera+=1
        
        sheetAll.write(filera,0,"TOTAL TIME")
        sheetAll.write(filera,1,timetotal)
        filera+=1
        
        sheetAll.write(filera,0,"NORM. TIME")
        sheetAll.write(filera,1,ntimetotal)
        sheetAll.write(filera,2,normalizationstring)
        filera+=1
        
        sheetAll.write(filera,0,"TOTAL KEYSTROKES")
        sheetAll.write(filera,1,keystrokestotal)
        filera+=1
        
        sheetAll.write(filera,0,"NORM. KEYSTROKES")
        sheetAll.write(filera,1,nkeystrokestotal)
        sheetAll.write(filera,2,normalizationstring)
        filera+=1
        
        sheetAll.write(filera,0,"TOTAL MOUSE ACTIONS")
        sheetAll.write(filera,1,mouseactionstotal)
        filera+=1
        
        sheetAll.write(filera,0,"NORM. MOUSE ACTIONS")
        sheetAll.write(filera,1,nmouseactionstotal)
        sheetAll.write(filera,2,normalizationstring)
        filera+=1
        
        if SHOW_LONG_PAUSES:
            sheetAll.write(filera,0,"TOTAL LONG PAUSES")
            sheetAll.write(filera,1,total_long_pauses)
            filera+=1
            
            sheetAll.write(filera,0,"NORM. TOTAL LONG PAUSES")
            sheetAll.write(filera,1,round(ntotal_long_pauses,round_other))
            sheetAll.write(filera,2,normalizationstring)
            filera+=1
        
        if SHOW_INSERTIONS:
            sheetAll.write(filera,0,"INSERTIONS")
            sheetAll.write(filera,1,insertionstotal)
            filera+=1
        
            sheetAll.write(filera,0,"NORM. INSERTIONS")
            sheetAll.write(filera,1,round(safediv(insertionstotal,normfactor),round_other))
            sheetAll.write(filera,2,normalizationstring)
            filera+=1
        if SHOW_DELETIONS:
            sheetAll.write(filera,0,"DELETIONS")
            sheetAll.write(filera,1,deletionstotal)
            filera+=1
            
            sheetAll.write(filera,0,"NORM. DELETIONS")
            sheetAll.write(filera,1,round(safediv(deletionstotal,normfactor),round_other))
            sheetAll.write(filera,2,normalizationstring)
            filera+=1
        if SHOW_SUBSTITUTIONS:
            sheetAll.write(filera,0,"SUBSTITUTIONS")
            sheetAll.write(filera,1,substitutionstotal)
            filera+=1
        
            sheetAll.write(filera,0,"NORM. SUBSTITUTIONS")
            sheetAll.write(filera,1,round(safediv(substitutionstotal,normfactor),round_other))
            sheetAll.write(filera,2,normalizationstring)
            filera+=1
        if SHOW_REORDERING:
            sheetAll.write(filera,0,"REORDERING")
            sheetAll.write(filera,1,reorderingtotal)
            filera+=1
            
            sheetAll.write(filera,0,"NORM. REORDERING")
            sheetAll.write(filera,1,round(safediv(reorderingtotal,normfactor),round_other))
            sheetAll.write(filera,2,normalizationstring)
            filera+=1
        if SHOW_KSR:
            sheetAll.write(filera,0,"KSR")
            sheetAll.write(filera,1,KSR)
            filera+=1
        if SHOW_MAR:
            sheetAll.write(filera,0,"MAR")
            sheetAll.write(filera,1,MAR)
            filera+=1
        if SHOW_KSRM:
            sheetAll.write(filera,0,"KSRM")
            sheetAll.write(filera,1,KSRM)
            filera+=1        
        if SHOW_HBLEU:
            sheetAll.write(filera,0,"BLEU")
            sheetAll.write(filera,1,BLEU)
            filera+=1
        if SHOW_HNIST:
            sheetAll.write(filera,0,"NIST")
            sheetAll.write(filera,1,NIST)
            filera+=1
        if SHOW_HTER:
            sheetAll.write(filera,0,"TER")
            sheetAll.write(filera,1,TER)
            filera+=1
        if SHOW_HTER_details:
            sheetAll.write(filera,0,"Ins")
            sheetAll.write(filera,1,INS)
            filera+=1
            
            sheetAll.write(filera,0,"NORM. Ins")
            sheetAll.write(filera,1,round(safediv(INS,normfactor),round_other))
            sheetAll.write(filera,2,normalizationstring)
            filera+=1
            
            sheetAll.write(filera,0,"Del")
            sheetAll.write(filera,1,DEL)
            filera+=1
            
            sheetAll.write(filera,0,"NORM. Del")
            sheetAll.write(filera,1,round(safediv(DEL,normfactor),round_other))
            sheetAll.write(filera,2,normalizationstring)
            filera+=1
            
            sheetAll.write(filera,0,"Sub")
            sheetAll.write(filera,1,SUB)
            filera+=1
            
            sheetAll.write(filera,0,"NORM. Sub")
            sheetAll.write(filera,1,round(safediv(SUB,normfactor),round_other))
            sheetAll.write(filera,2,normalizationstring)
            filera+=1
            
            sheetAll.write(filera,0,"Shft")
            sheetAll.write(filera,1,SHFT)
            filera+=1
            
            sheetAll.write(filera,0,"NORM. Shft")
            sheetAll.write(filera,1,round(safediv(SHFT,normfactor),round_other))
            sheetAll.write(filera,2,normalizationstring)
            filera+=1
            
            sheetAll.write(filera,0,"WdSh")
            sheetAll.write(filera,1,WDSH)
            filera+=1
            
            sheetAll.write(filera,0,"NORM. WDSH")
            sheetAll.write(filera,1,round(safediv(WDSH,normfactor),round_other))
            sheetAll.write(filera,2,normalizationstring)
            filera+=1
            
            sheetAll.write(filera,0,"NumErr")
            sheetAll.write(filera,1,NUMERR)
            filera+=1
            
            sheetAll.write(filera,0,"NORM. NumErr")
            sheetAll.write(filera,1,round(safediv(NUMERR,normfactor),round_other))
            sheetAll.write(filera,2,normalizationstring)
            filera+=1
            
            sheetAll.write(filera,0,"NumWd")
            sheetAll.write(filera,1,NUMWD)
            filera+=1
            
            sheetAll.write(filera,0,"NORM. NumWd")
            sheetAll.write(filera,1,round(safediv(NUMWD,normfactor),round_other))
            sheetAll.write(filera,2,normalizationstring)
            filera+=1
        if SHOW_HWER:
            sheetAll.write(filera,0,"WER")
            sheetAll.write(filera,1,WER)
            filera+=1
        if SHOW_HEd:
            sheetAll.write(filera,0,"%EdDist")
            sheetAll.write(filera,1,EditDistance)
            filera+=1
        
        if Calculate_pruned:
        
            sheetAll.write(filera,0,"PRUNED VALUES:",bold)
            filera+=1
            
            sheetAll.write(filera,0,"mean time:")
            sheetAll.write(filera,1,round(meantime,round_time))
            sheetAll.write(filera,2,normalizationstring) 
            filera+=1
            
            sheetAll.write(filera,0,"st. dev. time:")
            sheetAll.write(filera,1,round(stdevtime,round_time))
            sheetAll.write(filera,2,normalizationstring)
            filera+=1
            
            if SHOW_LONG_PAUSES:
                sheetAll.write(filera,0,"TOTAL LONG PAUSES")
                sheetAll.write(filera,1,total_long_pauses_pruned)
                filera+=1
                
                sheetAll.write(filera,0,"NORM. TOTAL LONG PAUSES")
                sheetAll.write(filera,1,round(ntotal_long_pauses_pruned,round_other))
                sheetAll.write(filera,2,normalizationstring)
                filera+=1
            
            if SHOW_INSERTIONS:
                sheetAll.write(filera,0,"INSERTIONS")
                sheetAll.write(filera,1,insertionstotal_pruned)
                filera+=1
                
                sheetAll.write(filera,0,"NORM. INSERTIONS")
                sheetAll.write(filera,1,round(safediv(insertionstotal_pruned,normfactor),round_other))
                sheetAll.write(filera,2,normalizationstring)
                filera+=1
            if SHOW_DELETIONS:
                sheetAll.write(filera,0,"DELETIONS")
                sheetAll.write(filera,1,deletionstotal_pruned)
                filera+=1
                
                sheetAll.write(filera,0,"NORM. DELETIONS")
                sheetAll.write(filera,1,round(safediv(deletionstotal_pruned,normfactor),round_other))
                sheetAll.write(filera,2,normalizationstring)
                filera+=1
            if SHOW_SUBSTITUTIONS:
                sheetAll.write(filera,0,"SUBSTITUTIONS")
                sheetAll.write(filera,1,substitutionstotal_pruned)
                filera+=1
                
                sheetAll.write(filera,0,"NORM. SUBSTITUTIONS")
                sheetAll.write(filera,1,round(safediv(substitutionstotal_pruned,normfactor),round_other))
                sheetAll.write(filera,2,normalizationstring)
                filera+=1
            if SHOW_REORDERING:
                sheetAll.write(filera,0,"REORDERING")
                sheetAll.write(filera,1,reorderingtotal_pruned)
                filera+=1
                
                sheetAll.write(filera,0,"NORM. REORDERING")
                sheetAll.write(filera,1,round(safediv(reorderingtotal_pruned,normfactor),round_other))
                sheetAll.write(filera,2,normalizationstring)
                filera+=1
            if SHOW_KSR:
                sheetAll.write(filera,0,"KSR")
                sheetAll.write(filera,1,KSR_pruned)
                filera+=1
            if SHOW_MAR:
                sheetAll.write(filera,0,"MAR")
                sheetAll.write(filera,1,MAR_pruned)
                filera+=1
            if SHOW_KSRM:
                sheetAll.write(filera,0,"KSRM")
                sheetAll.write(filera,1,KSRM_pruned)
                filera+=1
            if SHOW_HBLEU:
                sheetAll.write(filera,0,"BLEU")
                sheetAll.write(filera,1,BLEU_pruned)
                filera+=1
            if SHOW_HNIST:
                sheetAll.write(filera,0,"NIST")
                sheetAll.write(filera,1,NIST_pruned)
                filera+=1
            if SHOW_HWER:
                sheetAll.write(filera,0,"WER")
                sheetAll.write(filera,1,WER_pruned)
                filera+=1
            if SHOW_HTER:
                sheetAll.write(filera,0,"TER")
                sheetAll.write(filera,1,TER_pruned)
                filera+=1
            if SHOW_HTER_details:
                sheetAll.write(filera,0,"Ins")
                sheetAll.write(filera,1,INS_pruned)
                filera+=1
            
                sheetAll.write(filera,0,"NORM. Ins")
                sheetAll.write(filera,1,round(safediv(INS_pruned,normfactor),round_other))
                sheetAll.write(filera,2,normalizationstring)
                filera+=1
                
                sheetAll.write(filera,0,"Del")
                sheetAll.write(filera,1,DEL_pruned)
                filera+=1
                
                sheetAll.write(filera,0,"NORM. Del")
                sheetAll.write(filera,1,round(safediv(DEL_pruned,normfactor),round_other))
                sheetAll.write(filera,2,normalizationstring)
                filera+=1
                
                sheetAll.write(filera,0,"Sub")
                sheetAll.write(filera,1,SUB_pruned)
                filera+=1
                
                sheetAll.write(filera,0,"NORM. Sub")
                sheetAll.write(filera,1,round(safediv(SUB_pruned,normfactor),round_other))
                sheetAll.write(filera,2,normalizationstring)
                filera+=1
                
                sheetAll.write(filera,0,"Shft")
                sheetAll.write(filera,1,SHFT_pruned)
                filera+=1
                
                sheetAll.write(filera,0,"NORM. Shft")
                sheetAll.write(filera,1,round(safediv(SHFT_pruned,normfactor),round_other))
                sheetAll.write(filera,2,normalizationstring)
                filera+=1
                
                sheetAll.write(filera,0,"WdSh")
                sheetAll.write(filera,1,WDSH_pruned)
                filera+=1
                
                sheetAll.write(filera,0,"NORM. WdSh")
                sheetAll.write(filera,1,round(safediv(WDSH_pruned,normfactor),round_other))
                sheetAll.write(filera,2,normalizationstring)
                filera+=1
                
                sheetAll.write(filera,0,"NumErr")
                sheetAll.write(filera,1,NUMERR_pruned)
                filera+=1
                
                sheetAll.write(filera,0,"NORM. NumErr")
                sheetAll.write(filera,1,round(safediv(NUMERR_pruned,normfactor),round_other))
                sheetAll.write(filera,2,normalizationstring)
                filera+=1
                
                sheetAll.write(filera,0,"NumWd")
                sheetAll.write(filera,1,NUMWD_pruned)
                filera+=1
                
                sheetAll.write(filera,0,"NORM. NumWd")
                sheetAll.write(filera,1,round(safediv(NUMWD_pruned,normfactor),round_other))
                sheetAll.write(filera,2,normalizationstring)
            filera+=1
            if SHOW_HEd:
                sheetAll.write(filera,0,"%EdDist")
                sheetAll.write(filera,1,EditDistance_pruned)
                filera+=1
            
    sorter={}
    cont=0
    idents=sorted(list(data.keys()))
    for ident in idents:
        try:
            if Detailed_sort_measure=="BLEU": sorter[ident]=data[ident]["BLEU"]
            if Detailed_sort_measure=="NIST": sorter[ident]=data[ident]["NIST"]
            if Detailed_sort_measure=="WER": sorter[ident]=data[ident]["WER"]
            if Detailed_sort_measure=="TER": sorter[ident]=data[ident]["TER"]
            if Detailed_sort_measure=="EditDistance": sorter[ident]=data[ident]["EditDistance"]
            if Detailed_sort_measure=="Apparition": sorter[ident]=ident
            cont+=1
        except:
            pass
            
    if Detailed_sort_order=="ascending":
        sortident=sorted(sorter, key=sorter.get, reverse=False)
    elif Detailed_sort_order=="descending":  
        sortident=sorted(sorter, key=sorter.get, reverse=True) 
    
    cadena=[]
    sheetDetailed.write(0, 0, "IDENT.", bold)
    cadena.append("IDENT.")
    sheetDetailed.write(0, 1, "Source", bold)
    cadena.append("Source")
    sheetDetailed.write(0, 2, "Raw MT", bold)
    cadena.append("Raw MT")
    sheetDetailed.write(0, 3, "Post-Edited", bold)
    cadena.append("Post-Edited")
    sheetDetailed.write(0, 4, "DIFF.", bold)
    cadena.append("DIFF.")
    column=5
    if Detailed_results_LONG_PAUSES: 
        sheetDetailed.write(0, column, "LONG PAUSES", bold)
        cadena.append("LONG PAUSES")
        column+=1
    if Detailed_results_KSR: 
        sheetDetailed.write(0, column, "KSR", bold)
        cadena.append("KSR")
        column+=1
    if Detailed_results_MAR: 
        sheetDetailed.write(0, column, "MAR", bold)
        cadena.append("MAR")
        column+=1
    if Detailed_results_KSRM: 
        sheetDetailed.write(0, column, "KSRM", bold)
        cadena.append("KSRM")
        column+=1
    if Detailed_results_INSERTIONS: 
        sheetDetailed.write(0, column, "INSERTIONS", bold)
        cadena.append("INSERTIONS")
        column+=1
    if Detailed_results_DELETIONS: 
        sheetDetailed.write(0, column, "DELETIONS", bold)
        cadena.append("DELETIONS")
        column+=1
    if Detailed_results_SUBSTITUTIONS: 
        sheetDetailed.write(0, column, "SUBSTITUTIONS", bold)
        cadena.append("SUBSTITUTIONS")
        column+=1
    if Detailed_results_REORDERING: 
        sheetDetailed.write(0, column, "REORDERING", bold)
        cadena.append("REORDERING")
        column+=1
    if Detailed_results_BLEU: 
        sheetDetailed.write(0, column, "BLEU", bold)
        cadena.append("BLEU")
        column+=1
    if Detailed_results_NIST: 
        sheetDetailed.write(0, column, "NIST", bold)
        cadena.append("NIST")
        column+=1
    if Detailed_results_WER: 
        sheetDetailed.write(0, column, "WER", bold)
        cadena.append("WER")
        column+=1
    
    if Detailed_results_Ins: 
        sheetDetailed.write(0, column, "Ins", bold)
        cadena.append("Ins")
        column+=1
    if Detailed_results_Del: 
        sheetDetailed.write(0, column, "Del", bold)
        cadena.append("Del")
        column+=1
    if Detailed_results_Sub: 
        sheetDetailed.write(0, column, "Sub", bold)
        cadena.append("Sub")
        column+=1
    if Detailed_results_Shft: 
        sheetDetailed.write(0, column, "Shft", bold)
        cadena.append("Shft")
        column+=1
    if Detailed_results_WdSh: 
        sheetDetailed.write(0, column, "WdSh", bold)
        cadena.append("WdSh")
        column+=1
    if Detailed_results_NumErr: 
        sheetDetailed.write(0, column, "NumErr", bold)
        cadena.append("NumErr")
        column+=1
    if Detailed_results_NumWd: 
        sheetDetailed.write(0, column, "NumWd", bold)
        cadena.append("NumWd")
        column+=1
    if Detailed_results_TER: 
        sheetDetailed.write(0, column, "TER", bold)
        cadena.append("TER")
        column+=1
        
    if Detailed_results_Ed: 
        sheetDetailed.write(0, column, "EditDistance", bold)
        cadena.append("EditDistance")
        column+=1
    sheetDetailed.write(0, column, "TIME", bold)
    cadena.append("TIME")
    column+=1
    sheetDetailed.write(0, column, "TIME NORM.", bold)
    cadena.append("TIME_NORM")
    column+=1
    sheetDetailed.write(0, column, "KEYSTROKES", bold)
    cadena.append("KEYSTROKES")
    column+=1
    sheetDetailed.write(0, column, "KEYSTROKES NORM.", bold)
    cadena.append("KEYSTROKES_NORM")
    column+=1
    sheetDetailed.write(0, column, "MOUSEACTIONS", bold)
    cadena.append("KEYSTROKES")
    column+=1
    sheetDetailed.write(0, column, "MOUSEACTIONS NORM.", bold)
    cadena.append("KEYSTROKES_NORM")
    column+=1
    sheetDetailed.write(0, column, "PRUNED", bold)
    cadena.append("KEYSTROKES_NORM")
    column+=1
    cadena="\t".join(cadena)
    if Create_tabbedtext: sortida.write(cadena+"\n")
    row=1
    for sident in sortident:
        try:
            cadena=[]
            if data[sident]["PRUNED"]:
                sheetDetailed.write(row, 0, sident, bgred)
            else:
                sheetDetailed.write(row, 0, sident)
            cadena.append(str(sident))
            sheetDetailed.write(row, 1, data[sident]["source"], text_wrap)
            cadena.append(data[sident]["source"].replace("\n"," "))
            sheetDetailed.write(row, 2, data[sident]["rawMT"], text_wrap)
            cadena.append(data[sident]["rawMT"].replace("\n"," "))
            sheetDetailed.write(row, 3, data[sident]["postED"], text_wrap)
            cadena.append(data[sident]["postED"])
            dE=differencesExcel(data[sident]["postED"],data[sident]["rawMT"],red,blue,bold)
            dEtext=differences(data[sident]["postED"].replace("\n"," "),data[sident]["rawMT"].replace("\n"," "))
            sheetDetailed.write_rich_string(row,4, *dE, text_wrap)
            cadena.append(dEtext)
            column=5
            if Detailed_results_LONG_PAUSES: 
                sheetDetailed.write(row, column, data[sident]["LONG_PAUSES"])
                cadena.append(str(data[sident]["LONG_PAUSES"]))
                column+=1
            if Detailed_results_KSR: 
                KSR_det=round(data[sident]["KEYSTROKES"]/len(data[sident]["rawMT"]),round_KSR)
                sheetDetailed.write(row, column, KSR_det)
                cadena.append(str(KSR_det))
                column+=1
            if Detailed_results_MAR: 
                MAR_det=round(data[sident]["MOUSEACTIONS"]/len(data[sident]["rawMT"]),round_KSR)
                sheetDetailed.write(row, column, MAR_det)
                cadena.append(str(MAR_det))
                column+=1
            if Detailed_results_KSRM: 
                KSR_det=round(data[sident]["KEYSTROKES"]/len(data[sident]["rawMT"]),round_KSR)
                MAR_det=round(data[sident]["MOUSEACTIONS"]/len(data[sident]["rawMT"]),round_KSR)
                KSRM_det=KSR_det+MAR_det
                sheetDetailed.write(row, column, KSRM_det)
                cadena.append(str(data[sident]["KSRM"]))
                column+=1
            if Detailed_results_INSERTIONS: 
                sheetDetailed.write(row, column, data[sident]["INSERTIONS"])
                cadena.append(str(data[sident]["INSERTIONS"]))
                column+=1
            if Detailed_results_DELETIONS: 
                sheetDetailed.write(row, column, data[sident]["DELETIONS"])
                cadena.append(str(data[sident]["DELETIONS"]))
                column+=1
            if Detailed_results_SUBSTITUTIONS: 
                sheetDetailed.write(row, column, data[sident]["SUBSTITUTIONS"])
                cadena.append(str(data[sident]["SUBSTITUTIONS"]))
                column+=1
            if Detailed_results_REORDERING: 
                sheetDetailed.write(row, column, data[sident]["REORDERING"])
                cadena.append(str(data[sident]["REORDERING"]))
                column+=1
            if Detailed_results_BLEU: 
                sheetDetailed.write(row, column, data[sident]["BLEU"])
                cadena.append(str(data[sident]["BLEU"]))
                column+=1
            if Detailed_results_NIST: 
                sheetDetailed.write(row, column, data[sident]["NIST"])
                cadena.append(str(data[sident]["NIST"]))
                column+=1
            if Detailed_results_WER: 
                sheetDetailed.write(row, column, data[sident]["WER"])
                cadena.append(str(data[sident]["WER"]))
                column+=1
            if Detailed_results_Ins: 
                sheetDetailed.write(row, column, data[sident]["Ins"])
                cadena.append(str(data[sident]["Ins"]))
                column+=1
            if Detailed_results_Del: 
                sheetDetailed.write(row, column, data[sident]["Del"])
                cadena.append(str(data[sident]["Del"]))
                column+=1
            if Detailed_results_Sub: 
                sheetDetailed.write(row, column, data[sident]["Sub"])
                cadena.append(str(data[sident]["Sub"]))
                column+=1
            if Detailed_results_Shft: 
                sheetDetailed.write(row, column, data[sident]["Shft"])
                cadena.append(str(data[sident]["Shft"]))
                column+=1
            if Detailed_results_WdSh: 
                sheetDetailed.write(row, column, data[sident]["WdSh"])
                cadena.append(str(data[sident]["WdSh"]))
                column+=1
            if Detailed_results_NumErr: 
                sheetDetailed.write(row, column, data[sident]["NumErr"])
                cadena.append(str(data[sident]["NumErr"]))
                column+=1
            if Detailed_results_NumWd: 
                sheetDetailed.write(row, column, data[sident]["NumWd"])
                cadena.append(str(data[sident]["NumWd"]))
                column+=1
            if Detailed_results_TER: 
                sheetDetailed.write(row, column, data[sident]["TER"])
                cadena.append(str(data[sident]["TER"]))
                column+=1
            if Detailed_results_Ed: 
                sheetDetailed.write(row, column, data[sident]["EditDistance"])
                cadena.append(str(data[sident]["EditDistance"]))
                column+=1
            sheetDetailed.write(row, column, round(data[sident]["TIME"],round_time))
            cadena.append(str(round(data[sident]["TIME"],round_time)))
            column+=1
            sheetDetailed.write(row, column, round(data[sident]["TIME_NORM"],round_time))
            cadena.append(str(round(data[sident]["TIME_NORM"],round_time)))
            column+=1
            sheetDetailed.write(row, column, data[sident]["KEYSTROKES"])
            cadena.append(str(data[sident]["KEYSTROKES"]))
            column+=1
            sheetDetailed.write(row, column, round(data[sident]["KEYSTROKES_NORM"],round_keys))
            cadena.append(str(round(data[sident]["KEYSTROKES_NORM"],round_keys)))
            column+=1
            sheetDetailed.write(row, column, data[sident]["MOUSEACTIONS"])
            cadena.append(str(data[sident]["MOUSEACTIONS"]))
            column+=1
            sheetDetailed.write(row, column, round(data[sident]["MOUSEACTIONS_NORM"],round_mouse))
            cadena.append(str(round(data[sident]["MOUSEACTIONS_NORM"],round_mouse)))
            column+=1
            sheetDetailed.write(row, column, str(data[sident]["PRUNED"]))
            
            cadena.append(str(data[sident]["PRUNED"]))
            column+=1
            row+=1
            cadena="\t".join(cadena)
            if Create_tabbedtext:  sortida.write(cadena+"\n")
        except:
            print("ERROR",sys.exc_info())
            pass    
    workbook.close()
    
 
    
def copy_results():
    main_window.clipboard_append(results_frame_text.get("1.0",END))
    
if __name__ == "__main__":
    
    global timeprunelowerlimit
    global timepruneupperlimit
    global meantime
    global stdevtime
    
    if not os.path.isfile("config-analyzer.yaml"):
        messagebox.showerror("ERROR:", "No config-analyzer.yaml file.")
        sys.exit()
    
    stream = open('config-analyzer.yaml', 'r',encoding="utf-8")
    config=yaml.load(stream,Loader=Loader)

    filepathin=config['Filepath']['path_in']
    filepathout=config['Filepath']['path_out']
    
    tokenizerlist=config['Tokenizers']['list']
    defaultokenizer=config['Tokenizers']['default']
    
   
    normalization=config['Measures']['normalization']
    SHOW_INSERTIONS=config['Measures']['INSERTIONS']
    SHOW_DELETIONS=config['Measures']['DELETIONS']
    SHOW_SUBSTITUTIONS=config['Measures']['SUBSTITUTIONS']
    SHOW_REORDERING=config['Measures']['REORDERING']
    SHOW_KSR=config['Measures']['KSR']
    SHOW_MAR=config['Measures']['MAR']
    SHOW_KSRM=config['Measures']['KSRM']
    SHOW_HBLEU=config['Measures']['HBLEU']
    SHOW_HNIST=config['Measures']['HNIST']
    SHOW_HTER=config['Measures']['HTER']
    SHOW_HTER_details=config['Measures']['HTER_details']
    SHOW_HWER=config['Measures']['HWER']
    SHOW_HEd=config['Measures']['HEd']
    round_time=int(config['Measures']['round_time'])
    round_keys=int(config['Measures']['round_keys'])
    round_mouse=int(config['Measures']['round_mouse'])
    round_BLEU=int(config['Measures']['round_BLEU'])
    round_NIST=int(config['Measures']['round_NIST'])
    round_TER=int(config['Measures']['round_TER'])
    round_WER=int(config['Measures']['round_WER'])
    round_Ed=int(config['Measures']['round_Ed'])
    round_other=int(config['Measures']['round_other'])
    round_KSR=int(config['Measures']['round_KSR'])
    round_MAR=int(config['Measures']['round_MAR'])
    round_KSRM=int(config['Measures']['round_KSRM'])
    SHOW_LONG_PAUSES=int(config['Measures']['LONG_PAUSES'])
    min_pause_msec=float(config['Measures']['min_pause_msec'])/1000
    sum_additional_pause=int(config['Measures']['sum_additional_pause'])
    
    Detailed_results_LONG_PAUSES=config['Detailed_results']['LONG_PAUSES']
    Detailed_results_KSR=config['Detailed_results']['KSR']
    Detailed_results_MAR=config['Detailed_results']['MAR']
    Detailed_results_KSRM=config['Detailed_results']['KSRM']
    Detailed_results_BLEU=config['Detailed_results']['BLEU']
    Detailed_results_Ed=config['Detailed_results']['Ed']
    Detailed_results_NIST=config['Detailed_results']['NIST']
    Detailed_results_TER=config['Detailed_results']['TER']
    Detailed_results_WER=config['Detailed_results']['WER']
    Detailed_results_INSERTIONS=config['Detailed_results']['INSERTIONS']
    Detailed_results_DELETIONS=config['Detailed_results']['DELETIONS']
    Detailed_results_SUBSTITUTIONS=config['Detailed_results']['SUBSTITUTIONS']
    Detailed_results_REORDERING=config['Detailed_results']['REORDERING']
    
    Detailed_results_Ins=config['Detailed_results']['Ins']
    Detailed_results_Del=config['Detailed_results']['Del']
    Detailed_results_Sub=config['Detailed_results']['Sub']
    Detailed_results_Shft=config['Detailed_results']['Shft']
    Detailed_results_WdSh=config['Detailed_results']['WdSh']
    Detailed_results_NumErr=config['Detailed_results']['NumErr']
    Detailed_results_NumWd=config['Detailed_results']['NumWd']
    
    
    Detailed_sort_measure=config['Detailed_results']['sort_measure']
    Detailed_sort_order=config['Detailed_results']['sort_order']

    Calculate_pruned=config['Calculate_pruned']
    Create_excel=config['Create_excel']
    Create_tabbedtext=config['Create_tabbedtext']
    
    if not Create_excel and not Create_tabbedtext:
        Detailed_results_KSR=False
        Detailed_results_MAR=False
        Detailed_results_KSRM=False
        Detailed_results_BLEU=False
        Detailed_results_Ed=False
        Detailed_results_NIST=False
        Detailed_results_TER=False
        Detailed_results_WER=False
        Detailed_results_INSERTIONS=False
        Detailed_results_DELETIONS=False
        Detailed_results_SUBSTITUTIONS=False
        Detailed_results_LONG_PAUSES=False
        Detailed_results_Ins=False
        Detailed_results_Del=False
        Detailed_results_Sub=False
        Detailed_results_Shft=False
        Detailed_results_WdSh=False
        Detailed_results_NumErr=False
        Detailed_results_NmWd=False
        Detailed_results_REORDERING=False
    
    resultsfile=config['Files']['results']
   
    main_window = Tk()
    main_window.title("PosEdiOn Analyzer")

    notebook = ttk.Notebook(main_window)

    files_frame = Frame(notebook)
    B1=Button(files_frame, text = str("Open project file"), command=open_project_file,width=20)
    B1.grid(row=0,column=0)
    E1 = Entry(files_frame,  width=80)
    E1.grid(row=0,column=1)
    if Create_excel or Create_tabbedtext:
        B2=Button(files_frame, text = str("Results file"), command=open_results_file,width=20)
        B2.grid(row=1,column=0)
        E2 = Entry(files_frame,  width=80)
        E2.grid(row=1,column=1)
        E2.delete(0,END)
        E2.insert(0,resultsfile)
    
    L_tokenizers = Label(files_frame,text="Tokenizer:").grid(sticky="W",row=2,column=0)

    combo_tokenizers = ttk.Combobox(files_frame,state="readonly",values=tokenizerlist)
    combo_tokenizers.grid(sticky="W",row=2,column=1)

    position=tokenizerlist.index(defaultokenizer)   
    combo_tokenizers.current(position)


    B4=Button(files_frame, text = str("Analyze"), command=go,width=20)
    B4.grid(row=3,column=0)
    
    

    measures_frame = Frame(notebook)
    cbHTER = Checkbutton(measures_frame, text="HTER")
            
    results_frame = Frame(notebook)
    results_frame_text=scrolledtext.ScrolledText(results_frame,height=10)
    results_frame_text.grid(row=0,column=0)
    
    results_frame_B=Button(results_frame, text = str("Copy to clipboard"), command=copy_results,width=20)
    results_frame_B.grid(row=1,column=0)


    notebook.add(files_frame, text="Files", padding=30)
    notebook.add(results_frame, text="Results", padding=30)

    notebook.pack()
    notebook.pack_propagate(0) #Don't allow the widgets inside to determine the frame's width / height
    notebook.pack(fill=BOTH, expand=1)
    main_window.mainloop()

