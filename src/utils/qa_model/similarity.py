#!/usr/bin/python
# -*- coding:utf-8 -*-
import pickle
import jieba_fast as jieba
import torch
from utils.qa_model.model import AttentiveLSTM
from utils.qa_model.dataloader import UNK
from utils.similarity_algorithm import *
USE_CUDA = torch.cuda.is_available()
DEVICE = torch.device('cuda' if USE_CUDA else 'cpu')
if USE_CUDA:
    torch.cuda.set_device(7)
PATH = 'src/utils/qa_model/insuranceqa/'


def similarity(question, answer, model_path=PATH + 'test_model.param',
               vocab_path=PATH + 'vocab.pkl'):
    with open(vocab_path, 'rb') as fin:
        vocab = pickle.load(fin)
    model = AttentiveLSTM(len(vocab.idx_to_word), embed_size=100, hidden_size=141)
    model.load_state_dict(torch.load(model_path))
    model = model.to(DEVICE)
    model.eval()
    encoded_question = [vocab.word_to_idx.get(word, vocab.word_to_idx[UNK])
                        for word in jieba.cut(question)]
    encoded_answer = [vocab.word_to_idx.get(word, vocab.word_to_idx[UNK])
                        for word in jieba.cut(answer)]
    question_tensor = torch.Tensor(encoded_question).long().to(DEVICE)
    answer_tensor = torch.Tensor(encoded_answer).long().to(DEVICE)
    hidden = model.init_hidden(1)
    hidden_q = model.repackage_hidden(hidden, device=DEVICE)
    hidden_a = model.repackage_hidden(hidden, device=DEVICE)
    output = model(question_tensor.unsqueeze(0), 
                         answer_tensor.unsqueeze(0),
                         [len(encoded_question)], [len(encoded_answer)],
                         hidden_q, hidden_a)
    return output.squeeze().item()


def main():
    questions = ['今天几点开会？', '今天几点开会？',
                 '我车停哪？', '我车停哪？',
                 '今天有游泳活动么？',
                 '线性代数考试在哪个教室？',
                 '听说我们最近要停水么？']
    answers = ['开会时间是9:00', '开会时间',
               '停车位置', '那幢大楼门口',
               '爬山在山脚集合',
               '考试地点',
               '停水通知']
    for question, answer in zip(questions, answers):
        sim = similarity(question, answer)
        print(question, answer)
        print(sim)
        print(word_embedding_similarity(question, answer))
        print(fusion_similarity(question, answer))

if __name__ == '__main__':
    main()
