
export CUDA_VISIBLE_DEVICES=2

# RPATH=/mnt/a99/d0/varshiths/MVD
# the code base is written assuming the files are run from parent directory
RPATH=$(dirname `pwd`)
export PYTHONPATH=$PYTHONPATH:$RPATH
# export PYTHONPATH=$PYTHONPATH:$RPATH/slim
# export PATH=/opt/cuda-9.2/bin${PATH:+:${PATH}}
# export LD_LIBRARY_PATH=/opt/cuda-9.2/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

python2 demo.py
# python2 builders/model_builder_test.py
