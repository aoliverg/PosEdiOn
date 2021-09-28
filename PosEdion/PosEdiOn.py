#    PosEdiOn
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

import tkinter as tk
from tkinter import *
from tkinter import Tk
from tkinter import scrolledtext
from tkinter import messagebox 
import yaml
from chronometer import Chronometer
import codecs
from pynput import keyboard
from pynput import mouse
from pynput.keyboard import Key, Listener
import datetime
import atexit
import pyperclip
import os.path
import sys
import sqlite3

def savestart():
    global cont
    info=("START",lastsegment, datetime.datetime.now()) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime) VALUES (?,?,?)",info)

def saveexit():
    global cont
    print("Exiting...")
    cadena="EXIT"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
    info=("EXIT",lastsegment, datetime.datetime.now()) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime) VALUES (?,?,?)",info)
    conn.commit()
    print("Exiting2...")

def refresh(segmentid):
    global lastsegment
    global max_segment_id
    lastsegment=segmentid
    cur.execute('SELECT slsegment, rawMT, postEd, status FROM segments WHERE segment_id=?', (segmentid,))
    result=cur.fetchone()
    slsegment=result[0]
    rawMT=result[1]
    postEd=result[2]
    if postEd==None:
        postEd=rawMT
    status=result[3]
    T1.delete(1.0, END)
    T1.insert(tk.END, slsegment)
    T2.delete(1.0, END)
    T2.insert(tk.END, postEd)
    tpos=str(lastsegment)+"/"+str(max_segment_id)
    tposition.set(tpos)
    if status=="done":
        T2.configure({"background": "pale green"})
    elif status=="todo":
        T2.configure({"background": "white"})
    elif status=="revise":
        T2.configure({"background": "red2"})    
    else:
        T2.configure({"background": "white"})
        

def search_red(_event=None):
    global lastsegment
    cur.execute("SELECT segment_id FROM segments WHERE status='revise' order by segment_id asc")
    reds=cur.fetchall()
    redpositions=[]
    for r in reds:
        redpositions.append(r[0])
    found=False
    for r in redpositions:
        if r>lastsegment:   
            lenT2=len(T2.get("1.0",END))
            info=("OUT", lastsegment, datetime.datetime.now(),lenT2) 
            cur.execute("INSERT INTO actions (tipus, segment_id, datetime, len_posted) VALUES (?,?,?,?)",info)
            refresh(r)
            found=True
            T2.edit_reset()
            lenT2=len(T2.get("1.0",END))
            info=("IN", lastsegment, datetime.datetime.now(),lenT2) 
            cur.execute("INSERT INTO actions (tipus, segment_id, datetime, len_posted) VALUES (?,?,?,?)",info)
            break
    if not found:
        for r in redpositions:
            if r<lastsegment:
                lenT2=len(T2.get("1.0",END))
                info=("OUT", lastsegment, datetime.datetime.now(),lenT2) 
                cur.execute("INSERT INTO actions (tipus, segment_id, datetime, len_posted) VALUES (?,?,?,?)",info)
                refresh(r)
                found=True
                T2.edit_reset()
                lenT2=len(T2.get("1.0",END))
                info=("IN", lastsegment, datetime.datetime.now(),lenT2) 
                cur.execute("INSERT INTO actions (tipus, segment_id, datetime, len_posted) VALUES (?,?,?,?)",info)
                break
        
    
    

def go_to():
    global max_segment_id
    global segmentid
    global position
    segnum=T3.get().rstrip()
    position=int(segnum)
    if position>0 and position<=max_segment_id:
        lenT2=len(T2.get("1.0",END))
        info=("OUT", lastsegment, datetime.datetime.now(),lenT2) 
        cur.execute("INSERT INTO actions (tipus, segment_id, datetime, len_posted) VALUES (?,?,?,?)",info)
        refresh(position)
        T2.edit_reset()
        lenT2=len(T2.get("1.0",END))
        info=("IN", lastsegment, datetime.datetime.now(),lenT2) 
        cur.execute("INSERT INTO actions (tipus, segment_id, datetime, len_posted) VALUES (?,?,?,?)",info)

def pause():
    global pauseF
    global actions
    if pauseF:
        t.start()
        info=("RESTART",lastsegment, datetime.datetime.now()) 
        cur.execute("INSERT INTO actions (tipus, segment_id, datetime) VALUES (?,?,?)",info)
        B1.config(text="PAUSE")
        pauseF=False
        T1.config(state=NORMAL)
        T2.config(state=NORMAL)
        B2.config(state=NORMAL)
        B6.config(state=NORMAL)
    else:
        t.stop()
        cadena="PAUSE"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
        info=("PAUSE",lastsegment, datetime.datetime.now()) 
        cur.execute("INSERT INTO actions (tipus, segment_id, datetime) VALUES (?,?,?)",info)
        pauseF=True
        B1.config(text="RESTART")
        T1.config(state=DISABLED)
        T2.config(state=DISABLED)
        B2.config(state=DISABLED)
        B6.config(state=DISABLED)

def clock():
    global pauseF
    global tempsTotal
    global tempsAnterior
    if pauseF:
        pass
    else:
        tempsAra=datetime.datetime.now()
        tempsTotal+=(tempsAra-tempsAnterior).total_seconds()
        tempsAnterior=tempsAra
        tsvar.set(str(datetime.timedelta(seconds=round(tempsTotal,0))))
    root.after(250,clock)

def savefile():
    conn.commit()
    
def next(_event=None):
    global lastsegment
    global max_segment_id
    lenT2=len(T2.get("1.0",END))
    info=("OUT", lastsegment, datetime.datetime.now(),lenT2) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, len_posted) VALUES (?,?,?,?)",info)
    lastsegment+=1
    if lastsegment>max_segment_id: lastsegment=1
    refresh(lastsegment)
    lenT2=len(T2.get("1.0",END))
    info=("IN", lastsegment, datetime.datetime.now(),lenT2) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, len_posted) VALUES (?,?,?,?)",info)
    T2.edit_reset()
    conn.commit()
    
def previous(_event=None):
    global lastsegment
    global max_segment_id
    lenT2=len(T2.get("1.0",END))
    info=("OUT", lastsegment, datetime.datetime.now(),lenT2) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, len_posted) VALUES (?,?,?,?)",info)
    lastsegment-=1
    if lastsegment==0: lastsegment=max_segment_id
    refresh(lastsegment)
    lenT2=len(T2.get("1.0",END))
    info=("IN", lastsegment, datetime.datetime.now(),lenT2) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, len_posted) VALUES (?,?,?,?)",info)
    T2.edit_reset()

def accept(_event=None):
    global lastsegment
    global max_segment_id
    lenT2=len(T2.get("1.0",END))
    info=("OUT", lastsegment, datetime.datetime.now(),lenT2) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, len_posted) VALUES (?,?,?,?)",info)
    textmod=T2.get("1.0",END)
    data=(textmod,"done",lastsegment)
    conn.execute("UPDATE segments SET postED=?,status=? where segment_id=?",data)
    conn.commit()
    lastsegment+=1
    if lastsegment>max_segment_id: lastsegment=1
    refresh(lastsegment)
    lenT2=len(T2.get("1.0",END))
    info=("IN", lastsegment, datetime.datetime.now(),lenT2) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, len_posted) VALUES (?,?,?,?)",info)
    T2.edit_reset()


def select_text_T1(event):
    pass
    '''
    try:
        selected_text=T1.get(tk.SEL_FIRST, tk.SEL_LAST)
        pyperclip.copy(selected_text)
        
        clipboard=root.clipboard_get()
        keyp="select_text_T1."+clipboard
        info=("S",lastsegment, datetime.datetime.now(), keyp) 
        #cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
        
    except tk.TclError:
        pass
    '''
        
def select_text_T2(event):
    pass
    '''
    try:
        selected_text=T2.get(tk.SEL_FIRST, tk.SEL_LAST)
        pyperclip.copy(selected_text)
        
        clipboard=root.clipboard_get()
        keyp="select_text_T2."+clipboard
        info=("S",lastsegment, datetime.datetime.now(), keyp) 
        #cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
        
    except tk.TclError:
        pass
    '''

def getClipboardText():
    #rootAUX = tk.Tk()
    # keep the window from showing
    #rootAUX.withdraw()
    return root.clipboard_get()
    #rootAUX.destroy

def key_pressed(event):
    global lastsegment
    global max_segment_id
    global lastkeycode

    try:
        position=T2.index(tk.INSERT)
        lenT2=len(T2.get("1.0",END))
        edit_mode="Overwrite"
        if overwrite.get():
            edit_mode="Overwrite"
        else:
            edit_mode="Insert"
        try:
            keysym=event.keysym
        except:
            keysym=""
        try:
            keycode=event.keycode
        except:
            keycode=""
        if keysym=="Insert":
            if overwrite.get():
                overwrite.set(False)
                T2.configure(insertbackground='black')
                keyp="Key.setInsert"

            else:
                overwrite.set(True)
                T2.configure(insertbackground='red')
                keyp="Key.setOverwrite"
                
                            
        else:   
            
            keyp=""
            if not event.char=="" and overwrite.get():
                (line,pos)=position.split(".")
                pos=int(pos)
                position2=line+"."+str(pos+1)
                T2.delete(position, position2)
            if str(event.char) in userdef1:
                keyp="Key."+nameuserdef1+"."+str(event.char)
            elif event.char in userdef2:
                keyp="Key."+nameuserdef2+"."+str(event.char)
            elif event.char in userdef3:
                keyp="Key."+nameuserdef3+"."+str(event.char)
            elif event.char.isalpha():
                keyp="Key.letter."+str(event.char)
            elif event.char in ["0","1","2","3","4","5","6","7","8","9"]:
                keyp="Key.number."+str(event.char)
            elif event.char==" ":
                keyp="Key.space"
            elif event.char in valid_symbols:
                keyp="Key.symbol."+str(event.char)
            elif event.char in valid_punctuation:
                keyp="Key.punctuation."+str(event.char)
            #elif not event.char=="" and ord(event.char) in [8,127]:
            #    keyp="Key.erase"
            #elif not event.char=="" and  ord(event.char) in [9]:
            #    keyp="Key.tab"
            else:
                keyp="Key."+str(keycode)+"."+str(keysym)
                #try:
                #    if event.char=="":
                #        keyp="Key.spe(\"other\")"
                #    else:
                #        keyp="Key.spe("+str(ord(event.char))+")"
                #except:
                #    keyp="Key.spe(\"other\")"
    except:
        print("ERROR",sys.exc_info())
        pass
    register=True
    if keycode in [17,18,20,16]:
        if lastkeycode==keycode:
            register=False
    
    if register:
        info=("K",lastsegment, datetime.datetime.now(), keyp, position, lenT2, edit_mode) 
        cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed, position, len_posted, edit_mode) VALUES (?,?,?,?,?,?,?)",info)
        conn.commit()
    lastkeycode=keycode

def navigation_key(event):
    global cont
    global actions
    global pauseF
    global position
    position=T2.index(tk.INSERT)
    keyp="Key.navigation"
    info=("K",lastsegment, datetime.datetime.now(), keyp, position) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed, position) VALUES (?,?,?,?,?)",info)

def control_Z(event):
    keyp="Command.CtrlZ."
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)

def control_Y(event):
    keyp="Command.CtrlY."
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)

def control_C(event):
    clipboard_content=T2.selection_get()
    keyp="Command.CtrlC."+clipboard_content
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def control_X(event):
    clipboard_content=T2.selection_get()
    keyp="Command.CtrlX."+clipboard_content
    cadena="C"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
    
def control_V(event):
    #clipboard=root.clipboard_get()
    try:
        clipboard_content=getClipboardText()
    except:
        clipboard_content=""
    keyp="Command.CtrlV."+clipboard_content
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def control_N(event):
    keyp="Command.CtrlN"
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
    
def control_P(event):
    keyp="Command.CtrlP"
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def control_Return(event):
    keyp="Command.CtrlReturn"
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def control_G(event):
    keyp="Command.CtrlG"
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)

def control_W(event):
    keyp="Command.CtrlW"
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def control_R(event):
    keyp="Command.CtrR"
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def control_S(event):
    keyp="Command.CtrlS"
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def control_E(event):
    keyp="Command.CtrlE"
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def control_U(event):
    keyp="Command.CtrlU"
    info=("C",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def focus_in(event):
    keyp="Focus_in"
    info=("F",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def focus_out(event):
    keyp="Focus_out"
    info=("F",lastsegment, datetime.datetime.now(), keyp) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
        
def mouse_button1(event):
    Minfo="Mouse.button1"
    info=("M",lastsegment, datetime.datetime.now(), Minfo) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def mouse_doublebutton1(event):
    Minfo="Mouse.doublebutton1"
    info=("M",lastsegment, datetime.datetime.now(), Minfo) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def mouse_button2(event):
    Minfo="Mouse.button2"
    info=("M",lastsegment, datetime.datetime.now(), Minfo) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def mouse_doublebutton2(event):
    Minfo="Mouse.doublebutton2"
    info=("M",lastsegment, datetime.datetime.now(), Minfo) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def mouse_button3(event):
    Minfo="Mouse.button3"
    info=("M",lastsegment, datetime.datetime.now(), Minfo) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def mouse_doublebutton3(event):
    Minfo="Mouse.doublebutton3"
    info=("M",lastsegment, datetime.datetime.now(), Minfo) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)
    
def mouse_wheel(event):
    Minfo="Mouse.wheel_scroll"
    info=("M",lastsegment, datetime.datetime.now(), Minfo) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)

def clic_on_button(event):
    Minfo="Button"
    info=("B",lastsegment, datetime.datetime.now(), Minfo) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime, key_pressed) VALUES (?,?,?,?)",info)

def paint_green(_event=None):
    global lastsegment
    global max_segment_id
    data=("done",lastsegment)
    conn.execute("UPDATE segments SET status=? where segment_id=?",data)
    T2.configure({"background": "pale green"})
    info=("Paint_green",lastsegment, datetime.datetime.now()) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime) VALUES (?,?,?)",info)
    
def paint_red(_event=None):
    global lastsegment
    global max_segment_id
    data=("revise",lastsegment)
    conn.execute("UPDATE segments SET status=? where segment_id=?",data)
    T2.configure({"background": "red2"})
    info=("Paint_red",lastsegment, datetime.datetime.now()) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime) VALUES (?,?,?)",info)

def paint_white(_event=None):
    global lastsegment
    global max_segment_id
    data=("todo",lastsegment)
    conn.execute("UPDATE segments SET status=? where segment_id=?",data)
    T2.configure({"background": "white"})
    info=("Paint_white",lastsegment, datetime.datetime.now()) 
    cur.execute("INSERT INTO actions (tipus, segment_id, datetime) VALUES (?,?,?)",info)

def hide_timer():
    global timer
    timer.forget

def clear_target(_event=None):
    T2.delete(1.0, END)
    cadena="CLEAR"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
    
def unclear_target(_event=None):
    global cont
    T2.delete(1.0, END)
    T2.insert(tk.END, project[cont]["tlsegment"])
    cadena="RESTORE"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())




pauseF=False
tempsTotal=0

if not os.path.isfile("config.yaml"):
    messagebox.showerror("ERROR:", "No config.yaml file.")
    sys.exit()

stream = open('config.yaml', 'r')
config=yaml.load(stream,Loader=yaml.FullLoader)
height=config['Size']['height']
width=config['Size']['width']
font=config['Font']['font']
chrono=config['Chronometer']['status']
valid_symbols=config['Definition']['symbols'].split(" ")
valid_punctuation=config['Definition']['punctuation'].split(" ")
allowEditSL=False
if config['Behaviour']['allowEditSL']:
    allowEditSL=True

nameuserdef1=""
userdef1=[]
if not config['Definition']['nameuserdef1']=="None":
    nameuserdef1=config['Definition']['nameuserdef1']
if not config['Definition']['userdef1']=="None":
    userdef1=config['Definition']['userdef1'].split(" ")

nameuserdef2=""
userdef2=[]
if not config['Definition']['nameuserdef2']=="None":
    nameuserdef2=config['Definition']['nameuserdef2']
if not config['Definition']['userdef2']=="None":
    userdef2=config['Definition']['userdef2'].split(" ")

nameuserdef3=""
userdef3=[]
if not config['Definition']['nameuserdef3']=="None":
    nameuserdef3=config['Definition']['nameuserdef3']
if not config['Definition']['userdef3']=="None":
    userdef3=config['Definition']['userdef3'].split(" ")

root = tk.Tk()
root.title("PosEdiOn")
root.resizable(False, False) 

projectfile=config['Project']['file']

t=Chronometer()
t.start()

if os.path.isfile(projectfile):
    conn=sqlite3.connect(projectfile)
    cur = conn.cursor() 
else:
    print("Project file does not exist. Check the information in the config.yaml file. Exiting")
    sys.exit()
    
#CALCULEM EL TEMPS TOTAL PER AL CRONOMETRE
cur.execute('SELECT tipus, datetime FROM actions')
dts=cur.fetchall()

tempsTotal=0
timestart=0
timeend=0
cont=0
global tempsAnterior
tempsAnterior=datetime.datetime.now()
for dt in dts:
    tipus=dt[0]
    temps=datetime.datetime.strptime(dt[1],'%Y-%m-%d %H:%M:%S.%f')
    cont+=1
    if cont==1 or tipus=="IN" or tipus=="START" or tipus=="RESTART":
        timestart=temps
    elif tipus=="OUT" or tipus=="PAUSE" or tipus=="EXIT":
        timesend=temps
        seconds=(timesend-timestart).total_seconds()
        tempsTotal+=seconds


project={}
contid={}
global lastid
lastid=None
cur.execute("SELECT segment_id, slsegment, rawMT, postEd , status FROM segments order by segment_id asc")
for s in cur.fetchall():
   segment_id=s[0]
   slsegment=s[1]
   rawMT=s[2]
   postEd=s[3]
   status=s[4]
   cont=segment_id
   project[cont]={}
   project[cont]['id']=segment_id
   #contid[cont]=camps[0]
   project[cont]["slsegment"]=slsegment
   if not rawMT==None:
       project[cont]["tlsegment"]=rawMT
   else:
       project[cont]["tlsegment"]=""
   if not postEd==None:
       project[cont]["posteditedsegment"]=postEd
   else:
       project[cont]["posteditedsegment"]=""
   if not status==None:
       project[cont]["status"]=status
   else:
       project[cont]["status"]="todo"

global max_segment_id
max_segment_id=cont

cur.execute("SELECT segment_id FROM actions")
for s in cur.fetchall():
    cont=s[0]


global lastsegment
global lastkeyco
lastkeycode=""
if lastid==None:
    lastsegment=1
else:
    lastsegment=lastid

tsvar=tk.StringVar(root)
overwrite = tk.BooleanVar()
overwrite.set(False)
tsvar.set(round(tempsTotal,1))

tposition=tk.StringVar(root)
tpos=str(lastsegment)+"/"+str(max_segment_id)
tposition.set(tpos)


T1 = tk.scrolledtext.ScrolledText(root, height=height, width=width, wrap=WORD)
T1.configure(font=font)
T1.grid(row=0,column=0, columnspan=11)
T2 = tk.scrolledtext.ScrolledText(root, height=height, width=width, wrap=WORD, undo=True)
T2.configure(font=font)
T2.grid(row=1,column=0, columnspan=11)
if allowEditSL:
    T1.config(state=NORMAL)
else:
    T1.config(state=DISABLED)



if chrono=="show":
    timer=tk.Label(root,justify='center',textvariable = tsvar,font='courier 25')
    timer.grid(row=3,column=0)
    timer.forget


position=tk.Label(root,justify='center',textvariable = tposition,font='courier 25')
position.grid(row=3,column=1)

B1 = tk.Button(root, text="PAUSE", command=pause)
B1.grid(row=3,column=2)
B2 = tk.Button(root, text="ACCEPT", command=accept)
B2.grid(row=3,column=5)
B3 = tk.Button(root, text=">>", command=next)
B3.grid(row=3,column=6)
B4 = tk.Button(root, text="GO TO", command=go_to)
B4.grid(row=3,column=7)
B5 = tk.Button(root, text="<<", command=previous)
B5.grid(row=3,column=4)

B6 = tk.Button(root, text="Clear", command=clear_target)
B6.grid(row=3,column=9)


T3 = tk.Entry(root,width=5)
T3.configure(font=font)
T3.grid(row=3,column=8)


root.bind('<Control-p>', previous)
root.bind('<Control-n>', next)
root.bind('<Control-Return>', accept)

root.bind('<Control-g>', paint_green)
root.bind('<Control-w>', paint_white)
root.bind('<Control-r>', paint_red)
root.bind('<Control-s>', search_red)

root.bind('<Control-e>', clear_target)
root.bind('<Control-u>', unclear_target)

T2.bind("<Key>",key_pressed)
T2.bind('<Left>', navigation_key)
T2.bind('<Right>', navigation_key)
T2.bind('<Up>', navigation_key)
T2.bind('<Down>', navigation_key)


T2.bind("<Control-c>",control_C)
T2.bind("<Control-C>",control_C)
T2.bind("<Control-V>",control_V)
T2.bind("<Control-v>",control_V)
T2.bind("<Control-X>",control_X)
T2.bind("<Control-x>",control_X)

T1.bind("<Control-c>",control_C)
T2.bind("<Control-C>",control_C)
T1.bind("<Control-V>",control_V)
T1.bind("<Control-v>",control_V)
T1.bind("<Control-X>",control_X)
T1.bind("<Control-x>",control_X)


T1.bind('<Control-Return>', control_Return)
T1.bind('<Control-P>', control_P)
T1.bind('<Control-p>', control_P)
T1.bind('<Control-n>', control_N)
T1.bind('<Control-N>', control_N)
T1.bind('<Control-g>', control_G)
T1.bind('<Control-G>', control_G)
T1.bind('<Control-w>', control_W)
T1.bind('<Control-W>', control_W)
T1.bind('<Control-r>', control_R)
T1.bind('<Control-R>', control_R)
T1.bind('<Control-s>', control_S)
T1.bind('<Control-S>', control_S)
T1.bind('<Control-e>', control_E)
T1.bind('<Control-E>', control_E)
T1.bind('<Control-u>', control_U)
T1.bind('<Control-U>', control_U)

T2.bind('<Control-Return>', control_Return)
T2.bind('<Control-P>', control_P)
T2.bind('<Control-p>', control_P)
T2.bind('<Control-n>', control_N)
T2.bind('<Control-N>', control_N)
T2.bind('<Control-g>', control_G)
T2.bind('<Control-G>', control_G)
T2.bind('<Control-w>', control_W)
T2.bind('<Control-W>', control_W)
T2.bind('<Control-r>', control_R)
T2.bind('<Control-R>', control_R)
T2.bind('<Control-s>', control_S)
T2.bind('<Control-S>', control_S)
T2.bind('<Control-e>', control_E)
T2.bind('<Control-E>', control_E)
T2.bind('<Control-u>', control_U)
T2.bind('<Control-U>', control_U)

T2.bind('<Control-z>', control_Z)
T2.bind('<Control-Z>', control_Z)

T2.bind('<Control-y>', control_Y)
T2.bind('<Control-Y>', control_Y)

T1.bind("<<Selection>>", select_text_T1)
T2.bind("<<Selection>>", select_text_T2)

T1.bind("<FocusIn>", focus_in)
T1.bind("<FocusOut>", focus_out)

T2.bind("<FocusIn>", focus_in)
T2.bind("<FocusOut>", focus_out)

T1.bind("<Button-1>", mouse_button1) 
T1.bind("<Double-Button-1>", mouse_doublebutton1) 

T1.bind("<Button-2>", mouse_button2) 
T1.bind("<Double-Button-2>", mouse_doublebutton2) 

T1.bind("<Button-3>", mouse_button3) 
T1.bind("<Double-Button-3>", mouse_doublebutton3)

T1.bind("<MouseWheel>",mouse_wheel)


T2.bind("<Button-1>", mouse_button1) 
T2.bind("<Double-Button-1>", mouse_doublebutton1) 

T2.bind("<Button-2>", mouse_button2) 
T2.bind("<Double-Button-2>", mouse_doublebutton2) 

T2.bind("<Button-3>", mouse_button3) 
T2.bind("<Double-Button-3>", mouse_doublebutton3)

T2.bind("<MouseWheel>",mouse_wheel)

B1.bind("<Button>",clic_on_button)
B2.bind("<Button>",clic_on_button)
B3.bind("<Button>",clic_on_button)
B4.bind("<Button>",clic_on_button)
B5.bind("<Button>",clic_on_button)
B6.bind("<Button>",clic_on_button)

atexit.register(saveexit)


clock()

savestart()

refresh(lastsegment)

tk.mainloop()

'''
who - annotator
type - type of post-editing unit (HT - human translation, PE - post-editing)
src - source id
sys - system id
time - post-editing time
slen - number of tokens in source
mlen - number of tokens in MT
plen - number of tokens in PE
letters - letters typed
digits - digits typed
spaces - white chars typed
symbols - special symbols typed
navigation - navigation keystrokes
erase - erasing keystrokes
commands - commands entered (ctrl+c, etc.)
visible - visible keys typed
keystrokes - "total" keystrokes (except commands and navigation)
allkeys - total keystrokes
insertions - PET insertions
deletions - PET deletions
substitutions - PET substitutions
shifts - PET shifts
'''
