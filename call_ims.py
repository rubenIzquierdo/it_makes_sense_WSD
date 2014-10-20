#!/usr/bin/env python

######## SET THIS ######
#__path_to_ims__ = '/Users/ruben/NLP_tools/it_makes_sense_WSD'
########################

import sys
import os
import argparse
import pprint
from collections import defaultdict
from subprocess import Popen, PIPE
from KafNafParserPy import *
from tempfile import NamedTemporaryFile
from path_to_ims import PATH_TO_IMS



DEBUG = 0
__encoding__ = 'utf-8'
__this_name__ = 'It_Makes_Sense_WSD'
__this_version__ = '0.2'
__this_dir__ =  os.path.dirname(os.path.realpath(__file__))
__wordnet171_path__ = __this_dir__+'/resources/WordNet-1.7.1'
__wordnet171_index_sense = __wordnet171_path__+'/dict/index.sense'


def load_skeys_for_words():
    skeys_for_word = defaultdict(set)
    if os.path.exists(__wordnet171_index_sense):
        fd = open(__wordnet171_index_sense,'r')
        for line in fd:
            fields = line.strip().split()
            skey = fields[0]
            word_pos = skey[:skey.find('%')+2]
            skeys_for_word[word_pos].add(skey)
        fd.close()
    else:
        print>>sys.stderr,'Wordnet index.sense file not found at',__wordnet171_index_sense
    return skeys_for_word
        

def parse_ims_annotation(this_annotation):
    # this annotation is like: <x length="1 interest%2:37:00::|0.3614994335108463 interest%2:42:00::|0.3229031978804859 interest%2:42:01::|0.3155973686086678">interested</x>'
    senses = []
    my_fields = this_annotation.split('"')
    list_senses = my_fields[1]
    individual_senses = list_senses.split(' ')
    for individual_sense in individual_senses[1:]:
        sensekey, confidence = individual_sense.split('|')
        senses.append((sensekey,confidence))
    return senses



def parse_ims_annotated_sentence(this_line, list_token_ids):
    senses_for_token_id = {}
    current = 0
    # This contains just tokens split by whitespace
    raw_fields = this_line.split(' ')
    new_fields = []
    inside_annotation = False
    for raw_field in raw_fields:
        if raw_field  == '<x':
            inside_annotation = True
            new_fields.append(raw_field)
        elif raw_field[-4:] == '</x>':
            inside_annotation = False
            new_fields[-1] = new_fields[-1]+' '+raw_field
        else:
            if inside_annotation:
                new_fields[-1] = new_fields[-1]+' '+raw_field
            else:
                new_fields.append(raw_field)
          
    ## New fields contains now something like:
    #[u'I', u'<x length="1 be%2:42:03::|0.21612409602974728069 be%2:42:05::|0.12065987567453207 be%2:42:07::|0.08296448212787011 be%2:42:02::|0.09493153098603405 be%2:42:04::|0.09308360964470858 be%2:42:08::|0.09418994674455654">am</x>',
    #u'<x length="1 interest%2:37:00::|0.3614994335108463 interest%2:42:00::|0.3229031978804859 interest%2:42:01::|0.3155973686086678">interested</x>',
    #u'in',u'the', u'<x le...
    # IT MUST CONTAIN THE SAME TOKENS AS IN THE INPUT SENTENCE
    if len(new_fields) != len(list_token_ids):
        print>>sys.stderr,'WARNING!!! Different number of tokens in the input KAF/NAF file and in the output from ItMakesSense'
        
    for num_token, this_field in enumerate(new_fields):
        if this_field[:2] == '<x':
            token_id = list_token_ids[num_token]
            senses_for_token_id[token_id] = parse_ims_annotation(this_field)
        
    return senses_for_token_id
    
    
    
    
def call_as_subprocess(input_filename,is_there_pos):
    this_out = NamedTemporaryFile('w', delete = False)
    this_out.close()
    
    cmd = ['testPlain.bash']
    cmd.append('models')    ##models folder must be inside the ims folder
    cmd.append(input_filename)
    cmd.append(this_out.name)
    cmd.append('lib/dict/index.sense')
    cmd.append('1 1') #is sentence splitted and tokenised
    if is_there_pos:
        cmd.append('1')
    else:
        cmd.append('0')
        
    this_ims = Popen(' '.join(cmd),  stdin=None, stdout=None, stderr = PIPE, shell = True, cwd = PATH_TO_IMS)
    return_code = this_ims.wait()

    sentences_tagged = []
    if return_code != 0:
        print>>sys.stderr,'Error with IMS at',PATH_TO_IMS
        print>>sys.stderr,this_ims.stderr.read()
    else:
        f_in = open(this_out.name,'r')
        for line in f_in:
            sentences_tagged.append(line.decode(__encoding__).strip())
        f_in.close()
    
    os.remove(this_out.name)
    return sentences_tagged
        
        
   
        
        
    
def call_ims(this_input, this_output, use_pos,use_morphofeat):
    knaf_obj = KafNafParser(this_input)

    print>>sys.stderr,'Reading the input ...'
    ###########################    
    #Mapping from token id ==> (term_id, lemma, pos)
    ###########################
    tid_term_pos_for_token_id = {}
    for term in knaf_obj.get_terms():
        span = term.get_span()
        if span is not None:
            for token_id in span.get_span_ids():
                #tid_term_pos_for_token_id[token_id] = (term.get_id(),term.get_lemma(),term.get_pos())
                if use_morphofeat:
                    pos = term.get_morphofeat()
                else:
                    pos = term.get_pos()
                tid_term_pos_for_token_id[token_id] = (term.get_id(),term.get_lemma(),pos)
    ###########################
    

    ###########################
    ## Load the sentences
    # This is a list of lists, where each sublist is a list of pairs (token_id, text)
    ###########################
    sentences = []
    this_sent = None
    current_sent = []
    for token in knaf_obj.get_tokens():
        if token.get_sent() != this_sent and this_sent is not None:
            sentences.append(current_sent)
            current_sent = [(token.get_id(),token.get_text())]
        else:
            current_sent.append((token.get_id(),token.get_text()))
        
        this_sent = token.get_sent()
        
    sentences.append(current_sent)
    ###########################

    
    ###########################
    # Create temporary input file for the IMS as it only read input from files
    ###########################
    this_temp = NamedTemporaryFile('w', delete = False)    
    for sentence in sentences:
        for token_id, token_text in sentence:
            if use_pos or use_morphofeat:
                term_id,lemma,pos = tid_term_pos_for_token_id[token_id]
                this_temp.write(token_text.encode(__encoding__)+'/'+pos.encode(__encoding__)+' ')
            else:
                this_temp.write(token_text.encode(__encoding__)+' ')
        this_temp.write('\n')
    this_temp.close()
    ###########################
    
    ###Loading mapping from word to list of sensekeys
    skeys_for_word = load_skeys_for_words()

    ###########################
    # Calling to 
    ###########################
    print>>sys.stderr,'Calling to IMS at',PATH_TO_IMS,'...'
    sentences_tagged = call_as_subprocess(this_temp.name,use_pos or use_morphofeat)
    os.remove(this_temp.name)
    ###########################
    
    print>>sys.stderr,'Adding external references and writing the output ...'
    for n, sentence in enumerate(sentences_tagged):
        list_token_ids = [token_id for token_id, token_text in sentences[n]]
        senses_for_token_id = parse_ims_annotated_sentence(sentence,list_token_ids)
        # Add the new information to the kaf/naf obj
        for token_id, senses in senses_for_token_id.items():
            answered_for_this_token = set()
            term_id,_,_ = tid_term_pos_for_token_id[token_id]   # termid, lemma, pos
            for sensekey, confidence in senses:
                new_ext_ref = CexternalReference()
                new_ext_ref.set_reference(sensekey)
                new_ext_ref.set_confidence(confidence)
                new_ext_ref.set_resource('ItMakesSense#WN-1.7.1')
                knaf_obj.add_external_reference_to_term(term_id, new_ext_ref)
                answered_for_this_token.add(sensekey)
                
            ##Adding the rest of possible skeys with probability 0
            possible_skeys = set()
            for answered_sense in answered_for_this_token:
                word_pos = answered_sense[:answered_sense.find('%')+2]
                possible_skeys = possible_skeys | skeys_for_word.get(word_pos,set())
            
            for possible_skey in possible_skeys:
                if possible_skey not in answered_for_this_token:
                    new_ext_ref = CexternalReference()
                    new_ext_ref.set_reference(possible_skey)
                    new_ext_ref.set_confidence('0')
                    new_ext_ref.set_resource('ItMakesSense#WN-1.7.1')
                    knaf_obj.add_external_reference_to_term(term_id, new_ext_ref)
            ##################
        
        
        
                
        
        if DEBUG:
            pprint.pprint('Sentence:'+str(n),stream=sys.stderr)
            pprint.pprint(sentences[n],stream=sys.stderr)
            pprint.pprint(sentence,stream=sys.stderr)
            pprint.pprint(senses_for_token_id, stream=sys.stderr)
            pprint.pprint('============', stream=sys.stderr)
            
    my_lp = Clp()
    my_lp.set_name(__this_name__)
    my_lp.set_version(__this_version__)
    my_lp.set_timestamp()
    
    knaf_obj.add_linguistic_processor('terms',my_lp)
    
    knaf_obj.dump(this_output)
        
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Wrapper for the ItMakesSense WSD system that allows KAF/NAF as input and output formats',
                                     usage='cat myfile.naf | '+sys.argv[0]+' [-h] [-pos|-morphofeat]')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-pos', dest='use_knaf_pos', action='store_true', help='Use the POS tags of the pos attribute in the input KAf/NAF file')
    group.add_argument('-morphofeat', dest='use_knaf_morpho', action='store_true', help='Use the POS tags of the morphofeat attribute in the input KAf/NAF file')
                                                    
    args = parser.parse_args()
    
    
    if sys.stdin.isatty():
        parser.print_help()
        sys.exit(-1)
    else:
        # Reading from the standard input
        call_ims(sys.stdin, sys.stdout, use_pos = args.use_knaf_pos, use_morphofeat = args.use_knaf_morpho)
    
    
