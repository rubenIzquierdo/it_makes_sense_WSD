#!/usr/bin/env python

import argparse
import sys
import os
from shutil import rmtree
from KafNafParserPy import KafNafParser
from lxml import etree 
from xml.sax.saxutils import escape

class Clexelt:
    def __init__(self, this_item, this_pos):
        self.item = this_item      #bank.n
        self.pos = this_pos       #unk
        self.instances = []
        self.existing_instances = set()
        
    def exists(self,instance_id):
        return instance_id in self.existing_instances
    
    def add_instance(self,this_instance):
        self.instances.append(this_instance)
        self.existing_instances.add(this_instance.id)
        
    def __repr__(self):
        return self.item+' '+self.pos+' '+str(len(self.instances))
    
    def __iter__(self):
        for ins in self.instances:
            yield ins
            
    def create_xml_node(self):
        node = etree.Element('lexelt')
        node.set('item',self.item)
        node.set('pos',self.pos)
        for instance in self.instances:
            node.append(instance.create_xml_node())
        return node
        
        
class Cinstance:
    def __init__(self):
        self.id = ''
        self.docsrc = ''
        self.tokens = []
        self.index_head = []
        self.key = ''
        
    def create_xml_node(self):
        node = etree.Element('instance')
        node.set('id', self.id)
        node.set('docsrc', self.docsrc)
        
        this_string = '<context>'
        start_head = min(self.index_head)
        end_head = max(self.index_head) + 1
        for num_token, token in enumerate(self.tokens):
            if num_token == start_head:
                this_string+=' <head>'+escape(token)
            elif num_token == end_head:
                this_string+='</head> '+escape(token)
            else:
                this_string+=' '+escape(token)
        this_string+='</context>'
        context_node = etree.fromstring(this_string)
        node.append(context_node)
        return node
        
        

def add_file(filename, data_lexelt, reftype='lexical_key'):
    obj = KafNafParser(filename)
    tokens_per_sent = {}
    sent_for_token = {}
    sents_in_order = []
    for token in obj.get_tokens():
        sentid = token.get_sent()
        if sentid not in sents_in_order:
            sents_in_order.append(sentid)
        sent_for_token[token.get_id()] = sentid
        if sentid not in tokens_per_sent: tokens_per_sent[sentid] = []
        tokens_per_sent[sentid].append((token.get_id(), token.get_text()))
        
    annotated_lemmas = []   # LIST of (full_id, token ids, lemma,pos,synset)
    for term in obj.get_terms():
        synset_label = None
        for ext_ref in term.get_external_references():
            if ext_ref.get_reftype() == 'lexical_key':
                synset_label = term.get_lemma()+'%'+ext_ref.get_reference()
            elif ext_ref.get_reftype() == 'sense' and ext_ref.get_resource() == 'WordNet-3.0':
                synset_label = ext_ref.get_reference()
            if synset_label is not None:
                break    

        if synset_label is not None:
            annotated_lemmas.append((filename+'#'+term.get_id(), term.get_span().get_span_ids(), term.get_lemma(), term.get_pos(), synset_label))
            
    for full_id, token_ids, lemma,pos, synset_label in annotated_lemmas:
        #CREATE NEW INSTANCE
        
        this_key = lemma+'.'+pos.lower()[0]
        if this_key not in data_lexelt:
            data_lexelt[this_key] = Clexelt(this_key,pos)
        
        if not data_lexelt[this_key].exists(full_id):
            #Create the new instance
            new_instance = Cinstance()
            new_instance.id = full_id
            new_instance.docsrc = filename
            new_instance.key = synset_label
            
            tokens = []
            target_indexes = []
            this_sent = sent_for_token[token_ids[0]]
            index = sents_in_order.index(this_sent)
            start_idx = max(index-2,0)
            end_idx = min(index+2,len(sents_in_order)-1)
            selected_sents = sents_in_order[start_idx:end_idx+1]
            num_token = 0
            for current_sent in selected_sents:
                for token_id, token_text in tokens_per_sent[str(current_sent)]:
                    tokens.append(token_text)
                    if token_id in token_ids:
                        target_indexes.append(num_token)
                    num_token += 1  
                    
            new_instance.tokens = tokens[:]
            new_instance.index_head = target_indexes[:]
            data_lexelt[this_key].add_instance(new_instance)            

            
        

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates IMS training file from KAF/NAF files', version='1.0')
    input_group = parser.add_mutually_exclusive_group(required=True)
    #input_group.add_argument('-d', dest='directory', help='Directory with NAF/KAF files')
    input_group.add_argument('-f', dest='file', help='Single KAF/NAF file')
    input_group.add_argument('-l', dest='file_paths', help='File with a list of paths to KAF/NAF files')
    #parser.add_argument('-e', dest='extension', choices = ['KAF','NAF'], help='Type of input files when input is a directory')
    parser.add_argument('-o', dest='output', required=True, help='Output folder')
    args = parser.parse_args()
    
    #if args.directory is not None and args.extension is None:
    #    print>>sys.stderr,'Extension of files must be specified when the input is a directory'
    #    sys.exit(-1)
        
    data_lexelt = {}
    if args.file_paths is not None:
        fi = open(args.file_paths,'r')
        for path in fi:
            print 'Processing %s' % path.strip()
            add_file(path.strip(), data_lexelt)
    else:
        add_file(args.file,  data_lexelt)
    
    if args.output[-1] == '/':
        args.output = args.output[:-1]
    if os.path.exists(args.output):
        rmtree(args.output)
    
    os.mkdir(args.output)
    fd_list = open(args.output+'.word_list','w')
    for item_key, lexelt in data_lexelt.items():
        fd_list.write('%s\n' % item_key)
        output_xml = os.path.join(args.output,item_key+'.train.xml')
        corpus = etree.Element('corpus')
        corpus.set('lang','en')
        corpus.append(lexelt.create_xml_node())
        train_tree = etree.ElementTree(corpus)
        train_tree.write(output_xml,encoding='UTF-8', pretty_print=True, xml_declaration=True)
        
        
        key_filename = os.path.join(args.output,item_key+'.train.key')
        fd_key = open(key_filename,'w')
        for instance in lexelt:
            fd_key.write('%s %s %s\n' % (lexelt.item, instance.id, instance.key))
        fd_key.close()
    fd_list.close()
    print 'List of words in %s' % fd_list.name
        
        