#    MTUOC_tokenizer_eng
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
subs=[
(" ' s"," 's"),
("wouldn ' t","wouldn 't"),
("won ' t","won 't"),
("can ' t","can 't"),
("aren ' t","aren 't"),
("couldn ' t","couldn 't"),
("didn ' t","didn 't"),
("doesn ' t","doesn 't"),
("don ' t","don 't"),
("hadn ' t","hadn 't"),
("hasn ' t","hasn 't"),
("haven ' t","haven 't"),
("he ' d","he 'd"),
("he ' s","he 's"),
("I ' d","I 'd"),
("I ' ll","I 'll"),
("I ' m","I 'm"),
("I ' ve","I ' ve"),
("isn ' t","isn 't"),
("let 's","let 's"),
("mightn 't","mightn 't"),
("mustn ' t","mustn ' t"),
("shan ' t","shan 't"),
("she ' d","she 'd"),
("she ' ll","she 'll"),
("she ' s","she 's"),
("shouldn ' t","shouldn 't"),
("that ' s","that 's"),
("there ' s","there 's"),
("they ' d","they 'd"),
("they ' ll","they 'll"),
("they ' re","they 're"),
("they ' ve","they 've"),
("we ' d","we 'd"),
("we ' re","we 're"),
("we ' ve","we 've"),
("weren ' t","weren 't"),
("what ' ll","what 'll"),
("what ' re","what 're"),
("what ' s","what 's"),
("what ' ve","what 've"),
("where ' s","where 's"),
("who ' d","who 'd"),
("who ' ll","who 'll"),
("who ' re","who 're"),
("who ' s","who 's"),
("you ' re","you 're"),
("you ' ll","you 'll"),
("you ' ve","you 've"),
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


