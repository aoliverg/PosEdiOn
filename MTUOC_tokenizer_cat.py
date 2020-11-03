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
subs=[
    ("l ' "," l' "),
    ("m ' "," m' "),
    ("n ' "," n' "),
    ("s ' "," s' "),
    ("d ' "," d' "),
    ("s ' "," s' "),
    ("t ' "," t' "),
    ("-la"," -la"),
    ("-les"," -les"),
    (" ' l"," 'l"),
    (" ' ls"," 'ls"),
    ("-ho"," -ho"),
    ("-hi"," -hi"),
    (" ' n"," 'n"),
    (" ' m"," 'm"),
    (" ' t"," 't"),
    (" ' ns"," 'ns"),
    ("-vos"," -vos"),
    ("-se"," -se"),
    ("-me-la"," -me -la"),
    ("-me-les"," -me -les"),
    ("-me ' n"," -me 'n"),
    ("-m ' hi"," -m' hi"),
    ("-m ' ho"," -m' ho"),
    ("-me ' l"," -me 'l"),
    ("-me ' ls"," -me 'ls"),
    ("-te-la"," -te -la"),
    ("-te-les"," -te -les"),
    ("-te ' n"," -te 'n"),
    ("-t ' hi"," -t' hi"),
    ("-t ' ho"," -t' ho"),
    ("-te ' l"," -te 'l"),
    ("-te ' ls"," -te 'ls"),
    ("-nos-la"," -nos -la"),
    ("-nos-les"," -nos -les"),
    ("-nos-el"," -nos -el"),
    ("-nos-els"," -nos -els"),
    ("-vos-la"," -vos -la"),
    ("-vos-les"," -vos -les"),
    ("-vos-ho"," -vos -ho"),
    ("-vos-hi"," -vos -hi"),
    ("-vos-en"," -vos -en"),
    ("-vos-el"," -vos -el"),
    ("-vos-els"," -vos -els"),
    ("-se ' m"," -se 'm"),
    ("-se ' t"," -se 't"),
    ("-se ' ns"," -se 'ns"),
    ("-se-us"," -se -us"),
    ("-se-la"," -se -la"),
    ("-se-les"," -se -les"),
    ("-se ' l"," -se 'l"),
    ("-se ' n"," -se 'n"),
    ("-s ' hi"," -s' hi"),
    ("-s ' ho"," -s' ho"),
    ("-se ' ls"," -se 'ls"),
    ("-se-li"," -se -li"),
    ("-se-me-la"," -se -me -la"),
    ("-se-me-les"," -se -me -les"),
    ("-se-me ' l"," -se -me 'l"),
    ("-se-me'n"," -se -me 'n"),
    ("-se-m ' hi"," -se -m' hi"),
    ("-se-m ' ho"," -se -m' ho"),
    ("-se-me ' ls"," -se -me 'ls"),
    ("-se-te-la"," -se -te -la"),
    ("-se-te-les"," -se -te -les"),
    ("-se-te ' l"," -se -te 'l"),
    ("-se-te ' n"," -se -te 'n"),
    ("-se-t ' hi"," -se -t' hi"),
    ("-se-t ' ho"," -se -t' ho"),
    ("-se-te ' ls"," -se -te 'ls"),
    ("-se-nos-la"," -se -nos -la"),
    ("-se-nos-les"," -se -nos -les"),
    ("-se-nos-ho"," -se -nos -ho"),
    ("-se-nos-hi"," -se -nos -hi"),
    ("-se-nos-en"," -se -nos -en"),
    ("-se-nos-el"," -se -nos -el"),
    ("-se-nos-els"," -se -nos -els"),
    ("-se-us-la"," -se -us -la"),
    ("-se-us-les"," -se -us -les"),
    ("-se-us-el"," -se -us -el"),
    ("-se-us-ho"," -se -us -ho"),
    ("-se-us-hi"," -se -us -hi"),
    ("-se-us-en"," -se -us -en"),
    ("-se-us-els"," -se -us -els"),
    ("-la-hi"," -la -hi"),
    ("-la ' n"," -la 'n"),
    ("-l ' en"," -l' en"),
    ("-les-en"," -les -en"),
    ("-les-hi"," -les -hi"),
    ("-l ' hi"," -l' hi"),
    ("-li-ho"," -li -ho"),
    ("-li ' n"," -li 'n"),
    ("-los-el"," -los -el"),
    ("-los-els"," -los -els"),
    ("-los-en"," -los -en"),
    ("-los-hi"," -los -hi"),
    ("-los-ho"," -los -ho"),
    ("-los-la"," -los -la"),
    ("-los-les"," -los -les"),
    (" ' ls-hi"," 'ls -hi"),
    (" ' ls-la"," 'ls -la"),
    (" ' ls-les"," 'ls -les"),
    ("-me-li"," -me -li"),
    ("-n ' hi"," -n 'hi"),
    ("-ne"," -ne"),
    ("-nos-en"," -nos -en"),
    ("-nos-hi"," -nos -hi"),
    ("-nos-ho"," -nos -ho"),
    ("-nos-li"," -nos -li"),
    (" ' ns-el"," 'ns -el"),
    (" ' ns-els"," 'ns -els"),
    (" ' ns-en"," 'ns -en"),
    (" ' ns-hi"," 'ns -hi"),
    (" ' ns-ho"," 'ns -ho"),
    (" ' ns-la"," 'ns -la"),
    (" ' ns-les"," 'ns -les"),
    (" ' ns-li"," 'ns -li"),
    ("-te-li"," -te -li"),
    ("-te ' m"," -te 'm"),
    ("-te ' ns"," -te 'ns"),
    ("-us-el"," -us -el"),
    ("-us-els"," -us -els"),
    ("-us-em"," -us -em"),
    ("-us-en"," -us -en"),
    ("-us-ens"," -us -ens"),
    ("-us-hi"," -us -hi"),
    ("-us-ho"," -us -ho"),
    ("-us-la"," -us -la"),
    ("-us-les"," -us -les"),
    ("-us-li"," -us -li"),
    ("-vos-em"," -vos -em"),
    ("-vos-ens"," -vos -ens"),
    ("-vos-li"," -vos -li"),
    ("-li"," -li"),
    ("-lo", " -lo"),
    ("-los"," -los"),
    ("-nos"," -nos"),
    ("-us"," -us"),
    ("-te"," -te"),
    ("-me"," -me"),
    (" ' s"," 's"),
    (" ' l"," 'l"),
    (" ' ls"," 'ls"),
    (" ' n"," 'n"),
    (" ' m"," 'm"),
    (" ' t"," 't"),
    (" ' ns"," 'ns")]
    
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


