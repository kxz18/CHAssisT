#!/usr/bin/python
# -*- coding:utf-8 -*-
"""deep learning model of question and answering"""
import torch
import torch.nn as nn
import torch.nn.utils.rnn as rnn
import torch.nn.functional as F

USE_CUDA = torch.cuda.is_available()
DEVICE = torch.device('cuda' if USE_CUDA else 'cpu')


class SingleLSTM(nn.Module):
    """lstm results of question or answer solely"""

    def __init__(self, vocab_size, embed_size, hidden_size, batch_first=True):
        """params
        """
        super(SingleLSTM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.lstm = nn.LSTM(embed_size, hidden_size,
                            bidirectional=True,
                            batch_first=batch_first)
        self.batch_first = batch_first

    def forward(self, text, lengths, hidden):
        """forward"""
        embedded = self.embedding(text)     # [batch, seq, embed]
        embed_packed = rnn.pack_padded_sequence(embedded, lengths,
                                                batch_first=self.batch_first,
                                                enforce_sorted=False)
        res, new_hid = self.lstm(embed_packed, hidden)
        padded_res = rnn.pad_packed_sequence(res, batch_first=True)[0]  # (res, lengths)
        return padded_res, new_hid


class AttentiveLSTM(nn.Module):
    """question answering model of attentive lstm"""
    
    def __init__(self, vocab_size, embed_size, hidden_size):
        """params:
            """
        super(AttentiveLSTM, self).__init__()
        self.question_lstm = SingleLSTM(vocab_size, embed_size, hidden_size)
        self.answer_lstm = SingleLSTM(vocab_size, embed_size, hidden_size)
        #self.ave_pooling = nn.AvgPool2d((seq_len, 1), stride=1)
        self.softmax = nn.Softmax(dim=-1)
        self.dropout = nn.Dropout(0.1)
        self.hidden_size = hidden_size

    def forward(self, question, answer, len_q, len_a, hidden_q, hidden_a):
        """forward"""
        embed_q, new_hid_q = self.question_lstm(question, len_q, hidden_q)   # [batch, seq, hid]
        embed_a, new_hid_a = self.answer_lstm(answer, len_a, hidden_a)
        # paddings do not matter in avgpool as unitization is applied in dot
        final_embed_q = F.avg_pool2d(embed_a, (embed_a.shape[1], 1), stride=1)   # [batch, 1, hid]
        weights = embed_a.bmm(final_embed_q.transpose(1, 2))   # [batch, seq, 1]
        weights = self.softmax(weights.transpose(1, 2))     # [batch, 1, seq]
        final_embed_a = weights.bmm(embed_a)    # [batch, 1, hid]
        # unitization
        final_embed_q = F.normalize(final_embed_q, p=2, dim=-1)
        final_embed_a = F.normalize(final_embed_a, p=2, dim=-1)
        # dropout
        final_embed_q = self.dropout(final_embed_q)
        final_embed_a = self.dropout(final_embed_a)
        # dot
        cosine = final_embed_q.bmm(final_embed_a.transpose(1, 2))   # [batch, 1, 1]
        cosine = cosine.squeeze()
        return cosine, new_hid_q, new_hid_a

    def init_hidden(self, batch_size, requires_grad=True):
        """init hidden layer with all zero"""
        weight = next(self.parameters())
        # for lstm, hidden and cell states are needed
        return (weight.new_zeros((2, batch_size, self.hidden_size), requires_grad=requires_grad),
              weight.new_zeros((2, batch_size, self.hidden_size), requires_grad=requires_grad))

    def repackage_hidden(self, hidden, device):
        """cut connection of hidden with former calculation"""
        if isinstance(hidden, torch.Tensor):
            return hidden.detach().to(device)
        return tuple(self.repackage_hidden(v, device) for v in hidden)
