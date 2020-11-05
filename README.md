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

When the project is started, an actions file is created (taking the name from the config.yaml, Actions:file:). This file contains all the actions performed by the user.


## PosEdiOn-analyzer configuration

The configuration of PosEdiOn-analyzed is also performed using a yaml file: config-analyzer.yaml

```
Filepath:
  path_in: /home/user/postedition
  path_out: /home/user/postedition

Files:
   results: results.txt

Measures:
   round_time: 2
   round_keys: 2
   round_hTER: 4
   round_hBLEU: 4
   round_hEd: 2
   round_other: 1
```

This configuration allows us to specify the initial input and output paths, the initial name of the result file and the number of decimals to round the results.
