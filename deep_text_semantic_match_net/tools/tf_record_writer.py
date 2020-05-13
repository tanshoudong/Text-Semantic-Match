#coding=utf-8
from collections import Counter
import logging
import numpy
import time
import sys
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')
import tensorflow as tf


def int_feature(v):
    """
    int feature
    """
    return tf.train.Feature(int64_list=tf.train.Int64List(value=v))


def write_data_to_tf(filename, func, func_args, writer):
    """
    writes tf records, write data
    每行(一个样本)作为一个examples
    """
    with open(filename) as fin_data:
        for line in fin_data:
            example = func(line, func_args)
            if not example:
                continue
            writer.write(example.SerializeToString())


def parse_text_match_pointwise_pad_data(line, func_args):
    """
    pointwise parse
    """
    seq_len = func_args[0]
    pad_id = func_args[1]
    # left_ids \t right_ids \t label
    group = line.strip().split("\t")
    if len(group) != 3:
        logging.warning(
            "the line not conform to format(left_ids, right_ids, label)")
        return
    label = [0, 0]
    all_ids = []
    for i in [0, 1]:
        tmp_ids = [int(t) for t in group[i].strip().split(" ")]
        if len(tmp_ids) < seq_len:
            pad_len = seq_len - len(tmp_ids)
            tmp_ids = tmp_ids + [pad_id] * pad_len
        all_ids.append(tmp_ids[:seq_len])
    label[int(group[2])] = 1
    example = tf.train.Example(features=tf.train.Features(
        feature={"label": int_feature(label),
                 "left": int_feature(all_ids[0]),
                 "right": int_feature(all_ids[1])}))
    return example


def parse_text_match_pairwise_pad_data(line, func_args):
    """
    pairwise parse
    """
    seq_len = func_args[0]
    pad_id = func_args[1]
    # query_terms\t postitle_terms\t negtitle_terms
    group = line.strip().split("\t")
    if len(group) != 3:
        logging.warning(
            "the line not conform to format(query_terms, postitle_terms, negtitle_terms)")
        return
    all_ids = []
    for i in [0, 1, 2]:
        tmp_ids = [int(t) for t in group[i].strip().split(" ")]
        if len(tmp_ids) < seq_len:
            pad_len = seq_len - len(tmp_ids)
            tmp_ids = tmp_ids + [pad_id] * pad_len
        all_ids.append(tmp_ids[:seq_len])
    example = tf.train.Example(features=tf.train.Features(
        feature={"left": int_feature(all_ids[0]),
                 "pos_right": int_feature(all_ids[1]),
                 "neg_right": int_feature(all_ids[2])}))
    return example


def usage():
    """
    usage
    """
    print(sys.argv[0], "options")
    print("options")
    print("\ttype: data type include pointwise or pairwise")
    print("\tinputfile: input file path")
    print("\trecordfile: output recorf file")
    print("\tpad_id: pad id")
    print("\tmax_len: sequence max length")


if __name__ == "__main__":
    # if len(sys.argv) != 6:
    #     usage()
    #     sys.exit(-1)
    shell="./tools/tf_record_writer.py pointwise ../data/test_pointwise_data ../data/convert_test_pointwise_data 0 32".split(" ")
    sys.argv=shell

    input_data_format = sys.argv[1]
    filename = sys.argv[2]
    tfrecord_name = sys.argv[3]
    pad_id = int(sys.argv[4])
    max_len = int(sys.argv[5])
    data_format_func = {"pointwise": parse_text_match_pointwise_pad_data,
                        "pairwise": parse_text_match_pairwise_pad_data}
    if input_data_format in data_format_func:
        using_func = data_format_func[input_data_format]
    else:
        logging.error("data_format not supported")
        sys.exit(1)
    #以TFRecord的形式存储文件，存取简单，快速，尤其对大型训练数据很友好
    local_writer = tf.python_io.TFRecordWriter(tfrecord_name)
    write_data_to_tf(filename, using_func, [max_len, pad_id], local_writer)
    local_writer.close()
