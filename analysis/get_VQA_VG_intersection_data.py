import json
vqa_train = json.load(open('v2_mscoco_train2014_annotations.json'))
vqa_valid = json.load(open('v2_mscoco_val2014_annotations.json'))
print ('Loaded data')
removed = 0
new_vqa_train = {'annotations':[]}
new_vqa_valid = {'annotations':[]}
for k,v in vqa_train.items():
	if k!='annotations':
		new_vqa_train[k] = v
for k,v in vqa_valid.items():
        if k!='annotations':
                new_vqa_valid[k] = v

for d in vqa_train['annotations'][:]:
	if d['image_id'] not in vg_data:
		removed +=1
		if removed %1000==0:
			print ('removed data',removed)
	else:
		new_vqa_train['annotations'].append(d)
for d in vqa_valid['annotations'][:]:
	if d['image_id'] not in vg_data:
		removed+=1
		if removed%1000==0:	
			print ('removed data', removed)
	else:
		new_vqa_valid['annotations'].append(d)		

print (len(new_vqa_train['annotations']))
print (len(new_vqa_valid['annotations']))
json.dump(new_vqa_train, open('v2_mscoco_train2014_ints_vg_annotations.json','w'), indent=1)
json.dump(new_vqa_valid, open('v2_mscoco_val2014_ints_vg_annotations.json','w'), indent=1)
