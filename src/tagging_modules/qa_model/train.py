#!/usr/bin/python
# -*- coding:utf-8 -*-
"""training"""
import time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from model import AttentiveLSTM
from dataloader import DataLoader, flush_print
USE_CUDA = torch.cuda.is_available()
DEVICE = torch.device('cuda' if USE_CUDA else 'cpu')
GRAD_CLIP = 5.0
if USE_CUDA:
    torch.cuda.set_device(7)

    
def test(model, data_loader, limit = 0.8):
    """get test data of model"""
    model.eval()
    answer_sims = []
    fake_sims = []
    correct = 0
    all_cnt = 0
    with torch.no_grad():
        for batch in data_loader.batch_iter():
            batch_size = batch[0][0].shape[0]
            all_cnt += batch_size * (len(batch) - 1)
            hidden = model.init_hidden(batch_size)
            hidden_q = model.repackage_hidden(hidden, device=DEVICE)
            hidden_a = model.repackage_hidden(hidden, device=DEVICE)
            questions, len_q = batch[0]
            answers, len_a = batch[1]
            questions = questions.to(DEVICE)
            answers = answers.to(DEVICE)
            len_q = len_q.to(DEVICE)
            lan_a = len_a.to(DEVICE)
            output, _, _ = model(questions, answers, len_q, len_a, hidden_q, hidden_a)
            fake_answer_sims = []
            for fake_answer_data in batch[2:]:
                hidden_q = model.repackage_hidden(hidden, device=DEVICE)
                hidden_a = model.repackage_hidden(hidden, device=DEVICE)
                fake_answer, len_a = fake_answer_data
                fake_answer = fake_answer.to(DEVICE)
                len_a = len_a.to(DEVICE)
                similarity, _, _ = model(questions, fake_answer, len_q, len_a, hidden_q, hidden_a)
                fake_answer_sims.append(similarity.unsqueeze(0))
            fake_answer_max_sim = torch.max(torch.cat(fake_answer_sims, 0), dim=0).values
            answer_sims.append(torch.mean(output).item())
            fake_sims.append(torch.mean(torch.cat(fake_answer_sims, 0)).item())
            correct += torch.sum(output >= limit).item() + torch.sum(fake_answer_max_sim < limit).item()
            
    model.train()
    return correct / all_cnt, np.mean(answer_sims), np.mean(fake_sims)
    
def evaluate(model, data_loader):
    """get loss on validation or test set"""
    model.eval()
    epoch_losses = []
    loss_fn = nn.HingeEmbeddingLoss(margin=0.2)
    with torch.no_grad():
        for batch in data_loader.batch_iter():
            batch_size = batch[0][0].shape[0]
            hidden = model.init_hidden(batch_size)
            hidden_q = model.repackage_hidden(hidden, device=DEVICE)
            hidden_a = model.repackage_hidden(hidden, device=DEVICE)
            questions, len_q = batch[0]
            answers, len_a = batch[1]
            questions = questions.to(DEVICE)
            answers = answers.to(DEVICE)
            len_q = len_q.to(DEVICE)
            lan_a = len_a.to(DEVICE)
            output, _, _ = model(questions, answers, len_q, len_a, hidden_q, hidden_a)
            fake_answer_sims = []
            for fake_answer_data in batch[2:]:
                hidden_q = model.repackage_hidden(hidden, device=DEVICE)
                hidden_a = model.repackage_hidden(hidden, device=DEVICE)
                fake_answer, len_a = fake_answer_data
                fake_answer = fake_answer.to(DEVICE)
                len_a = len_a.to(DEVICE)
                similarity, _, _ = model(questions, fake_answer, len_q, len_a, hidden_q, hidden_a)
                fake_answer_sims.append(similarity.unsqueeze(0))
            fake_answer_max_sim = torch.max(torch.cat(fake_answer_sims, 0), dim=0).values
            loss = loss_fn(torch.cat((output, fake_answer_max_sim)),
                           torch.Tensor([-1 for _ in output] + [1 for _ in fake_answer_max_sim]).to(DEVICE))

            epoch_losses.append(loss.item())
    model.train()
    return np.mean(epoch_losses)
    

def train(model, target, train_data_loader, valid_data_loader, epoch, lr, _continue):
    
    """training"""
    if _continue:
        try:
            model.load_state_dict(torch.load(target))
            flush_print('model loaded, continue training')
        except Exception as error:
            flush_print(f'failed to load model: {error}, contruct new model')
    model = model.to(DEVICE)
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    all_losses = []
    min_loss = 10000
    loss_fn = nn.HingeEmbeddingLoss(margin=0.2)

    for e in range(epoch):
        epoch_losses = []
        flush_print(f'epoch {e} starts')
        start = time.time()
        batch_num = 0
        for batch in train_data_loader.batch_iter():
            batch_num += 1
            batch_size = batch[0][0].shape[0]
            hidden = model.init_hidden(batch_size)
            hidden_q = model.repackage_hidden(hidden, device=DEVICE)
            hidden_a = model.repackage_hidden(hidden, device=DEVICE)
            questions, len_q = batch[0]
            answers, len_a = batch[1]
            questions = questions.to(DEVICE)
            answers = answers.to(DEVICE)
            len_q = len_q.to(DEVICE)
            lan_a = len_a.to(DEVICE)
            output, _, _ = model(questions, answers, len_q, len_a, hidden_q, hidden_a)
            fake_answer_sims = []
            for fake_answer_data in batch[2:]:
                hidden_q = model.repackage_hidden(hidden, device=DEVICE)
                hidden_a = model.repackage_hidden(hidden, device=DEVICE)
                fake_answer, len_a = fake_answer_data
                fake_answer = fake_answer.to(DEVICE)
                len_a = len_a.to(DEVICE)
                similarity, _, _ = model(questions, fake_answer, len_q, len_a, hidden_q, hidden_a)
                fake_answer_sims.append(similarity.unsqueeze(0))
            fake_answer_max_sim = torch.max(torch.cat(fake_answer_sims, 0), dim=0).values
            loss = loss_fn(torch.cat((output, fake_answer_max_sim)),
                           torch.Tensor([-1 for _ in output] + [1 for _ in fake_answer_max_sim]).to(DEVICE))
            
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
            optimizer.step()
            
            epoch_losses.append(loss.item())
            if batch_num % 100 == 0:
                flush_print(np.mean(epoch_losses[-30:]))
                valid_loss = evaluate(model, valid_data_loader)
                if valid_loss <= min_loss:
                    min_loss = valid_loss
                    torch.save(model.state_dict(), target)
                    flush_print('best model saved')
            
        all_losses.append(np.mean(epoch_losses))
        valid_loss = evaluate(model, valid_data_loader)
        accu, avg_answer, avg_fake = test(model, test_set, limit = 0.8)
        end = time.time()
        flush_print(f'epoch: {e}, train loss: {all_losses[-1]}, valid loss: {valid_loss}, elapsed: {end - start} s')
        flush_print(f'on test set: accu: {accu}, average answer similarity: {avg_ansewr}, fake: {avg_fake}')
        
        # save model
        if valid_loss <= min_loss:
            min_loss = valid_loss
            torch.save(model.state_dict(), target)
            flush_print('best model saved')
            

def main():
    train_set = DataLoader('../baike/baike_qa_train_processed.json',
                           vocab_size=40000, seq_len_q=80, seq_len_a=100,\
                           batch_size=32, vocab_path="vocab.pkl", shuffle=True,
                           num_workers=4, nohup=False)
    valid_set = DataLoader('../baike/baike_qa_valid_processed.json',
                           vocab_size=40000, seq_len_q=80, seq_len_a=100,\
                           batch_size=32, vocab_path="vocab.pkl", shuffle=True,
                           num_workers=4, nohup=False)
    test_set = DataLoader('../baike/baike_qa_test_processed.json',
                       vocab_size=40000, seq_len_q=80, seq_len_a=200,\
                       batch_size=64, vocab_path="vocab.pkl", shuffle=True,
                       num_workers=4, nohup=False)
    model = AttentiveLSTM(valid_set.get_vocab_size(), embed_size=300, hidden_size=512)
    target = 'test_model.param'
    train(model, target, train_set, valid_set, epoch=20, lr=1e-3)


if __name__ == '__main__':
    main()

