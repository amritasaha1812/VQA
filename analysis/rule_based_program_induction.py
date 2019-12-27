import sys
import os
import json 
import spacy
import pickle as pkl
from collections import Counter
objects_counter = Counter()
attributes_counter = Counter()
relations_counter = Counter()

nlp = spacy.load('en_core_web_sm')
visual_genome_dir = '../../VisualGenome'
vqa_dir = '..'
def process_lexicon(d, f):
	for x in json.load(open(f)):
		pos_tag = x.split('.')[-2]
		x_text = '.'.join(x.split('.')[:-2]).lower().replace('_',' ')
		x_lemma = ' '.join([xi.text if xi.lemma_.startswith('-') else xi.lemma_ for xi in nlp(x_text.replace('-',' '))])
		d[x_text.replace('_',' ')+'.'+pos_tag] = [x]
		d[x_lemma+'.'+pos_tag] = [x]
	return d

def process_alias_lexicon(d, f, pos_tags):
	original_lexicon = {'.'.join(x[0].split('.')[:-2]):x[0] for x in d.values()}
	for x in open(f).readlines():
		xs = [xi.strip() for xi in x.split(',')]
		xs_words_in_lexicon = set([])
		for x in xs:
			xs_words_in_lexicon.update([original_lexicon[w] for w in x.split(' ') if w in original_lexicon])
		xs_words_in_lexicon = list(xs_words_in_lexicon)
		for xi in xs:
			d.update({xi+'.'+pos_i:xs_words_in_lexicon for pos_i in pos_tags})	 
	return d

leading = 'What'.lower()
middle = ['is', 'was', 'are', 'were', 'would', 'do', 'did', 'does', 'has', 'have', 'kind']
if not os.path.exists(visual_genome_dir+'/data/preprocessed_object_types_expanded.json'):
	objects = process_lexicon({}, visual_genome_dir+'/data/raw/object_types.json')
	relations = process_lexicon({}, visual_genome_dir+'/data/raw/relationship_types.json')
	attributes = process_lexicon({}, visual_genome_dir+'/data/raw/attribute_types.json')
	objects.update(process_alias_lexicon(objects, visual_genome_dir+'/data/raw/object_alias.txt', ['n']))
	relations.update(process_alias_lexicon(relations, visual_genome_dir+'/data/raw/relationship_alias.txt', ['v']))
	json.dump(objects, open(visual_genome_dir+'/data/preprocessed/object_types_expanded.json','w'), indent=1)
	json.dump(relations, open(visual_genome_dir+'/data/preprocessed/relationship_types_expanded.json','w'), indent=1)
	json.dump(attributes, open(visual_genome_dir+'/data/preprocessed/attribute_types_expanded.json','w'), indent=1)
else:
	objects = json.load(open(visual_genomd_dir+'/data/preprocessed/object_types_expanded.json'))
	relations = json.load(open(visual_genomd_dir+'/data/preprocessed/relationship_types_expanded.json'))
	attributes = json.load(open(visual_genomd_dir+'/data/preprocessed/attribute_types_expanded.json'))
synsets = json.load(open(visual_genome_dir+'/data/raw/synsets.json'))
def parse(segment, segment_pos, segment_desc):
	objects_in_segment = {}#set([])
	attributes_in_segment = {}#set([])
	relations_in_segment = {}#set([])		
	segment_desc = {w:w_desc for w, w_desc in zip(segment,segment_desc)}
	for w, w_pos in zip(segment, segment_pos):
		if w+'.n' in objects and w_pos=='NOUN':
			objects_in_segment[w] = w+'.n'
		if w+'.a' in attributes and (w_pos=='ADJ' or w_pos=='ADP'):
			attributes_in_segment[w] = w+'.a'
		#if w+'.n' in attributes and w_pos=='NOUN':
		#	attributes_in_segment[w] = w+'.n'
		if w+'.r' in attributes and (w_pos=='ADP' or w_pos=='ADJ'):
			attributes_in_segment[w] = w+'.r'
		if w+'.v' in relations and w_pos=='VERB':
			relations_in_segment[w] = w+'.v'
	intersecting_objects_attributes = set(objects_in_segment.keys()).intersection(set(attributes_in_segment.keys()))
	for e in intersecting_objects_attributes:
		if e in segment_desc and any([d in intersecting_objects_attributes for d in segment_desc[e]]):
			del objects_in_segment[e]
			print ('deleting ', e , 'from object')
			#for d in segment_desc[e]:
			#	if d in intersecting_objects_attributes and d in attributes_in_segment:
			#		del attributes_in_segment[d]
	intersecting_objects_relations =  set(objects_in_segment.keys()).intersection(set(relations_in_segment.keys()))
	for e in intersecting_objects_relations:
		if e in segment_desc and any([d in intersecting_objects_relations for d in segment_desc[e]]):
			del objects_in_segment[e]
			print ('deleting ', e , 'from object')
	for o in list(objects_in_segment.keys()):
		if o in attributes_in_segment:
			del objects_in_segment[o]
			print ('deleting ', e, 'from object')
	return objects_in_segment, attributes_in_segment, relations_in_segment
split = sys.argv[1]
if split not in ['train2014', 'val2014', 'test-dev2015']:
        raise Exception('Wrong Argument.. should be either of \'train2014\', \'val2014\', \'test-dev2015\'')

questions = json.load(open(vqa_dir+'/data/v2_OpenEnded_mscoco_'+split+'_questions.json'))['questions']	
data_to_dump = []
for q in questions:
	image_id = q['image_id']
	image_file = 'COCO_'+split+'_000000'+str(image_id)+'.jpg'
	image_path = vqa_dir+'/data/'+split+'/'
	masked_rcnn_labels = set([])
	q_id = q['question_id']
	q = q['question']
	orig_q = q
	q = q.replace('"','').replace('can you see','is').replace('can be seen','is').replace('do you see', 'is').replace('do you call','is').replace('would you call','is').replace('will you call','is').replace('will you name','is').replace('should you call','is').replace('kind of ','').replace('type of ','').replace(' in this image','').replace(' of this image','').replace(' in this picture','').replace(' of this picture','').replace(' in this photograph','').replace(' of this photograph','').replace(' in this photo','').replace(' of this photo','').strip()
	if q.endswith('called ?'):
		q = q.replace('called ?','?')
	if q.endswith('called?'):
		q = q.replace('called?','?')
	doc = nlp(q)
	all_desc = []
	q_pos = [token.pos_ for token in doc]
	q_lemma = [token.lemma_ for token in doc]
	q = [token.text for token in doc] 
	valid_q = True
	if q[0].lower()!=leading:
		valid_q = False
                #print ('Not a What type question', q)
		continue
	else:
		print ('\nQuery :', orig_q)
	for i,token in enumerate(doc):
		all_desc.append([d.lemma_ for d in token.subtree if d!=token])
	immediate_children = {token.text:token.children for token in doc}
	children_of_root = [immediate_children[token.text] for token in doc if token.dep_=='ROOT'][0]		
	first = None
	last = None
	for m in middle:
		if m in q:	
			first = q_lemma[1:q.index(m)]
			first_pos = q_pos[1:q.index(m)]
			first_desc = all_desc[1:q.index(m)]
			last = q_lemma[q.index(m)+1:]
			last_pos = q_pos[q.index(m)+1:]
			last_desc = all_desc[q.index(m)+1:]
			#print ('BreakDown: ', ' '.join(first), '-----',  ' '.join(last))
			objects_in_first = []
			attributes_in_first = []
			relations_in_first = []
			objects_in_last = []
			attributes_in_last = []
			relations_in_last = []	
			if len(first)>0:
				objects_in_first, attributes_in_first, relations_in_first = parse(first, first_pos, first_desc)
				for o in objects_in_first:
					objects_counter.update(objects[objects_in_first[o]])
				for a in attributes_in_first:
					attributes_counter.update(attributes[attributes_in_first[a]])
				for r in relations_in_first:
					relations_counter.update(relations[relations_in_first[r]])
				objects_in_first = set(objects_in_first.keys())
				attributes_in_first = set(attributes_in_first.keys())
				relations_in_first = set(relations_in_first.keys())
				#print ('FIRST PHRASE:  objs:', objects_in_first, ': attrs:', attributes_in_first, ': rels:', relations_in_first)			
			if len(last)>0:
				objects_in_last, attributes_in_last, relations_in_last = parse(last, last_pos, last_desc)
				for o in objects_in_last:
					objects_counter.update(objects[objects_in_last[o]])
				for a in attributes_in_last:
					attributes_counter.update(attributes[attributes_in_last[a]])
				for r in relations_in_last:
					relations_counter.update(relations[relations_in_last[r]])
				objects_in_last = set(objects_in_last.keys())
				attributes_in_last = set(attributes_in_last.keys())
				relations_in_last = set(relations_in_last.keys())		
				#print ('LAST PHRASE:  objs:', objects_in_last, ': attrs:', attributes_in_last, ': rels:', relations_in_last)
				target_object = set([])
				target_attribute = set([])
				if objects_in_first==0 and attributes_in_first==0 and relations_in_first==0:
					for c in children_of_root:
						if c in objects_in_last:
							objects_in_last.remove(c)
							target_object.add(c)
						if c in attributes_in_last:
							attributes_in_last.remove(c)
							target_attribute.add(c)
				else:
					target_object = objects_in_first
					target_attribute = attributes_in_first
				count =1
				program = []
				to_return = []
				for o in objects_in_last:
					program.append('Obj'+str(count)+' = Filter_Object(\''+o+'\')')
					count+=1
				obj_var_start = 1
				obj_var_end = count-1
				if len(objects_in_last)>1:
					if count-1==obj_var_start+1:
						program.append('Obj'+str(count)+' = Intersection([Obj'+str(obj_var_start)+',Obj'+str(count-1)+'])') 
					else:
						program.append('Obj'+str(count)+' = Intersection([Obj'+str(obj_var_start)+', ..., Obj'+str(count-1)+'])')	
					obj_var_end = count
					count+=1
				attr_var_start = count
				for a in attributes_in_last:
					program.append('Obj'+str(count)+' = Filter_Attribute(\''+a+'\', Obj'+str(count-1)+')')
					count+=1
				attr_var_end = count-1						
				'''if len(attributes_in_last)>1:
					program.append('Obj'+str(count)+' = Intersection([Obj'+str(attr_var_start)+', ..., Obj'+str(count-1)+'])')
					attr_var_end = count
					count+=1
				'''
				for r in relations_in_last:
					program.append('Obj'+str(count)+' = Filter_Relation(\''+r+'\', Obj'+str(count-1)+')')
					count+=1 
				#to_return = ['Obj'+str(count-1)]
				if len(target_attribute)>0 and len(target_object)>0:
					for a in target_attribute:
						program.append('Obj'+str(count)+' = Filter_Attribute(\''+a+'\', Obj'+str(count-1)+')')
						count += 1
					to_return = []
					for o in target_object:
						program.append('Obj'+str(count)+' = Find_Object(\''+o+'\', Obj'+str(count-1)+')')
						to_return.append('Obj'+str(count))
						count+=1
				if len(target_attribute)>0 and len(target_object)==0:
					to_return = []
					for a in target_attribute:
						program.append('Obj'+str(count)+' = Find_Attribute(\''+a+'\', Obj'+str(count-1)+')')
						to_return.append('Obj'+str(count))
						count+=1
				elif len(target_attribute)==0 and len(target_object)>0:
					to_return = []
					for o in target_object:
						program.append('Obj'+str(count)+' = Find_Object(\''+o+'\', Obj'+str(count-1)+')')		
						to_return.append('Obj'+str(count))
						count+=1
				elif len(target_attribute)==0 and len(target_object)==0:
					to_return = []
					program.append('Obj'+str(count)+' = Find_Object(Obj'+str(count-1)+')')
					to_return.append('Obj'+str(count))
					count+=1
				for p in program:
					print ('  '+p)
				if len(program)>0:
					program.append('  Return '+', '.join(to_return))
					print ('  Return '+', '.join(to_return))
				d = {'question':' '.join(q), 'masked_rcnn_labels':list(masked_rcnn_labels), 'program':program, 'question_id':q_id, 'image_id':image_id}
				if valid_q:
					data_to_dump.append(d)
					
			break
json.dump(data_to_dump, open(vqa_dir+'/data/rule_based_program_for_question'+split+'.json','w'), indent=1)
pkl.dump(objects_counter, open(vqa_dir+'/objects_counter_'+split+'.pkl','wb'))
pkl.dump(attributes_counter, open(vqa_dir+'/attributes_counter_'+split+'.pkl','wb'))
pkl.dump(relations_counter, open(vqa_dir+'/relations_counter_'+split+'.pkl','wb'))
