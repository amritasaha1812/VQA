
export CUDA_VISIBLE_DEVICES=2

# RPATH=/mnt/a99/d0/varshiths/MVD
# the code base is written assuming the files are run from parent directory
RPATH=$(dirname `pwd`)
export PYTHONPATH=$PYTHONPATH:$RPATH
# export PYTHONPATH=$PYTHONPATH:$RPATH/slim
# export PATH=/opt/cuda-9.2/bin${PATH:+:${PATH}}
# export LD_LIBRARY_PATH=/opt/cuda-9.2/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

python dataset_tools/create_coco_tf_record.py \
	--include_masks False \
	--train_image_dir ../coco/train2014 \
	--val_image_dir ../coco/val2014 \
	--test_image_dir ../coco/test2015 \
	--train_annotations_file  \
	--val_annotations_file  \
	--testdev_annotations_file  \
	--output_dir data_records/coco/

python2 inference/infer_detections.py \
	--input_tfrecord_paths=/path/to/input/tfrecord1,/path/to/input/tfrecord2 \
	--output_tfrecord_path_prefix=/path/to/output/detections.tfrecord \
	--inference_graph=/faster_rcnn_inception_v2_coco_2018_01_28/frozen_inference_graph.pb
