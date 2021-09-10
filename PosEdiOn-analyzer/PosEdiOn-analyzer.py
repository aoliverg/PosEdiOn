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
        ident=completeid(result[0])
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
    
    cur.execute('SELECT * FROM actions')
    results=cur.fetchall()
    cont=0
    lenprev=0
    controlX=False
    controlV=False
    for result in results:
        cont+=1
        action_id=result[0]
        tipus=result[1]
        ident=completeid(result[2])
        date_string=result[3]
        key_pressed=result[4]
        position=result[5]
        len_posted=result[6]
        edit_mode=result[7]
        chars=len(data[ident]["rawMT"])
        tokens=len(data[ident]["rawMT_tok"])
        
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
        if cont==1 or tipus=="IN" or tipus=="START" or tipus=="RESTART":
            timestart=datetime.datetime.strptime(date_string,'%Y-%m-%d %H:%M:%S.%f')
            lenprev=len_posted
            controlX=False
            controlV=False
        elif tipus=="OUT" or tipus=="PAUSE" or tipus=="EXIT":
            len_prev=0
            controlX=False
            controlV=False
            timesend=datetime.datetime.strptime(date_string,'%Y-%m-%d %H:%M:%S.%f')
            seconds=(timesend-timestart).total_seconds()
            data[ident]["TIME"]+=seconds
            if normalization=="char": data[ident]["TIME_NORM"]+=seconds/chars
            elif normalization=="token":  data[ident]["TIME_NORM"]+=seconds/tokens
            elif normalization=="segment":  data[ident]["TIME_NORM"]+=seconds
            
        elif tipus=="K": 
            data[ident]["KEYSTROKES"]+=1
            if normalization=="char": data[ident]["KEYSTROKES_NORM"]+=1/chars
            elif normalization=="token":  data[ident]["KEYSTROKES_NORM"]+=1/tokens
            elif normalization=="segment":  data[ident]["KEYSTROKES_NORM"]+=1
            if edit_mode=="Insert":
                if key_pressed.startswith("Key.letter") or key_pressed.startswith("Key.number") or key_pressed.startswith("Key.space") or key_pressed.startswith("Key.punctuation") or key_pressed.startswith("Key.mathematical") or key_pressed.startswith("Key.symbol"):
                    data[ident]["INSERTIONS"]+=1
            elif edit_mode=="Overwrite":
                if key_pressed.startswith("Key.letter") or key_pressed.startswith("Key.number") or key_pressed.startswith("Key.space") or key_pressed.startswith("Key.punctuation") or key_pressed.startswith("Key.mathematical") or key_pressed.startswith("Key.symbol"):
                    if len_posted>len_prev:
                        data[ident]["INSERTIONS"]+=1
                    elif len_posted==len_prev:
                        data[ident]["SUBSTITUTIONS"]+=1
            if key_pressed in ["Key.46.Delete","Key.8.Backspace"]:
                data[ident]["DELETIONS"]+=1
            
            
            
        elif tipus=="M": 
            data[ident]["MOUSEACTIONS"]+=1
            if normalization=="char": data[ident]["MOUSEACTIONS_NORM"]+=1/chars
            elif normalization=="token":  data[ident]["MOUSEACTIONS_NORM"]+=1/tokens
            elif normalization=="segment":  data[ident]["MOUSEACTIONS_NORM"]+=1
            
            
        elif tipus=="C":
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

    Round_BLEU=2
    Round_NIST=2
    Round_TER=2
    Round_WER=2
    Round_Ed=2

    resultsSegments={}
    resultsBleu={}
    resultsNist={}
    resultsTer={}
    resultsWer={}
    resultsEd={}


    Detailed_results_KSR=True
    Detailed_results_MAR=True
    Detailed_results_KSRM=True
    Detailed_results_BLEU=True
    Detailed_results_Ed=True
    Detailed_results_NIST=True
    Detailed_results_TER=True
    Detailed_results_WER=True
    Detailed_results_INSERTIONS=True
    Detailed_results_DELETIONS=True
    Detailed_results_SUBSTITUTIONS=True
    Detailed_results_REORDERING=True
    

    ident=sorted(list(data.keys()))
    references=[]
    references_tok=[]
    hypothesis=[]
    hypothesis_tok=[]
    references_pruned=[]
    references_tok_pruned=[]
    hypothesis_pruned=[]
    hypothesis_tok_pruned=[]
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
       
        try:
            BLEU_sentence=round(sentence_bleu([postED_tok],rawMT_tok),Round_BLEU)
            data[i]["BLEU"]=BLEU_sentence
        except:
            data[i]["BLEU"]="-"
            
        try:
            NIST_sentence=round(sentence_nist([postED_tok],rawMT_tok),Round_NIST)
            data[i]["NIST"]=NIST_sentence
        except:
            data[i]["NIST"]="-"
            
        try:
            TER_sentence=round(ter_corpus([postED_tok],[rawMT_tok]),Round_TER)
            data[i]["TER"]=TER_sentence
        except:
            data[i]["TER"]="-"

        try:
            WER_sentence=round(wer_score(postED_tok,rawMT_tok),Round_WER)
            data[i]["WER"]=WER_sentence 
        except:
            data[i]["WER"]="-"    
        
        try:
            ed_sentence=edit_distance(" ".join(postED_tok)," ".join(rawMT_tok))
            ed_sentence=100*ed_sentence/len(" ".join(rawMT_tok))
            ed_sentence=round(ed_sentence,Round_Ed)
            data[i]["EditDistance"]=ed_sentence
        except:
            data[i]["EditDistance"]="-"
            
        try:
            data[i]["KSR"]=round(data[i]["KEYSTROKES"]/len(rawMT),round_ksr)
        except:
            data[i]["KSR"]="-"
            
        try:
            data[i]["MAR"]=round(data[i]["MOUSEACTIONS"]/len(rawMT),round_mar)
        except:
            data[i]["MAR"]="-"
            
        try:
            data[i]["KSRM"]=round(data[i]["KSR"]+data[i]["MAR"],round_ksrm)
        except:
            data[i]["KSRM"]="-"
            
             
    #GLOBAL RESULTS
    results_frame_text.delete('1.0', END)
    totalsegments=len(hypothesis_tok)
    cadena="TOTAL EVALUATED SEGMENT PAIRS:"+str(totalsegments)+"\n"
    results_frame_text.insert(INSERT, cadena)
    resultsSegments["All"]=totalsegments
    
    percentequals=100*equals/cont
    resultsSegments['pcequalsegments']=percentequals
    resultsSegments['equalsegments']=equals
    cadena="EQUAL SEGMENTS: "+str(equals)+" OF "+str(cont)+" SEGMENTS - "+str(round(percentequals,2))+" %\n"
    results_frame_text.insert(INSERT, cadena)
    percentequals=100*tokequal/toktotal
    resultsSegments['totaltok' ]=toktotal
    resultsSegments['equaltok']=tokequal
    resultsSegments['pcequaltok']=round(percentequals,2)
    cadena="EQUAL TOKENS: "+str(tokequal)+" OF "+str(toktotal)+" TOKENS - "+str(round(percentequals,2))+" %\n"
    results_frame_text.insert(INSERT, cadena)
    if normalization=="char": scadena=" per char"
    elif normalization=="token": scadena=" per token"
    elif normalization=="segment": scadena=" per segment"
    
    if normalization=="char": ntimetotal=timetotal/chartotal
    elif normalization=="token": ntimetotal=timetotal/toktotal
    elif normalization=="segment": ntimetotal=timetotal/totalsegments
    if normalization=="char": resultsSegments['normalizationstring']="per char"
    elif normalization=="token": resultsSegments['normalizationstring']="per token"
    elif normalization=="segment": resultsSegments['normalizationstring']="per segment"
    td=str(datetime.timedelta(seconds=timetotal))
    tdl=td.split(":")
    td2=":".join(tdl[:-1])+":"+str(int(round(float(tdl[-1]),0)))
    cadena="TOTAL TIME: "+td2+" NORM TIME: "+str(round(ntimetotal,round_time))+scadena+"\n"
    results_frame_text.insert(INSERT, cadena)
    resultsSegments['total_time']=td2
    resultsSegments['norm_time']=round(ntimetotal,round_time)
    if normalization=="char": nkeystrokestotal=keystrokestotal/chartotal
    elif normalization=="token": nkeystrokestotal=keystrokestotal/toktotal
    elif normalization=="segment": nkeystrokestotal=keystrokestotal/totalsegments
    if normalization=="char": nmouseactionstotal=mouseactionstotal/chartotal
    elif normalization=="token": nmouseactionstotal=mouseactionstotal/toktotal
    elif normalization=="segment": nmouseactionstotal=mouseactionstotal/totalsegments
    cadena="TOTAL KEYSTROKES: "+str(keystrokestotal)+" NORM KEYSTROKES: "+str(round(nkeystrokestotal,2))+scadena+"\n"
    results_frame_text.insert(INSERT, cadena)
    cadena="TOTAL MOUSE ACTIONS: "+str(mouseactionstotal)+" NORM MOUSE ACTIONS: "+str(round(nmouseactionstotal,2))+scadena+"\n"
    results_frame_text.insert(INSERT, cadena)
    resultsSegments['total_keystrokes']=keystrokestotal
    resultsSegments['norm_keystrokes']=round(nkeystrokestotal,round_keys)
    resultsSegments['total_mouseactions']=keystrokestotal
    resultsSegments['norm_mouseactions']=round(nkeystrokestotal,round_mouse)
    try:
        KSR=keystrokestotal/chartotal
    except:
        KSR="-"
    resultsSegments["KSR"]=KSR
    try:
        MAR=mouseactionstotal/len(rawMT)
    except:
        MAR="-"
    resultsSegments["MAR"]=MAR    
    try:
        KSRM=KSR+MAR
    except:
        KSRM="-"
    resultsSegments["KSRM"]=KSRM
    
    cadena="INSERTIONS:"+str(insertionstotal)+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="DELETIONS: "+str(deletionstotal)+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="SUBSTITUTIONS: "+str(substitutionstotal)+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="REORDERING: "+str(round(reorderingtotal,round_ksrm))+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="KSR:     "+str(round(KSR,round_ksr))+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="MAR:     "+str(round(MAR,round_mar))+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="KSRM:    "+str(round(KSRM,round_ksrm))+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    
    try:
        BLEU=corpus_bleu(references_tok,hypothesis_tok)
        cadena="BLEU:    "+str(str(round(BLEU,Round_BLEU)))+"\n"
        results_frame_text.insert(INSERT, cadena)
        resultsBleu["All"]=round(BLEU,Round_BLEU)
    except:
        resultsBleu["All"]="-"
    
    try:
        NIST=corpus_nist(references_tok,hypothesis_tok)
        cadena="NIST:    "+str(round(NIST,Round_NIST))+"\n"
        results_frame_text.insert(INSERT, cadena)
        resultsNist["All"]=round(NIST,Round_NIST)
    except:
        resultsNist["All"]="-"
    try:
        TERcorpus=ter_corpus(references_tok,hypothesis_tok)
        cadena="TER:     "+str(round(TERcorpus,Round_TER))+"\n"
        results_frame_text.insert(INSERT, cadena)
        resultsTer["All"]=round(TERcorpus,Round_TER)
    except:
        resultsTer["All"]="-"
    
    try:
        WER=wer_corpus(references_tok,hypothesis_tok)
        cadena="WER:     "+str(round(WER,Round_WER))+"\n"
        results_frame_text.insert(INSERT, cadena)
        resultsWer["All"]=round(WER,Round_WER)
    except:
        resultsWer["All"]="-"
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
        
        EditDistance=100*(edtotal/chartotal)
        cadena="%EdDist: "+str(round(EditDistance,Round_Ed))+"\n"
        results_frame_text.insert(INSERT, cadena)
        resultsEd["All"]=round(EditDistance,Round_Ed)  
    except:
        print("ERROR",sys.exc_info())
        resultsEd["All"]="-"
        
    #PRUNED GLOBAL VALUES
    cadena="\nPRUNED VALUES: \n"
    results_frame_text.insert(INSERT,cadena)
    
    cadena="mean time: "+str(round(meantime,round_time))+scadena+"\n"
    results_frame_text.insert(INSERT,cadena)
    
    cadena="st. dev. time: "+str(round(stdevtime,round_time))+scadena+"\n"
    results_frame_text.insert(INSERT,cadena)
    
    try:
        KSR_pruned=keystrokestotal_pruned/chartotal
    except:
        KSR_pruned="-"
    resultsSegments["KSR_pruned"]=KSR
    try:
        MAR_pruned=mouseactionstotal_pruned/len(rawMT)
    except:
        MAR_pruned="-"
    resultsSegments["MAR_pruned"]=MAR    
    try:
        KSRM_pruned=KSR_pruned+MAR_pruned
    except:
        KSRM_pruned="-"
    resultsSegments["KSRM_pruned"]=KSRM_pruned
    
    cadena="KSR:     "+str(round(KSR_pruned,round_ksr))+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="MAR:     "+str(round(MAR_pruned,round_mar))+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="KSRM:    "+str(round(KSRM_pruned,round_ksrm))+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="INSERTIONS:"+str(insertionstotal_pruned)+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="DELETIONS: "+str(deletionstotal_pruned)+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="SUBSTITUTIONS: "+str(substitutionstotal_pruned)+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="REORDERING: "+str(round(reorderingtotal_pruned,round_ksrm))+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="KSR:     "+str(round(KSR_pruned,round_ksr))+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="MAR:     "+str(round(MAR_pruned,round_mar))+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    cadena="KSRM:    "+str(round(KSRM_pruned,round_ksrm))+"\n"
    results_frame_text.insert(INSERT, cadena)
    
    try:
        BLEU_PRUNED=corpus_bleu(references_tok_pruned,hypothesis_tok_pruned)
        cadena="BLEU:    "+str(str(round(BLEU_PRUNED,Round_BLEU)))+"\n"
        results_frame_text.insert(INSERT, cadena)
        resultsBleu["All_pruned"]=round(BLEU_PRUNED,Round_BLEU)
    except:
       
        resultsBleu["All_pruned"]="-"
    
    try:
        NIST_PRUNED=corpus_nist(references_tok_pruned,hypothesis_tok_pruned)
        cadena="NIST:    "+str(round(NIST_PRUNED,Round_NIST))+"\n"
        results_frame_text.insert(INSERT, cadena)
        resultsNist["All_pruned"]=round(NIST_PRUNED,Round_NIST)
    except:
        resultsNist["All_pruned"]="-"
        print("***ERROR NIST PRUNED",sys.exc_info())
    try:
        TERcorpus_PRUNED=ter_corpus(references_tok_pruned,hypothesis_tok_pruned)
        cadena="TER:     "+str(round(TERcorpus_PRUNED,Round_TER))+"\n"
        results_frame_text.insert(INSERT, cadena)
        resultsTer["All_pruned"]=round(TERcorpus_PRUNED,Round_TER)
    except:
        resultsTer["All_pruned"]="-"
        print("***ERROR TER PRUNED",sys.exc_info())
    
    try:
        WER_PRUNED=wer_corpus(references_tok_pruned,hypothesis_tok_pruned)
        cadena="WER:     "+str(round(WER_PRUNED,Round_WER))+"\n"
        results_frame_text.insert(INSERT, cadena)
        resultsWer["All_pruned"]=round(WER_PRUNED,Round_WER)
    except:
        resultsWer["All_pruned"]="-"
        print("***ERROR WER PRUNED",sys.exc_info())
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
        
        EditDistance_PRUNED=100*(edtotal/chartotal)
        cadena="%EdDist: "+str(round(EditDistance_PRUNED,Round_Ed))+"\n"
        results_frame_text.insert(INSERT, cadena)
        resultsEd["All_pruned"]=round(EditDistance_PRUNED,Round_Ed)  
    except:
        resultsEd["All"]="-"
        print("***ERROR ED PRUNED",sys.exc_info())

    #EXCEL
    
    

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
    sheetAll.write(filera,1,resultsSegments["All"])
    filera+=1
    
    sheetAll.write(filera,0,"EQUAL SEGMENTS")
    sheetAll.write(filera,1,resultsSegments["equalsegments"])
    filera+=1
    
    sheetAll.write(filera,0,"% EQUAL SEGMENTS")
    sheetAll.write(filera,1,resultsSegments["pcequalsegments"])
    filera+=1
    
    sheetAll.write(filera,0,"TOTAL TOKENS")
    sheetAll.write(filera,1,resultsSegments["totaltok"])
    filera+=1
    
    sheetAll.write(filera,0,"EQUAL TOKENS")
    sheetAll.write(filera,1,resultsSegments["equaltok"])
    filera+=1
    
    sheetAll.write(filera,0,"% EQUAL TOKENS")
    sheetAll.write(filera,1,resultsSegments["pcequaltok"])
    filera+=1
    
    sheetAll.write(filera,0,"TOTAL TIME")
    sheetAll.write(filera,1,resultsSegments["total_time"])
    filera+=1
    
    sheetAll.write(filera,0,"NORM. TIME")
    sheetAll.write(filera,1,resultsSegments["norm_time"])
    sheetAll.write(filera,2,resultsSegments["normalizationstring"])
    filera+=1
    
    sheetAll.write(filera,0,"TOTAL KEYSTROKES")
    sheetAll.write(filera,1,resultsSegments["total_keystrokes"])
    filera+=1
    
    sheetAll.write(filera,0,"NORM. KEYSTROKES")
    sheetAll.write(filera,1,resultsSegments["norm_keystrokes"])
    sheetAll.write(filera,2,resultsSegments["normalizationstring"])
    filera+=1
    
    sheetAll.write(filera,0,"TOTAL MOUSE ACTIONS")
    sheetAll.write(filera,1,resultsSegments["total_mouseactions"])
    filera+=1
    
    sheetAll.write(filera,0,"NORM. MOUSE ACTIONS")
    sheetAll.write(filera,1,resultsSegments["norm_mouseactions"])
    sheetAll.write(filera,2,resultsSegments["normalizationstring"])
    filera+=1
    
    sheetAll.write(filera,0,"KSR")
    sheetAll.write(filera,1,round(KSR,round_ksr))
    filera+=1
    
    sheetAll.write(filera,0,"MAR")
    sheetAll.write(filera,1,round(MAR,round_mar))
    filera+=1
    
    sheetAll.write(filera,0,"KSRM")
    sheetAll.write(filera,1,round(KSRM,round_ksrm))
    filera+=1
    
    sheetAll.write(filera,0,"INSERTIONS")
    sheetAll.write(filera,1,insertionstotal)
    filera+=1
    
    sheetAll.write(filera,0,"DELETIONS")
    sheetAll.write(filera,1,deletionstotal)
    filera+=1
    
    sheetAll.write(filera,0,"SUBSTITUTIONS")
    sheetAll.write(filera,1,substitutionstotal)
    filera+=1
    
    sheetAll.write(filera,0,"REORDERING")
    sheetAll.write(filera,1,reorderingtotal)
    filera+=1
    
    
    sheetAll.write(filera,0,"BLEU")
    sheetAll.write(filera,1,resultsBleu["All"])
    filera+=1
    
    sheetAll.write(filera,0,"NIST")
    sheetAll.write(filera,1,resultsNist["All"])
    filera+=1
    
    sheetAll.write(filera,0,"TER")
    sheetAll.write(filera,1,resultsTer["All"])
    filera+=1
    
    sheetAll.write(filera,0,"WER")
    sheetAll.write(filera,1,resultsWer["All"])
    filera+=1
    
    sheetAll.write(filera,0,"%EdDist")
    sheetAll.write(filera,1,resultsEd["All"])
    filera+=1
    
    sheetAll.write(filera,0,"PRUNED VALUES:")
    filera+=1
    
    sheetAll.write(filera,0,"mean time:")
    sheetAll.write(filera,1,round(meantime,round_time))
    sheetAll.write(filera,2,resultsSegments["normalizationstring"]) 
    filera+=1
    
    sheetAll.write(filera,0,"st. dev. time:")
    sheetAll.write(filera,1,round(stdevtime,round_time))
    sheetAll.write(filera,2,resultsSegments["normalizationstring"])
    filera+=1
    
    sheetAll.write(filera,0,"KSR")
    sheetAll.write(filera,1,round(KSR_pruned,round_ksr))
    filera+=1
    
    sheetAll.write(filera,0,"MAR")
    sheetAll.write(filera,1,round(MAR_pruned,round_mar))
    filera+=1
    
    sheetAll.write(filera,0,"KSRM")
    sheetAll.write(filera,1,round(KSRM_pruned,round_ksrm))
    filera+=1

    sheetAll.write(filera,0,"INSERTIONS")
    sheetAll.write(filera,1,insertionstotal_pruned)
    filera+=1
    
    sheetAll.write(filera,0,"DELETIONS")
    sheetAll.write(filera,1,deletionstotal_pruned)
    filera+=1
    
    sheetAll.write(filera,0,"SUBSTITUTIONS")
    sheetAll.write(filera,1,substitutionstotal_pruned)
    filera+=1
    
    sheetAll.write(filera,0,"REORDERING")
    sheetAll.write(filera,1,reorderingtotal_pruned)
    filera+=1

    sheetAll.write(filera,0,"BLEU")
    sheetAll.write(filera,1,resultsBleu["All_pruned"])
    filera+=1
    
    sheetAll.write(filera,0,"NIST")
    sheetAll.write(filera,1,resultsNist["All_pruned"])
    filera+=1
    
    sheetAll.write(filera,0,"TER")
    sheetAll.write(filera,1,resultsTer["All_pruned"])
    filera+=1
    
    sheetAll.write(filera,0,"WER")
    sheetAll.write(filera,1,resultsWer["All_pruned"])
    filera+=1
    
    sheetAll.write(filera,0,"%EdDist")
    sheetAll.write(filera,1,resultsEd["All_pruned"])
    filera+=1




    Detailed_sort_measure="Apparition"
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
            
    #if Detailed_sort_order=="ascending":
    sortident=sorted(sorter, key=sorter.get, reverse=False)
    #elif Detailed_sort_order=="descending":  
    #    sortident=sorted(sorter, key=sorter.get, reverse=True) 
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
    if Detailed_results_TER: 
        sheetDetailed.write(0, column, "TER", bold)
        cadena.append("WER")
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
    sortida.write(cadena+"\n")
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
            if Detailed_results_KSR: 
                sheetDetailed.write(row, column, data[sident]["KSR"])
                cadena.append(str(data[sident]["KSR"]))
                column+=1
            if Detailed_results_KSR: 
                sheetDetailed.write(row, column, data[sident]["MAR"])
                cadena.append(str(data[sident]["MAR"]))
                column+=1
            if Detailed_results_KSRM: 
                sheetDetailed.write(row, column, data[sident]["KSRM"])
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
            sortida.write(cadena+"\n")
        except:
            print("ERROR",sys.exc_info())
            pass
        
    workbook.close()
###    
    
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
    
    round_time=int(config['Measures']['round_time'])
    round_keys=int(config['Measures']['round_keys'])
    round_mouse=int(config['Measures']['round_mouse'])
    round_hTER=int(config['Measures']['round_hTER'])
    round_hBLEU=int(config['Measures']['round_hBLEU'])
    round_hEd=int(config['Measures']['round_hEd'])
    round_other=int(config['Measures']['round_other'])
    round_ksr=int(config['Measures']['round_KSR'])
    round_mar=int(config['Measures']['round_MAR'])
    round_ksrm=int(config['Measures']['round_KSRM'])
    
    resultsfile=config['Files']['results']
   
    main_window = Tk()
    main_window.title("PosEdiOn Analyzer")

    notebook = ttk.Notebook(main_window)

    files_frame = Frame(notebook)
    B1=Button(files_frame, text = str("Open project file"), command=open_project_file,width=20)
    B1.grid(row=0,column=0)
    E1 = Entry(files_frame,  width=80)
    E1.grid(row=0,column=1)
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

