#!/usr/bin/python
# -*- coding:utf-8 -*-
"""algorithms of similarity calculating between question and answer"""
import re
import time
from collections import defaultdict
from math import sqrt
import pickle
import jieba_fast as jieba
import torch
import numpy as np
from utils.qa_model.model import AttentiveLSTM
from utils.qa_model.dataloader import UNK
USE_CUDA = torch.cuda.is_available()
DEVICE = torch.device('cuda' if USE_CUDA else 'cpu')
if USE_CUDA:
    torch.cuda.set_device(7)
DATA_PATH = 'src/utils/qa_model/baike/'

def deep_learning_similarity(question, answer,
                             model_path=f'{DATA_PATH}test_model.param',
                             vocab_path=f'{DATA_PATH}vocab.pkl'):
    """deep learning based question-answering similarity calculation"""
    with open(vocab_path, 'rb') as fin:
        vocab = pickle.load(fin)
    model = AttentiveLSTM(len(vocab.idx_to_word), embed_size=300, hidden_size=512)
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
    output, _, _ = model(question_tensor.unsqueeze(0),
                         answer_tensor.unsqueeze(0),
                         [len(encoded_question)], [len(encoded_answer)],
                         hidden_q, hidden_a)
    print(question, answer, output.squeeze().item())
    return output.squeeze().item()


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


class WordEmbedding:
    """embedding of words(word2vec), singleton"""
    unk = '<unk>'
    _instance = None

    def __new__(cls):
        """singleton"""
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            print('word embedding table instance created')
            cls._instance.__singleton_init__()
        return cls._instance

    def __singleton_init__(self):
        """initialize"""
        print('loading word vectors...')
        start = time.time()
        file_path = 'src/utils/qa_model/word_vectors/sgns.zhihu.word'
        vocab, embedding_size = self.get_word2vec(file_path)
        self.vocab = vocab
        self.embedding_size = embedding_size
        print(f'word vectors loaded from {file_path}, elapsed {time.time() - start} s')

    def get_word2vec(self, word2vec_path):
        """load word vectors: <word> <vector>"""
        with open(word2vec_path, 'r') as fin:
            lines = fin.readlines()
        vocab = {}
        embedding_size = len(re.split(r'\s+', lines[-1].strip())) - 1  # 1 for the word
        for line in lines[1:]:
            splited_line = re.split(r'\s+', line.strip())
            vocab[splited_line[0]] = np.array(list(map(float, splited_line[1:])))
        vocab[self.unk] = np.zeros(embedding_size)
        return vocab, embedding_size

    def word2vec(self, word):
        """turn word to vector"""
        return self.vocab.get(word, self.vocab[self.unk])

def word_embedding_similarity(text1, text2):
    embedding = WordEmbedding()
    vec1 = np.mean([embedding.word2vec(word) for word in jieba.cut(text1)], axis=0)
    vec2 = np.mean([embedding.word2vec(word) for word in jieba.cut(text2)], axis=0)
    divider = sqrt(vec1.dot(vec1) * vec2.dot(vec2))
    res = vec1.dot(vec2) / divider
    if res == np.nan:
        return None
    return res


def fusion_similarity(text1, text2):
    """fusion of frequency similarity and word embeding similarity"""
    res1 = frequency_cosine_similarity(text1, text2)
    res2 = word_embedding_similarity(text1, text2)
    if res2 is None:
        return res1
    return (res1 + res2) / 2
