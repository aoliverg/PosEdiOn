#    MTUOC_tokenizer_fra
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
    for det in subs:
        if not det[1]==det[1].replace(" ",""):
            segment=segment.replace(det[1],det[1].replace(" ",""))
            segment=segment.replace(det[1].upper(),det[1].replace(" ","").upper())
            segment=segment.replace(det[1].capitalize(),det[1].replace(" ","").capitalize())
    tokens=segment.split(" ")
    desegment=detok.detokenize(tokens)
    return(desegment)
tok = ToktokTokenizer()
detok = TreebankWordDetokenizer()
#p'tit (feminine singular p'tite, masculine plural p'tits, feminine plural p'tites)
subs=[
    ("p ' tit","p'tit"),
    ("p ' tite","p'tite"),
    ("p ' tits","p'tits"),
    ("p ' tites","p'tites"),
    ("anniv ' ","anniv' "),
    ("app ' ","app' "),
    ("aujourd ' hui","aujourd'hui"),
    ("c ' ","c' "),
    ("champ ' ","champ' "),
    ("ct ' ","ct' "),
    ("d ' ","d' "),
    ("grand ' ","grand' "),
    ("j ' ","j' "),
    ("jusqu ' ","jusqu'"),
    ("jusqu ' à","jusqu'à"),
    ("jusqu ' au","jusqu'au"),
    ("jusqu ' aux","jusqu'aux"),
    ("l ' ","l' "),
    ("l ' on ","l'on"),
    ("lorsqu ' ","lorsqu' "),
    ("-m ' "," -m' "),
    ("m ' ","m' "),
    ("n ' ","n' "),
    ("pauv ' ","pauv' "),
    ("presqu ' ","presqu' "),
    ("prod ' ","prod' "),
    ("puisqu ' ","puisqu' "),
    ("qu ' ","qu' "),
    ("quelqu ' ","quelq' "),
    ("quelqu ' un","quelqu'une"),
    ("quelqu ' une","quelqu'une"),
    ("quéqu ' ","qu'equ' "),
    ("quoiqu ' ","quoiqu' "),
    ("répèt ' ","répèt' "),
    ("s ' ","s' "),
    ("sal ' ","sal' "),
    ("-t ' ","-t' "),
    ("t ' ","t' "),
    ("vot ' ","vot' ")
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


