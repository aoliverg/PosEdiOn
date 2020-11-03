#    PosEdiOn
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

import tkinter as tk
from tkinter import *
from tkinter import scrolledtext
import yaml
from chronometer import Chronometer
import codecs
from pynput import keyboard
from pynput import mouse
from pynput.keyboard import Key, Listener
import datetime
import atexit
import pyperclip

def savestart():
    global cont
    cadena="START"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
    actions.write(cadena+"\n")

def saveexit():
    global cont
    cadena="EXIT"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
    actions.write(cadena+"\n")
    savefile()

def search_red(_event=None):
    global cont
    global project
    contactual=cont
    cont+=1
    continua=True
    while continua:
        if project[cont]["status"]=="revise":
            T1.config(state=NORMAL)
            T1.delete(1.0, END)
            T1.insert(tk.END, project[cont]["slsegment"])
            T1.config(state=DISABLED)
            T2.delete(1.0, END)
            T2.insert(tk.END, project[cont]["posteditedsegment"])
            if project[cont]["status"]=="done":
                T2.configure({"background": "pale green"})
            elif project[cont]["status"]=="todo":
                T2.configure({"background": "white"})
            elif project[cont]["status"]=="revise":
                T2.configure({"background": "red2"})
            tpos=str(cont)+"/"+str(contmax)
            tposition.set(tpos)
            continua=False
            
        elif cont==contmax:
            cont=0
        elif cont==contactual:
            continua=False
        cont+=1
    cont-=1

def go_to():
    global cont
    segnum=T3.get().rstrip()
    cont=int(segnum)
    T1.config(state=NORMAL)
    T1.delete(1.0, END)
    T1.insert(tk.END, project[cont]["slsegment"])
    T1.config(state=DISABLED)
    T2.delete(1.0, END)
    T2.insert(tk.END, project[cont]["posteditedsegment"])
    tpos=str(cont)+"/"+str(contmax)
    tposition.set(tpos)
    if project[cont]["status"]=="done":
        T2.configure({"background": "pale green"})
    elif project[cont]["status"]=="todo":
        T2.configure({"background": "white"})
    elif project[cont]["status"]=="revise":
        T2.configure({"background": "red2"})

def pause():
    global pauseF
    global actions
    if pauseF:
        t.start()
        cadena="RESTART"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
        actions.write(cadena+"\n")
        B1.config(text="PAUSE")
        pauseF=False
        T1.config(state=NORMAL)
        T2.config(state=NORMAL)
        B2.config(state=NORMAL)
        B6.config(state=NORMAL)
    else:
        t.stop()
        cadena="PAUSE"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
        actions.write(cadena+"\n")
        pauseF=True
        B1.config(text="RESTART")
        T1.config(state=DISABLED)
        T2.config(state=DISABLED)
        B2.config(state=DISABLED)
        B6.config(state=DISABLED)

def clock():
    global pauseF
    global tempsTotal
    if pauseF:
        pass
    else:
        tempsTotal+=1
        tempsTotal=round(tempsTotal,0)
        tsvar.set(str(datetime.timedelta(seconds=tempsTotal)))
    root.after(1000,clock)

def savefile():
    global project
    global filename
    sortida=codecs.open(filename,"w",encoding="utf-8")

    for clau in project.keys():
        cadena=str(clau)+"\t"+project[clau]['id']+"\t"+project[clau]["slsegment"]+"\t"+project[clau]["tlsegment"]+"\t"+project[clau]["posteditedsegment"].replace("\t"," ").rstrip()+"\t"+project[clau]["status"]
        sortida.write(cadena+"\n")
    sortida.close()
def next(_event=None):
    global cont
    global contmax
    global project
    global actions
    textmod=T2.get("1.0",END)

    cadena="OUT"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
    actions.write(cadena+"\n")
    cont+=1
    
    if cont>contmax:
        cont=1
    cadena="IN"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
    actions.write(cadena+"\n")
    T1.config(state=NORMAL)
    T1.delete(1.0, END)
    T1.insert(tk.END, project[cont]["slsegment"])
    T1.config(state=DISABLED)
    T2.config(state=NORMAL)
    T2.delete(1.0, END)
    T2.insert(tk.END, project[cont]["posteditedsegment"])
    tpos=str(cont)+"/"+str(contmax)
    tposition.set(tpos)
    if project[cont]["status"]=="done":
        T2.configure({"background": "pale green"})
    elif project[cont]["status"]=="todo":
        T2.configure({"background": "white"})
    elif project[cont]["status"]=="revise":
        T2.configure({"background": "red2"})

def accept(_event=None):
    global cont
    global contmax
    global project
    global actions
    if not pauseF:
        textmod=T2.get("1.0",END)
        project[cont]["posteditedsegment"]=textmod.replace("\t"," ")
        savefile()
        cadena="OUT"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
        actions.write(cadena+"\n")
        project[cont]["status"]="done"
        savefile()
        cont+=1
        
        if cont>contmax:
            cont=1
        cadena="IN"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
        actions.write(cadena+"\n")
    
        T1.config(state=NORMAL)
        T1.delete(1.0, END)
        T1.insert(tk.END, project[cont]["slsegment"])
        T1.config(state=DISABLED)
        T2.config(state=NORMAL)
        T2.delete(1.0, END)
        T2.insert(tk.END, project[cont]["posteditedsegment"])
        tpos=str(cont)+"/"+str(contmax)
        tposition.set(tpos)
        if project[cont]["status"]=="done":
            T2.configure({"background": "pale green"})
        elif project[cont]["status"]=="todo":
            T2.configure({"background": "white"})
        elif project[cont]["status"]=="revise":
            T2.configure({"background": "red2"})
        

def previous(_event=None):
    global cont
    global contmax
    global actions
    cadena="OUT"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
    actions.write(cadena+"\n")
    cont-=1
    
    if cont<=0:
        cont=contmax
    cadena="IN"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
    actions.write(cadena+"\n")
    T1.config(state=NORMAL)
    T1.delete(1.0, END)
    T1.insert(tk.END, project[cont]["slsegment"])
    T1.config(state=DISABLED)
    T2.config(state=NORMAL)
    T2.delete(1.0, END)
    T2.insert(tk.END, project[cont]["posteditedsegment"])
    tpos=str(cont)+"/"+str(contmax)
    tposition.set(tpos) 
    if project[cont]["status"]=="done":
        T2.configure({"background": "pale green"})
    elif project[cont]["status"]=="todo":
        T2.configure({"background": "white"})
    elif project[cont]["status"]=="revise":
        T2.configure({"background": "red2"})

def select_event_T1(event):
    try:
        selected_text=T1.get(tk.SEL_FIRST, tk.SEL_LAST)
        pyperclip.copy(selected_text)
    except tk.TclError:
        pass
        
def select_event_T2(event):
    try:
        selected_text=T2.get(tk.SEL_FIRST, tk.SEL_LAST)
        pyperclip.copy(selected_text)
    except tk.TclError:
        pass

def key_pressed(event):
    global cont
    global actions
    global pauseF
    try:
        position=T2.index(tk.INSERT)
        keyp=""
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
        elif not event.char=="" and ord(event.char) in [8,127]:
            keyp="Key.erase"
        elif not event.char=="" and  ord(event.char) in [9]:
            keyp="Key.tab"
            
        else:
            try:
                if event.char=="":
                    keyp="Key.spe(\"other\")"
                else:
                    keyp="Key.spe("+str(ord(event.char))+")"
            except:
                keyp="Key.spe(\"other\")"
    except:
        print("ERROR",sys.exc_info())
        pass
    cadena="K"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp+"\t"+str(position)
    actions.write(cadena+"\n")

def navigation_key(event):
    global cont
    global actions
    global pauseF
    position=T2.index(tk.INSERT)
    keyp="Key.navigation"
    
    cadena="K"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp+"\t"+str(position)
    actions.write(cadena+"\n")

def control_C(event):
    clipboard=root.clipboard_get()
    keyp="Command.CtrlC."+clipboard
    
    cadena="C"+"\t"+str(cont)+"\ŧ"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")
    
def control_X(event):
    clipboard=root.clipboard_get()
    keyp="Command.CtrlX."+clipboard
    
    cadena="C"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")
    
def control_V(event):
    keyp="Command.CtrlV"
    
    cadena="C"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")
    
def control_V(event):
    clipboard=root.clipboard_get()
    keyp="Command.Ctrlv."+clipboard
    
    cadena="C"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    
def control_N(event):
    keyp="Command.CtrlN"
    
    cadena="C"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")
    
def control_P(event):
    keyp="Command.CtrlP"
    
    cadena="C"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")
    
def control_Return(event):
    keyp="Command.CtrlReturn"
    
    cadena="C"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")
    
def control_G(event):
    keyp="Command.CtrlG"
    
    cadena="C"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")

def control_W(event):
    keyp="Command.CtrlW"
    
    cadena="C"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")
    
def control_R(event):
    keyp="Command.CtrR"
    
    cadena="C"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")
    
def control_S(event):
    keyp="Command.CtrlS"
    
    cadena="C"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")
    
def control_E(event):
    keyp="Command.CtrlE"
    
    cadena="C"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")
    
def control_U(event):
    keyp="Command.CtrlU"
    
    cadena="C"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")
    
def focus_in(event):
    keyp="Focus_in"
    
    cadena="F"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")
    
def focus_out(event):
    keyp="Focus_out"
    
    cadena="F"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+keyp
    actions.write(cadena+"\n")
        


def mouse_button1(event):
    Minfo="Mouse.button1"
    cadena="M"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+Minfo
    actions.write(cadena+"\n")
    
def mouse_doublebutton1(event):
    Minfo="Mouse.doublebutton1"
    cadena="M"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+Minfo
    actions.write(cadena+"\n")
    
def mouse_button2(event):
    Minfo="Mouse.button2"
    cadena="M"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+Minfo
    actions.write(cadena+"\n")
    
def mouse_doublebutton2(event):
    Minfo="Mouse.doublebutton2"
    cadena="M"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+Minfo
    actions.write(cadena+"\n")
    
def mouse_button3(event):
    Minfo="Mouse.button3"
    cadena="M"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+Minfo
    actions.write(cadena+"\n")
    
def mouse_doublebutton3(event):
    Minfo="Mouse.doublebutton3"
    cadena="M"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+Minfo
    actions.write(cadena+"\n")
    
def mouse_wheel(event):
    Minfo="Mouse.wheel_scroll"
    cadena="M"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+Minfo
    actions.write(cadena+"\n")

def clic_on_button(event):
    Minfo="Button"
    cadena="B"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())+"\t"+Minfo
    actions.write(cadena+"\n")

def paint_green(_event=None):
    global cont
    project[cont]["status"]="done"
    T2.configure({"background": "pale green"})
    
def paint_red(_event=None):
    global cont
    project[cont]["status"]="revise"
    T2.configure({"background": "red2"})

def paint_white(_event=None):
    global cont
    project[cont]["status"]="todo"
    T2.configure({"background": "white"})

def hide_timer():
    global timer
    timer.forget

def clear_target(_event=None):
    T2.delete(1.0, END)
    cadena="CLEAR"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
    actions.write(cadena+"\n")
    
def unclear_target(_event=None):
    global cont
    T2.delete(1.0, END)
    T2.insert(tk.END, project[cont]["tlsegment"])
    cadena="RESTORE"+"\t"+str(cont)+"\t"+str(project[cont]['id'])+"\t"+str(datetime.datetime.now())
    actions.write(cadena+"\n")





pauseF=False
tempsTotal=0

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



arxiuactions=config['Actions']['file']

entrada=codecs.open(arxiuactions,"a",encoding="utf-8")
entrada.close()

entrada=codecs.open(arxiuactions,"r",encoding="utf-8")

tempsTotal=0
timestart=0
timeend=0
tipus=""

for linia in entrada:
    linia=linia.rstrip()
    camps=linia.split("\t")
    tipus=camps[0]
    cont=camps[1]
    segment_id=camps[2]
    date_string=camps[3]
    
    if cont==1 or tipus=="IN" or tipus=="START" or tipus=="RESTART":
        timestart=datetime.datetime.strptime(date_string,'%Y-%m-%d %H:%M:%S.%f')
    elif tipus=="PAUSE" or tipus=="EXIT":
        timesend=datetime.datetime.strptime(date_string,'%Y-%m-%d %H:%M:%S.%f')
        seconds=(timesend-timestart).total_seconds()
        tempsTotal+=seconds


t=Chronometer()
t.start()

entrada.close()

filename=config['Text']['file']

actionsfile=config['Actions']['file']

entrada=codecs.open(filename,"r",encoding="utf-8")

actions=codecs.open(actionsfile,"a",encoding="utf-8",buffering=0)
actions.close()

actions=codecs.open(actionsfile,"r",encoding="utf-8",buffering=0)
actionslines=actions.readlines()

if len(actionslines)==0:
    lastsegment=0
else:
    lastline=actionslines[-1]
    lastsegment=int(lastline.split("\t")[1])
    


actions.close()

actions=codecs.open(actionsfile,"a",encoding="utf-8",buffering=0)



project={}
contid={}
for linia in entrada:
    linia=linia.rstrip()
    camps=linia.split("\t")
    cont=int(camps[0])
    project[cont]={}
    project[cont]['id']=camps[1]
    #contid[cont]=camps[0]
    project[cont]["slsegment"]=camps[2]
    if len(camps)>=4:
        project[cont]["tlsegment"]=camps[3]
    else:
        project[cont]["tlsegment"]=""
        camps.append("")
    if len(camps)>=5:
        project[cont]["posteditedsegment"]=camps[4]
        project[cont]["status"]="done"
    else:
        project[cont]["posteditedsegment"]=camps[3]
        project[cont]["status"]="todo"
    if len(camps)>=6:
        project[cont]["status"]=camps[5]
    else:
        project[cont]["status"]="todo"


contmax=cont

if lastsegment>=cont: 
    lastsegment=0
    cont=1
elif not lastsegment==0:
    cont=lastsegment
else:
    cont=1


entrada.close()



tsvar=tk.StringVar(root)
tsvar.set(round(tempsTotal,1))

tposition=tk.StringVar(root)
tpos=str(cont)+"/"+str(contmax)
tposition.set(tpos)

T1 = tk.scrolledtext.ScrolledText(root, height=height, width=width, wrap=WORD)
T1.configure(font=font)
T1.grid(row=0,column=0, columnspan=10)
T2 = tk.scrolledtext.ScrolledText(root, height=height, width=width, wrap=WORD)
T2.configure(font=font)
T2.grid(row=1,column=0, columnspan=10)
T1.insert(tk.END, project[cont]["slsegment"])
if allowEditSL:
    T1.config(state=NORMAL)
else:
    T1.config(state=DISABLED)

T2.insert(tk.END, project[cont]["posteditedsegment"])
if project[cont]["status"]=="done":
    T2.configure({"background": "pale green"})
if project[cont]["status"]=="todo":
    T2.configure({"background": "white"})

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

T1.bind("<<Selection>>", select_event_T1)
T2.bind("<<Selection>>", select_event_T2)

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
