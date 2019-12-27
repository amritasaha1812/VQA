#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 13:04:26 2019

@author: amrita
"""
import os
import json
import pickle as pkl

#VQA dataset
vqa_data_dir = '/dccstor/cssblr/amrita/VQA/data'
version = '2014'
split = 'train'
data_file = os.path.join(vqa_data_dir, 'v2_mscoco_'+split+version+'_annotations.json')
data = json.load(open(data_file))
vqa_image_ids = []
for annotation in data['annotations']:
    image_id = annotation['image_id']
    vqa_image_ids.append(image_id)
#print (vqa_image_ids[:10])
vqa_image_ids = set(vqa_image_ids)    
    
masked_rcnn_dir = '/dccstor/cssblr/amrita/Mask_RCNN/results/coco'
version = '2014'
split = 'train'
data_file = os.path.join(masked_rcnn_dir, 'coco_eval_'+version+'_'+split+'.pkl')
data = pkl.load(open(data_file, 'rb'), encoding='latin1')
annotations = data.cocoGt.anns
mrcnn_image_ids = []
for ann in annotations:
    image_id = annotations[ann]['image_id']
    mrcnn_image_ids.append(image_id)
mrcnn_image_ids = set(mrcnn_image_ids)    
print ('Intersection ', len(mrcnn_image_ids.intersection(vqa_image_ids)), ' out of ', len(vqa_image_ids))    
neural_motifs_dir = '/dccstor/cssblr/amrita/neural-motifs/results'
version = '2014'
split = 'train'
data_file = os.path.join(neural_motifs_dir, 'motifnet_predcls_'+split+'.pkl')
data = pkl.load(open(data_file, 'rb'), encoding='latin1')
nmotif_image_ids = []
for d in data:
    image_id = int(d['image_filename'].split('/')[-1].split('.')[0])
    nmotif_image_ids.append(image_id)
#print (nmotif_image_ids[:10])
nmotif_image_ids = set(nmotif_image_ids)
print ('Intersection ', len(nmotif_image_ids.intersection(vqa_image_ids)), ' out of ', len(vqa_image_ids))    
