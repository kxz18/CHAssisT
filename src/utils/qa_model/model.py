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
        padded_res = rnn.pad_packed_sequence(res, batch_first=self.batch_first)[0]  # (res, lengths)
        return padded_res, new_hid


class SingleTransformer(nn.Module):
    """lstm results of question or answer solely"""

    def __init__(self, vocab_size, embed_size, nhead, batch_first=True):
        """params
        """
        super(SingleTransformer, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        encoder_layer = nn.TransformerEncoderLayer(d_model=embed_size, nhead=nhead)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=3)
        self.batch_first = batch_first

    def forward(self, text):
        """forward"""
        embedded = self.embedding(text)     # [batch, seq, embed]
        res = self.transformer_encoder(embedded)
        return res


class AttentiveLSTM(nn.Module):
    """question answering model of attentive lstm"""
    
    def __init__(self, vocab_size, embed_size, hidden_size):
        """params:
            """
        super(AttentiveLSTM, self).__init__()
        #self.question_encoder = SingleLSTM(vocab_size, embed_size, hidden_size)
        #self.answer_encoder = SingleLSTM(vocab_size, embed_size, hidden_size)
        self.question_encoder = SingleTransformer(vocab_size, embed_size, 4)
        self.answer_encoder = SingleTransformer(vocab_size, embed_size, 4)
        #self.ave_pooling = nn.AvgPool2d((seq_len, 1), stride=1)
        self.softmax = nn.Softmax(dim=-1)
        self.dropout = nn.Dropout(0.2)
        self.hidden_size = hidden_size
        self.out_size = embed_size     # 2*hidden_size for biLSTM, embed_size for transformer
        # attentive part
        self.w_am = nn.Linear(self.out_size, self.out_size)
        self.w_qm = nn.Linear(self.out_size, self.out_size)
        self.w_ms = nn.Linear(self.out_size, 1)
        # linear transformation for question embedding when calculating attention
        self.w = nn.Linear(self.out_size, self.out_size);
        # cos
        self.cos = nn.CosineSimilarity(dim=-1)

    def forward(self, question, answer, len_q, len_a, hidden_q, hidden_a):
        """forward"""
        # lstm encoder
        #embed_q, _ = self.question_encoder(question, len_q, hidden_q)   # [batch, seq, hid]
        #embed_a, _ = self.answer_encoder(answer, len_a, hidden_a)
        # transformer encoder
        embed_q = self.question_encoder(question)    # [batch, seq, hid]
        embed_a = self.answer_encoder(answer)
        # paddings do not matter in avgpool as unitization is applied in dot
        final_embed_q = F.max_pool2d(embed_q, (embed_q.shape[1], 1), stride=1)   # [batch, 1, hid]
        #weights = embed_a.bmm(final_embed_q.transpose(1, 2))   # [batch, seq, 1]
        weights = embed_a.bmm(self.w(final_embed_q).transpose(1, 2))   # [batch, seq, 1]
        weights = self.softmax(weights.transpose(1, 2))     # [batch, 1, seq]
        final_embed_a = weights.bmm(embed_a)    # [batch, 1, hid]
        #m_aq = self.w_am(embed_a) + self.w_qm(final_embed_q)    # [batch, seq, hid]
        #s_aq = self.w_ms(torch.tanh(m_aq))   # [batch, seq, 1]
        #s_aq = self.softmax(s_aq.transpose(1, 2))   # [batch, 1, seq]
        #final_embed_a = s_aq.bmm(embed_a)     # [batch, 1, hid]
        # dropout
        final_embed_q = self.dropout(final_embed_q)
        final_embed_a = self.dropout(final_embed_a)
        # unitization
        #final_embed_q = F.normalize(final_embed_q, p=2, dim=-1)
        #final_embed_a = F.normalize(final_embed_a, p=2, dim=-1)
        # dot
        #cosine = final_embed_q.bmm(final_embed_a.transpose(1, 2))   # [batch, 1, 1]
        cosine = self.cos(final_embed_q, final_embed_a)
        cosine = cosine.squeeze()
        #cosine = F.relu(cosine)
        #cosine = torch.sigmoid(cosine)
        #print('m_aq', m_aq)
        #print('s_aq', s_aq)
        #print('cosine', cosine)
        #if torch.max(torch.isnan(cosine)).item():
        #    print('question', question)
        #    print('answer', answer)
        #    for param in self.parameters():
        #        print('param', param)
        return cosine

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
