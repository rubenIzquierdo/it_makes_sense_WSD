#KAF/NAF Python wrapper for the It-Makes-Sense WSD system#

This repository implements a wrapper in Python around the It Makes Sense (IMS) system for Word Sense Disambiguation of English text to allow KAF or NAF files as input or output.
The description of the KAF or NAF format can be found at https://github.com/opener-project/kaf and http://www.newsreader-project.eu/files/2013/01/techreport.pdf

##Requirements##
This are the only two dependencies:
* KafNafParserPy library, that can be found at https://github.com/cltl/KafNafParserPy
* IMS system that can be found at http://www.comp.nus.edu.sg/~nlp/software.html

In case you want to use ILI synsets of WN30 instead of sensekeys of WN171 you should get also the mappings between
version provided by the UPC (http://www.talp.upc.edu/index.php/technology/tools/45-textual-processing-tools/98-wordnet-mappings/)

##Installation##
The installation is pretty simple, just follow these steps:

1. Go to the folder where you want to install this repository
2. Clone this repository
3. Clone the KafNafParserPy
4. Run `install_ims.sh` in the repository to download and install all the required files for the original IMS system

You could skip the step number 4 in case that you have already the IMS system installed on your machine (you should make sure that the models folder is actually a subfolder of the main root folder
for your IMS installation). In this case, edit the file `path_to_ims.py` and modify the variable PATH_TO_IMS to point to the correct path of IMS in your local machine.

This could be one example, given that you want to install this repository in `~/my_github`:
```shell
cd ~/my_github
git clone https://github.com/rubenIzquierdo/it_makes_sense_WSD.git
cd it_makes_sense_WSD
install_ims.sh
```

##Usage##

The main script is the `call_ims.py` script. It reads a KAF or NAF file from the standard input, and writes the KAF or NAF file extended with sense information
provided by the IMS WSD system to the standard output. The KAF/NAF input file must have at least the token layer (created by a tokeniser) and the term layer (created
bt a Pos-tagger usually). There is one example file in the repository, the file `input.kaf`. To call to the IMS system with this file and write the result to the file
`output.kaf`, you should just run:

```shell
cat input.kaf | python call_ims.py > output.kaf
```

You can get the help of the script by running:

```shell
call_ims.py -h
usage: cat myfile.naf | ./call_ims.py [-h] [-pos|-morphofeat]

Wrapper for the ItMakesSense WSD system that allows KAF/NAF as input and
output formats

optional arguments:
  -h, --help   show this help message and exit
  -ili30       Map skeys of WN171 provided by the system to ili synsets of
               WN30
  -pos         Use the POS tags of the pos attribute in the input KAf/NAF file
  -morphofeat  Use the POS tags of the morphofeat attribute in the input
               KAf/NAF file
```

You can force to use the pos-tag labels found in the input KAF/NAF file by specifying the parameter -pos or -morphofeat, which will refer to the pos attributes or to the morphofeat attributes on the term layer.
If you do not provide any of these parameters, the IMS will perform internally pos-tagging and lemmatisation (but the postags and lemmas in the input term layer will not be modified). The
parameter `-ili30` would generate WordNet3.0 synsets instead of sensekeys of WordNet1.7.1. For instance:
```xml
    <term lemma="bit" morphofeat="NN" pos="N" tid="t19" type="open">
      <span>
        <target id="w19"/>
      </span>
      <externalReferences>
        <externalRef confidence="0.3391744933419935" reference="bit%1:23:01::" resource="ItMakesSense#WN-1.7.1"/>
        <externalRef confidence="0.16435686275758304" reference="bit%1:28:00::" resource="ItMakesSense#WN-1.7.1"/>
	...
===========
    <term lemma="bit" morphofeat="NN" pos="N" tid="t19" type="open">
      <span>
        <target id="w19"/>
      </span>
      <externalReferences>
        <externalRef confidence="0.3391744933419935" reference="ili-30-13761407-n" resource="WordNet-3.0"/>
        <externalRef confidence="0.16435686275758304" reference="ili-30-15246853-n" resource="WordNet-3.0"/>>
	...
```

##Creating IMS training data from KAF/NAF##

You can create training data for training your own models with IMS with the script `convert_to_ims_training_format.py`. Calling to this
script with the option -h will provide you with the description of the parameters:
```shell
convert_to_ims_training_format.py -h
usage: convert_to_ims_training_format.py [-h] [-v] (-f FILE | -l FILE_PATHS)
                                         -o OUTPUT

Creates IMS training file from KAF/NAF files

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
  -f FILE        Single KAF/NAF file
  -l FILE_PATHS  File with a list of paths to KAF/NAF files
  -o OUTPUT      Output folder
```

The input can be either a single KAF/NAF file (`-f` option), or a file which contains a list of paths to KAF/NAF files (one per file, option `-l`). The output
parameter `-o` specifies the folder where you want to store all the training files. This script will generate two files for every lemma, one with the instances
and contexts for training, and one with the key senses. All the files will be stored in the output folder. Besides to this folder, a file will be generated
with the same name of the folder and the suffix `.word_list`. This file contains all the lemmas (without suffices) that have been generated, so it can be used
later to train the models by using the `train_one.bash` script provided with the IMS package.


##Contact##
* Ruben Izquierdo
* Vrije University of Amsterdam
* ruben.izquierdobevia@vu.nl  rubensanvi@gmail.com
* http://rubenizquierdobevia.com/

