#!/usr/bin/python
# -*- coding:utf-8 -*-
from collections import Counter, defaultdict
import re
import pickle
import json
import random
import sys
import time
from tqdm import tqdm
import numpy as np
import torch
import torch.utils.data as tud
import torch.nn.utils.rnn as rnn

UNK = '<unk>'
PAD = '<pad>'

def flush_print(s):
    print(s)
    sys.stdout.flush()
    
class Vocab:
    """vocabulary"""
    def __init__(self):
        """init"""
        self.word_to_idx = defaultdict(int)
        self.idx_to_word = []
    
    @classmethod
    def get_vocab(self, lines, vocab_path, max_size=-1,
            tokenizer=lambda x: re.split(r'\s+', x), nohup=False):
        try:
            if not nohup:
                flush_print(f'trying to load vocabulary from {vocab_path}')
            with open(vocab_path, 'rb') as fin:
                return pickle.load(fin)
        except Exception as error:
            if not nohup:
                flush_print(f'load vocabulary error: {error}, start creating')
        vocab = Vocab()
        united_text = ' '.join(lines)
        counter = Counter(re.split(r'\s+', united_text))  # split to words
        length = 0
        if max_size < 0:
            counter = dict(counter)
        else:
            counter = dict(counter.most_common(max_size))
        counter[UNK] = 0
        counter[PAD] = 0
        vocab.idx_to_word = [word for word in counter.keys()]
        vocab.word_to_idx = {word: i for i, word in enumerate(vocab.idx_to_word)}
        with open(vocab_path, 'wb') as fout:
            pickle.dump(vocab, fout)
        if not nohup:
            flush_print(f'vocabulary saved to {vocab_path}')
        return vocab
    
    
class WordEmbeddingDataset(tud.Dataset):
    '''
    class of dataset, turn word into id
    '''
    def __init__(self, questions, answers, word_to_idx, idx_to_word, max_len_q, max_len_a, fake_answer_num):
        super(WordEmbeddingDataset, self).__init__()
        self.questions_encoded = []
        self.questions_lens = []
        self.answers_encoded = []
        self.answers_lens = []
        for question, answer in zip(questions, answers):
            question = re.split(r'\s+', question)
            answer = re.split(r'\s+', answer)
            if len(question) <= 0 or len(answer) <= 0:
                continue
            
            encoded_q = [word_to_idx.get(word, word_to_idx[UNK]) for word in question] +\
                        [word_to_idx[PAD] for i in range(len(question), max_len_q)]
            self.questions_encoded.append(encoded_q[0:max_len_q])
            self.questions_lens.append(len(question) if len(question) < max_len_q else max_len_q)  
            
            encoded_a = [word_to_idx.get(word, word_to_idx[UNK]) for word in answer] +\
                        [word_to_idx[PAD] for i in range(len(answer), max_len_a)]
            self.answers_encoded.append(encoded_a[0:max_len_a])
            self.answers_lens.append(len(answer) if len(answer) < max_len_q else max_len_a)
        self.word_to_idx = word_to_idx
        self.idx_to_word = idx_to_word
        self.fake_answer_num = fake_answer_num

    def __len__(self):
        return len(self.questions_encoded)

    def __getitem__(self, idx):
        question = torch.Tensor(self.questions_encoded[idx]).long()
        answer = torch.Tensor(self.answers_encoded[idx]).long()
        len_q = self.questions_lens[idx]
        len_a = self.answers_lens[idx]
        # get fake answers
        fake_answers_idx = random.sample(range(0, self.__len__() - 1), self.fake_answer_num)
        # revise fake_answers_idx
        fake_answers_idx = [_idx if _idx < idx else _idx + 1 for _idx in fake_answers_idx]
        return_data = [(question, len_q), (answer, len_a)] +\
                       [(torch.Tensor(self.answers_encoded[_idx]).long(), self.answers_lens[_idx])\
                       for _idx in fake_answers_idx]
        return tuple(return_data)


class DataLoader:
    '''
    class of dataloader
    '''
    def __init__(self, file_path, vocab_size, seq_len_q, seq_len_a, batch_size, fake_answer_num=5,\
            vocab_path="vocab.pkl", shuffle=True, num_workers=4, nohup=False):
        self.vocab_size = vocab_size
        self.vocab = {}
        self.word_to_idx = {}
        self.idx_to_word = []
        self.dataloader = None
        self.seq_len_q = seq_len_q
        self.seq_len_a = seq_len_a
        self.fake_answer_num = fake_answer_num
        self.nohup = nohup
        self.set_data(file_path, vocab_path, batch_size, shuffle=shuffle, num_workers=num_workers)

    def set_data(self, file_path, vocab_path, batch_size, shuffle=False, num_workers=4):
        '''change data set'''
        if not self.nohup:
            flush_print(f'loading text from {file_path}')
        time_start = time.time()
        with open(file_path, 'r') as fin:
            text = fin.readlines()
        if not self.nohup:
            flush_print(f'data loaded, elapsed: {time.time()-time_start} s')
            flush_print('start processing ...')

        time_start = time.time()
        questions = []
        answers = []
        for line in text:
            data = json.loads(line)
            questions.append(data['question'])
            answers.append(data['answer'])
        # prepare text for vocabulary building
        if not self.nohup:
            flush_print(f'processed, elapsed: {time.time()-time_start} s')
            flush_print('start generating vocabulary')
        
        time_start = time.time()
        self.vocab = Vocab.get_vocab(questions + answers, vocab_path, self.vocab_size)
        self.word_to_idx = self.vocab.word_to_idx
        self.idx_to_word = self.vocab.idx_to_word
        # in case vocabulary is reloaded
        self.vocab_size = len(self.idx_to_word)
        if not self.nohup:
            flush_print(f'vocabulary generated, elapsed: {time.time()-time_start} s')
            flush_print('creating dataset ...')
        time_start = time.time()
        dataset = WordEmbeddingDataset(questions, answers, self.word_to_idx,\
                self.idx_to_word, self.seq_len_q, self.seq_len_a, self.fake_answer_num)
        self.dataloader = tud.DataLoader(dataset, batch_size=batch_size,\
                     shuffle=shuffle, num_workers=num_workers)
        self.batches = iter(self.dataloader)
        if not self.nohup:
            flush_print(f'batches loaded, elapsed: {time.time() - time_start} s')

    def batch_iter(self):
        return iter(self.dataloader)

    def get_vocab_size(self):
        '''
        return size of vocabulary
        '''
        return len(self.idx_to_word)

    def get_word(self, idx):
        '''
        turn id to word
        '''
        return self.idx_to_word[idx]
    
    def get_idx(self, word):
        '''
        turn word to id
        '''
        return self.word_to_idx[word]

    def batch_num(self):
        '''
        return batch num
        '''
        return len(self.dataloader)

    def data_num(self):
        """return number of data"""
        return self.dataloader.dataset.__len__()
