#KAF/NAF Python wrapper for the It-Makes-Sense WSD system#

This repository implements a wrapper in Python around the It Makes Sense (IMS) system for Word Sense Disambiguation of English text to allow KAF or NAF files as input or output.
The description of the KAF or NAF format can be found at https://github.com/opener-project/kaf and http://www.newsreader-project.eu/files/2013/01/techreport.pdf

##Requirements##
This are the only two dependencies:
* KafNafParserPy library, that can be found at https://github.com/cltl/KafNafParserPy
* IMS system that can be found at http://www.comp.nus.edu.sg/~nlp/software.html


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
git clone XXX
cd IMS_WSD
install_ims.sh
git clone https://github.com/cltl/KafNafParserPy
```

##Usage##

The main script is the `call_ims.py` script. It reads a KAF or NAF file from the standard input, and writes the KAF or NAF file extended with sense information
provided by the IMS WSD system to the standard output. The KAF/NAF input file must have at least the token layer (created by a tokeniser) and the term layer (created
bt a Pos-tagger usually). There is one example file in the repository, the file `input.kaf`. To call to the IMS system with this file and write the result to the file
`output.kaf`, you should just run:

```shell
cat input.kaf | python call_ims.py > output.kaf
```



##Contact##
* Ruben Izquierdo
* Vrije University of Amsterdam
* ruben.izquierdobevia@vu.nl

