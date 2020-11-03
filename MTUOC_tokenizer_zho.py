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

import sys
input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8',errors="replace")
#This is a simplified tokenization-detokenization process for Chinese. It is useful for Neural Machine Translation.

#TOKENIZATION: splits all by spaces
#DETOKENIZATION: removes all spaces

def tokenize(segment):
    tokenized = " ".join(list(segment))
    return(tokenized)
    
def detokenize(segment):
    desegment=segment.replace(" ","")
    return(desegment)

if __name__ == "__main__":
    if len(sys.argv)>1:
        action=sys.argv[1]
    else:
        action="tokenize"
    for line in sys.stdin:
        line=line.strip()
        
        if action=="tokenize":
            output=tokenize(line)
            print(output)
        elif action=="detokenize":
            output=detokenize(line)
            print(output)


