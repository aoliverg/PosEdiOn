import codecs
import numpy as np
from matplotlib import pyplot as plt
import sys


varlist=[]


resultsfile=sys.argv[1]
measure="HTER"
try:
    toprune=sys.argv[2]
except:
    toprune="no"

if toprune=="pruned":
    prune=True
else:
    prune=False

column=0
if measure=="HBLEU": column=5
if measure=="Hed": column=6
if measure=="HTER": column=7

entrada=codecs.open(resultsfile,"r",encoding="utf-8")

cont=0
for linia in entrada:
    linia=linia.rstrip()
    cont+=1
    if cont>1:
        if linia.startswith("-----"): break
        camps=linia.split("\t")
        ispruned=eval(camps[2])
        include=False
        if not prune:
            include=True
        elif not ispruned:
            include=True
        if include:
            varlist.append(float(camps[column]))

print(varlist)
graphic={}

xs=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]

for x in xs:
    graphic[x]=0
    
for y in varlist:
    rx=round(y,1)
    if rx<=1:
        graphic[rx]+=1

ys=[]

for x in xs:
    ys.append(graphic[x])
    
barplot=plt.bar(xs,ys,width=0.1)
plt.xlim(0,1)
plt.xticks(np.arange(0,1,step=0.1))
plt.yticks(np.arange(0,max(ys)+2,step=5))

plt.title(measure+" distribution")
plt.xlabel(measure)
plt.ylabel("COUNT")
       
barplot[0].set_color('g')
barplot[1].set_color('g')
barplot[2].set_color('yellow')
barplot[3].set_color('yellow')
barplot[4].set_color('b')
barplot[5].set_color('b')
barplot[6].set_color('r')
barplot[7].set_color('r')
barplot[8].set_color('black')
barplot[9].set_color('black')
barplot[10].set_color('black')
    
plt.show()
