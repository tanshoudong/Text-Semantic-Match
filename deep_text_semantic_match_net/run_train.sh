#!/usr/bin/env bash
#指定bash执行出错即停止
set -e # set -o errexit
#指定bash在执行过程中遇到未知变量即停止执行
set -u # set -o nounset
#set -o pipefail命令用于解决管道命令中子命令失败的情况，只要一个子命令失败，整个管道命令就失败，脚本就会终止执行。
set -o pipefail 

echo "convert train data"
python ./tools/tf_record_writer.py pointwise ./data/train_pointwise_data ./data/convert_train_pointwise_data 0 32
echo "convert test data"
python ./tools/tf_record_writer.py pointwise ./data/test_pointwise_data ./data/convert_test_pointwise_data 0 32
echo "convert data finish"

in_task_type='train'
in_task_conf='./examples/lstm-pointwise.json'
python tf_simnet.py \
		   --task $in_task_type \
		   --task_conf $in_task_conf

