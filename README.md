PosEdiOn
========

## Pre-requisites

The program should be run using Python3 (Windows users can use the exe file instead). To install the prerequisites:

```
sudo pip3 install -r requirements.txt
```

## PosEdiOn configuration

The configuration of PosEdion if performed using the config.yaml file. An example file is provided:

```
Text:
    file: original-TA.txt
    
Actions:
    file: actions.txt

Languages:
    source: eng
    target: spa

Size:
    height: 10
    width: 80
    
Behaviour:
    allowEditSL: True

Font:
    font: courier 12

Chronometer:
    status: show
    #possible values: show / hide
        
Definition:
    symbols: "! @ # $ % ^ & ( ) _ { } [ ] ' ? ¿ ! ¡ < >"
    punctuation: ", : ; ."
    nameuserdef1: mathematical
    userdef1: "+ - * / =" 
    nameuserdef2: None
    userdef2: None
    nameuserdef3: None
    userdef3: None
```

The Text:file: is the file containing the project. This is a tab delimited file containing the following fields:

```
cont \t segment-id \t source-text \t (mt-text)
```

The first field is a counter of the segment; the second fiedl is an id for the segment (it can be used for identifying the segments in the results file); the third field is the source text; the fourth, that is optional, is the machine translated text. In projects where the user should translate the text (not post-edit it), this field can be empty. Once the post-edition (or translation) project starts, a fifth field is generated contaning the postedited (or translated) text.
