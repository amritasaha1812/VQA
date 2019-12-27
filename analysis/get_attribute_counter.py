#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 10:43:31 2019

@author: amrita
"""
import pickle as pkl
import json
import sys
from collections import Counter

vqa_dir = '..'
visual_genome_dir = '../../VisualGenome'

questions = [x['question'].lower().replace('?','').strip() for x in json.load(open(vqa_dir+'/data/v2_OpenEnded_mscoco_train2014_questions.json'))['questions']]
questions.extend([x['question'].lower().replace('?','').strip() for x in json.load(open(vqa_dir+'/data/v2_OpenEnded_mscoco_val2014_questions.json'))['questions']]
attributes = set([x.lower().replace('_',' ').strip() for x in pkl.load(open(visual_genome_dir+'/data/preprocessed/attribute_regions.pkl','rb'), encoding='latin1').keys() if len(x.lower().replace('_',' ').strip())>2])
attribute_counter = {k:0 for k in attributes}
num_questions = len(questions)
split_id = int(sys.argv[1])
split_size = int(float(num_questions)/int(sys.argv[2]))
start_index = split_id*split_size
end_index = start_index + split_size
for q in questions[start_index:end_index]:
    for attr in attributes:
        if ' '+attr+' ' in ' '+q+' ':
            attribute_counter[attr]+=1
json.dump(attribute_counter, open(vqa_dir+'/data/attribute_counter/data_split_'+str(split_id)+'.json','w'), indent=1)
            
            
