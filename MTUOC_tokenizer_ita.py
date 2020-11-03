#    MTUOC_tokenizer_spa
#    Copyright (C) 2019  Antoni Oliver
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

from nltk import word_tokenize
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.tokenize.treebank import TreebankWordTokenizer, TreebankWordDetokenizer
import sys
import io
input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8',errors="replace")

def tokenize(segment):
    global subs
    tokens = tok.tokenize(segment)
    tokenized=" ".join(tokens)
    for sub in subs:
        tokenized=tokenized.replace(sub[0],sub[1])
        tokenized=tokenized.replace(sub[0].upper(),sub[1].upper())
        tokenized=tokenized.replace(sub[0].capitalize(),sub[1].capitalize())
    tokenized=' '.join(tokenized.split())
    return(tokenized)
    
def detokenize(segment):
    #generic
    tokens=segment.split(" ")
    desegment=detok.detokenize(tokens)
    return(desegment)
tok = ToktokTokenizer()
detok = TreebankWordDetokenizer()
subs=[

("all ' ","all' "),
("anch ' ","anch' "),
("assuefa ' ","assuefa' "),
("attivita ' ","attivita' "),
(" ' beh"," 'beh"),
("c ' ","c' "),
("citta ' ","citta' "),
("com ' ","com' "),
("confa ' ","confa' "),
("cos ' ","cos' "),
("d ' ","d' "),
("da ' ","da' "),
("dagl ' ","dagl' "),
("dall ' ","dall' "),
("dell ' ","dell' "),
("di ' ","di' "),
("disfa ' ","disfa' "),
("dov ' ","dov' "),
("fa ' ","fa' "),
("l ' ","l' "),
("libertà ' ","libertà' "),
("liquefa ' ","liquefa' "),
("m ' ","m' "),
("malfa ' ","malfa' "),
("n ' ","n'"),
(" ' ndrangheta"," 'ndrangheta"),
(" ' ndranghete"," 'ndranghete"),
(" ' ndrina"," 'ndrina"),
(" ' ndrine"," 'ndrine"),
("nell ' ","nell' "),
(" ' oh"," 'oh"),
("po ' ","po' "),
("putrefa ' ","putrefa' "),
("quell ' ","quell' "),
("quest ' ","quest' "),
("rarefa ' ","rarefa' "),
("rida ' ","rida' "),
("ridi ' ","ridi' "),
("rifa ' ","rifa' "),
("riva ' ","riva' "),
("s ' ","s' "),
("sant ' ","sant' "),
("senz ' ","senz' "),
("societa ' ","societa' "),
("soddisfa ' ","soddisfa' "),
("sopraffa ' ","sopraffa' "),
("sott ' ","sott' "),
("sottosta ' ","sottosta' "),
("sta ' ","sta' "),
("strafa ' ","strafa' "),
("stupefa ' ","stupefa' "),
("sull ' ","sull' "),
("t ' ","t' "),
("un ' ","un' "),
("va ' ","va' "),
("vent ' ","vent' "),
("vu ' ","vu' ")

]
    
nosplit={}

if __name__ == "__main__":
    if len(sys.argv)>1:
        action=sys.argv[1]
    else:
        action="tokenize"
    for line in sys.stdin:
        line=line.strip()
        #normalization of apostrophe
        line=line.replace("’","'")
        line=line.replace('“','"')
        line=line.replace('”','"')
        line=line.replace('.)',' . )')
        line=line.replace('/',' /')
        line=line.replace("\\","\\")
        line=line.replace("€"," € ")
        line=line.replace("£"," £ ")
        line=line.replace("¢"," ¢ ")
        line=line.replace("¥"," ¥ ")
        line=line.replace("#"," # ")
        
        if action=="tokenize":
            output=tokenize(line)
            print(output)
        elif action=="detokenize":
            output=detokenize(line)
            print(output)


