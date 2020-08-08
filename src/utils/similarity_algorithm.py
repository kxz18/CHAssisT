#!/usr/bin/python
# -*- coding:utf-8 -*-
"""algorithms of similarity calculating between question and answer"""
from collections import defaultdict
from math import sqrt
# import pickle
# import jieba_fast as jieba
# import torch
# from utils.qa_model.model import AttentiveLSTM
# from utils.qa_model.dataloader import UNK
# USE_CUDA = torch.cuda.is_available()
# DEVICE = torch.device('cuda' if USE_CUDA else 'cpu')
# if USE_CUDA:
#     torch.cuda.set_device(7)
# 
# 
# def deep_learning_similarity(question, answer,
#                              model_path='utils/qa_model/test_model.param',
#                              vocab_path='utils/qa_model/vocab.pkl'):
#     """deep learning based question-answering similarity calculation"""
#     with open(vocab_path, 'rb') as fin:
#         vocab = pickle.load(fin)
#     model = AttentiveLSTM(len(vocab.idx_to_word), embed_size=300, hidden_size=512)
#     model.load_state_dict(torch.load(model_path))
#     model = model.to(DEVICE)
#     model.eval()
#     encoded_question = [vocab.word_to_idx.get(word, vocab.word_to_idx[UNK])
#                         for word in jieba.cut(question)]
#     encoded_answer = [vocab.word_to_idx.get(word, vocab.word_to_idx[UNK])
#                       for word in jieba.cut(answer)]
#     question_tensor = torch.Tensor(encoded_question).long().to(DEVICE)
#     answer_tensor = torch.Tensor(encoded_answer).long().to(DEVICE)
#     hidden = model.init_hidden(1)
#     hidden_q = model.repackage_hidden(hidden, device=DEVICE)
#     hidden_a = model.repackage_hidden(hidden, device=DEVICE)
#     output, _, _ = model(question_tensor.unsqueeze(0),
#                          answer_tensor.unsqueeze(0),
#                          [len(encoded_question)], [len(encoded_answer)],
#                          hidden_q, hidden_a)
#     return output.squeeze().item()


def frequency_cosine_similarity(text1, text2):
    """compare the cosine similarity between two texts.
    frequency-based word embedding"""

    # count frequency of characters
    counter1 = defaultdict(lambda: 0)
    counter2 = defaultdict(lambda: 0)
    for char in text1:
        counter1[char] += 1
    for char in text2:
        counter2[char] += 1

    # vectorize and dot
    all_char = set(list(counter1.keys()) + list(counter2.keys()))
    len1_sqr = 0
    len2_sqr = 0
    dot = 0     # dot result of two vectors
    for char in all_char:
        dot += counter1[char] * counter2[char]
        len1_sqr += counter1[char] * counter1[char]
        len2_sqr += counter2[char] * counter2[char]

    # cosine similarity
    return dot / sqrt(len1_sqr * len2_sqr)
