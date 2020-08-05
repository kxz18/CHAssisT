#!/usr/bin/python
# -*- coding:utf-8 -*-
"""do preprocess of baike qa data"""
import json
import random
import jieba_fast as jieba


def preprocess(path, target, fake_num):
    """preprocess data to wanted format like:
    {'title': ..., 'answer': ..., 'fake_answer1' ... 'fake_answerk'},
    fake_answeri means the ith fake answer"""
    with open(path) as fin:
        lines = fin.readlines()
    questions = []
    answers = []
    for line in lines:
        json_data = json.loads(line)
        # get all questions and corresponding answers
        questions.append(' '.join(jieba.cut(json_data['title'])))
        answers.append(' '.join(jieba.cut(json_data['answer'])))
    # assign right answer and {fake_num} wrong answer
    revised_data = []
    for idx, question in enumerate(questions):
        right_answer = answers[idx]
        fake_answers_idx = random.sample(range(0, len(questions) - 1), fake_num)
        fake_answers = [answers[_idx] if _idx < idx else answers[_idx + 1]
                        for _idx in fake_answers_idx]
        data = {
            'question': question,
            'answer': right_answer,
        }
        for _idx, fake_answer in enumerate(fake_answers):
            data[f'fake_answer{_idx}'] = fake_answer
        revised_data.append(json.dumps(data, ensure_ascii=False))
    with open(target, 'w') as fout:
        fout.write('\n'.join(revised_data))


def split_set(path, target1, target2, ratio, shuffle=True):
    """split set with target2:raw = ratio
    params:
        path: raw data path
        target1: path of set1 splited from raw data
        target2: path of set2 splited from raw data
        ratio: target2:raw"""
    with open(path, 'r') as fin:
        lines = fin.readlines()
    if shuffle:
        random.shuffle(lines)
    split_point = int(len(lines) * (1 - ratio))
    set1 = lines[:split_point]
    set2 = lines[split_point:]
    with open(target1, 'w') as fout:
        fout.writelines(set1)  # already have \n
    with open(target2, 'w') as fout:
        fout.writelines(set2)


def main():
    """main entry"""
    prefix_path = './baike/'
    raw_train = 'baike_qa_train.json'
    raw_valid = 'baike_qa_valid.json'
    processed_train = 'baike_qa_train_processed.json'
    processed_valid = 'baike_qa_valid_processed.json'
    processed_test = 'baike_qa_test_processed.json'
    fake_num = 5
    split_set(prefix_path + raw_valid, prefix_path + processed_valid,
              prefix_path + processed_test, 0.3)
    print('finish spliting test set from valid set')
    raws = [prefix_path + path for path in [raw_train, processed_valid, processed_test]]
    targets = [prefix_path + path for path in [processed_train, processed_valid, processed_test]]
    for raw, target in zip(raws, targets):
        preprocess(raw, target, fake_num)
        print(f'finish preprocess {target}')

if __name__ == '__main__':
    main()
