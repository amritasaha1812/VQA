import spacy
import json
import re
nlp = spacy.load('en_core_web_sm')
leading = 'What'.lower()
vqa_dir = '..'
split = sys.argv[1]
if split not in ['train2014', 'val2014', 'test-dev2015']:
        raise Exception('Wrong Argument.. should be either of \'train2014\', \'val2014\', \'test-dev2015\'') 
def remove_trailing_stopword(x):
	if len(x)==0:
		return x
	if x[-1].lower()!=leading and nlp.vocab[x[-1]].is_stop:
		if len(x)==1:
			return ''
		else:
			return remove_trailing_stopword(x[:-1])
	else:
		return x

def get_intersection(tokens, tokens_last):
	last_counter = 0
	last_last_counter = 0	
	for i in range(min([len(tokens), len(tokens_last)])):
		if tokens[i] == tokens_last[i]:
			last_counter=i+1
		else:
			break
	new_tail_noun_phrase = ' '.join(remove_trailing_stopword(tokens[last_counter:]))
	new_tail_noun_phrase_last = ' '.join(remove_trailing_stopword(tokens_last[last_counter:]))
	new_tokens = ' '.join(tokens[:last_counter])
	new_tokens_wo_stop = ' '.join(remove_trailing_stopword(tokens[:last_counter])).strip()
	if new_tokens_wo_stop.lower() != leading:
		new_tokens = new_tokens_wo_stop
	return new_tokens, new_tail_noun_phrase, new_tail_noun_phrase_last

questions = json.load(open(vqa_dir+'/data/v2_OpenEnded_mscoco_'+split+'_questions.json'))['questions']
l = []
for q in questions:
	q = q['question']
	orig_q = q
	q = q.replace('"','').replace('can you see','is').replace('can be seen','is').replace('do you see', 'is').replace('do you call','is').replace('would you call','is').replace('will you call','is').replace('will you name','is').replace('should you call','is').replace('kind of ','').replace('type of ','').replace(' in this image','').replace(' of this image','').replace(' in this picture','').replace(' of this picture','').replace(' in this photograph','').replace(' of this photograph','').replace(' in this photo','').replace(' of this photo','').strip()
	if q.endswith('called ?'):
		q = q.replace('called ?','?')
	if q.endswith('called?'):
		q = q.replace('called?','?')	
	q = q.split(' ')
	if q[0].lower()!=leading:
		continue
	q = re.sub('\s+', ' ', " ".join(q)).strip()
	l.append(q.replace('"','').strip().lower())
print ('Collected all '+leading+'...* questions')
l = list(set(l))
l.sort()
last_tokens = []
last_template = ''
last_tail_np = '                                             '
addtolist = []
template_clusters = {}
for i in range(len(l)):
	#print (l[i])
	tokens = [x.strip().lower() for x in l[i].replace("?","").strip().split(' ') if x.strip()!='?']
	if last_tokens is None:
		last_tokens = []
	curr_template, curr_tail_np, new_last_tail_np = get_intersection(tokens, last_tokens)
	if len(new_last_tail_np)<len(last_tail_np):
		last_template_to_print = ' '.join(last_tokens)+'   ('+curr_template + ' [[ '+new_last_tail_np+' ]])'
		if curr_template not in template_clusters:
			template_clusters[curr_template] = []
		template_clusters[curr_template].append(' '.join(last_tokens))
	else:
		last_template_to_print = ' '.join(last_tokens)+'   ('+last_template + ' [[ '+last_tail_np+' ]])'
		if last_template not in template_clusters:
			template_clusters[last_template] = []
		template_clusters[last_template].append(' '.join(last_tokens))
	addtolist.append(last_template_to_print)	
	print ('Added ::::',last_template_to_print)
	if i==len(l)-1:
		curr_template_to_print = ' '.join(tokens)+'   ('+last_template + ' [[ '+curr_tail_np+' ]])'
		if last_template not in template_clusters:
			template_clusters[last_template] = []
		template_clusters[last_template].append(' '.join(tokens))
		addtolist.append(curr_template_to_print)
		print ('Added ::::',curr_template_to_print)
	last_template = curr_template
	last_tail_np = curr_tail_np
	last_tokens = tokens
for k,v in template_clusters.items():
        template_clusters[k] = list(set(v))
json.dump(template_clusters, open(vqa_dir+'/data/'+leading+'_question_template_clusters.json','w'), indent=1)	
