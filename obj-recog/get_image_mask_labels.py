from utils import label_map_util
PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
print type(category_index)
