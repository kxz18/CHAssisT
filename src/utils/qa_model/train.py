#!/usr/bin/python
# -*- coding:utf-8 -*-
"""training"""
import sys
import time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from utils.qa_model.model import AttentiveLSTM
from utils.qa_model.dataloader import DataLoader, flush_print
USE_CUDA = torch.cuda.is_available()
DEVICE = torch.device('cuda' if USE_CUDA else 'cpu')
GRAD_CLIP = 5.0
if USE_CUDA:
    torch.cuda.set_device(7)


def hinge_loss(cos1, cos2, margin=0.2):
    """max(0, margin - cos1 + cos2)"""
    raw = torch.mean(margin - cos1 + cos2)
    loss = torch.max(torch.Tensor([0]).to(DEVICE), raw)

    #loss_fn = nn.HingeEmbeddingLoss(margin=margin)
    #loss = loss_fn(torch.cat([cos1, cos2]), torch.Tensor(
    #    [-1 for _ in cos1] + [1 for _ in cos2]).to(DEVICE))

    #loss_fn = nn.MarginRankingLoss(margin=margin, reduction='sum')
    #loss = loss_fn(cos1, cos2, torch.Tensor([1 for _ in cos1]).to(DEVICE))

    #loss_fn = nn.BCELoss()
    #loss = loss_fn(torch.cat([cos1, cos2]),
    #               torch.Tensor([1 for _ in cos1] + [0 for _ in cos2]).to(DEVICE))
    return loss

    
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
            all_cnt += batch_size
            hidden = model.init_hidden(batch_size)
            hidden_q = model.repackage_hidden(hidden, device=DEVICE)
            hidden_a = model.repackage_hidden(hidden, device=DEVICE)
            questions, len_q = batch[0]
            answers, len_a = batch[1]
            questions = questions.to(DEVICE)
            answers = answers.to(DEVICE)
            len_q = len_q.to(DEVICE)
            lan_a = len_a.to(DEVICE)
            output = model(questions, answers, len_q, len_a, hidden_q, hidden_a)
            fake_answer_sims = []
            for fake_answer_data in batch[2:]:
                hidden_q = model.repackage_hidden(hidden, device=DEVICE)
                hidden_a = model.repackage_hidden(hidden, device=DEVICE)
                fake_answer, len_a = fake_answer_data
                fake_answer = fake_answer.to(DEVICE)
                len_a = len_a.to(DEVICE)
                similarity = model(questions, fake_answer, len_q, len_a, hidden_q, hidden_a)
                fake_answer_sims.append(similarity.unsqueeze(0))
            fake_answer_max_sim = torch.max(torch.cat(fake_answer_sims, 0), dim=0).values
            answer_sims.append(torch.mean(output).item())
            fake_sims.append(torch.mean(torch.cat(fake_answer_sims, 0)).item())
            #correct += torch.sum(output >= limit).item() +\
            #           torch.sum(fake_answer_max_sim < limit).item()
            correct += torch.sum(torch.max(
                        torch.cat([fake_answer_max_sim.unsqueeze(0),
                                   output.unsqueeze(0)], 0), dim=0)[1]).item()
            
    model.train()
    return correct / all_cnt, np.mean(answer_sims), np.mean(fake_sims)
    
def evaluate(model, data_loader):
    """get loss on validation or test set"""
    model.eval()
    epoch_losses = []
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
            output = model(questions, answers, len_q, len_a, hidden_q, hidden_a)
            fake_answer_sims = []
            for fake_answer_data in batch[2:]:
                hidden_q = model.repackage_hidden(hidden, device=DEVICE)
                hidden_a = model.repackage_hidden(hidden, device=DEVICE)
                fake_answer, len_a = fake_answer_data
                fake_answer = fake_answer.to(DEVICE)
                len_a = len_a.to(DEVICE)
                similarity = model(questions, fake_answer, len_q, len_a, hidden_q, hidden_a)
                fake_answer_sims.append(similarity.unsqueeze(0))
            fake_answer_max_sim = torch.max(torch.cat(fake_answer_sims, 0), dim=0)[0]
            # loss = loss_fn(output - fake_answer_max_sim,
            #                torch.Tensor([-1 for _ in output]).to(DEVICE))
            #loss = loss_fn(torch.cat((output, fake_answer_max_sim)),
            #               torch.Tensor([-1 for _ in output] + [1 for _ in fake_answer_max_sim]).to(DEVICE))
            loss = hinge_loss(output, fake_answer_max_sim)

            epoch_losses.append(loss.item())
    model.train()
    return np.mean(epoch_losses)
    

def train(model, target, train_data_loader, valid_data_loader,
          test_data_loader, epoch, lr, _continue):
    
    """training"""
    if _continue:
        try:
            model.load_state_dict(torch.load(target))
            flush_print('model loaded, continue training')
        except Exception as error:
            flush_print(f'failed to load model: {error}, contruct new model')
    step = 0
    step_size = 20000
    model = model.to(DEVICE)
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=0.01)
    all_losses = []
    min_loss = 10000
    for e in range(epoch):
        epoch_losses = []
        flush_print(f'epoch {e} starts')
        start = time.time()
        step_start = time.time()
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
            output = model(questions, answers, len_q, len_a, hidden_q, hidden_a)
            fake_answer_sims = []
            for fake_answer_data in batch[2:]:
                hidden_q = model.repackage_hidden(hidden, device=DEVICE)
                hidden_a = model.repackage_hidden(hidden, device=DEVICE)
                fake_answer, len_a = fake_answer_data
                fake_answer = fake_answer.to(DEVICE)
                len_a = len_a.to(DEVICE)
                similarity = model(questions, fake_answer, len_q, len_a, hidden_q, hidden_a)
                fake_answer_sims.append(similarity.unsqueeze(0))
            fake_answer_max_sim = torch.max(torch.cat(fake_answer_sims, 0), dim=0)[0]
            # loss = loss_fn(torch.cat((output, fake_answer_max_sim)),
            #               torch.Tensor([-1 for _ in output] + [1 for _ in fake_answer_max_sim]).to(DEVICE))
            loss = hinge_loss(output, fake_answer_max_sim)
            
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
            optimizer.step()
            
            epoch_losses.append(loss.item())
            if (train_data_loader.data_num() * e + batch_num * batch_size) // step_size > step:
                step += 1
                valid_loss = evaluate(model, valid_data_loader)
                flush_print(f'step: {step}, loss on train set: ' +\
                            f'{np.mean(epoch_losses[-step_size//batch_size:])},' +\
                            f'loss on validation set: {valid_loss}')
                flush_print('accu, avg_answer, avg_fake:' +\
                            f' {str(test(model, test_data_loader, limit = 0.7))}')
                flush_print(f'elapsed: {time.time() - step_start} s')
                step_start = time.time()
                if valid_loss <= min_loss:
                    min_loss = valid_loss
                    torch.save(model.state_dict(), target)
                    flush_print('best model saved')
            
        all_losses.append(np.mean(epoch_losses))
        valid_loss = evaluate(model, valid_data_loader)
        accu, avg_answer, avg_fake = test(model, test_data_loader, limit = 0.8)
        end = time.time()
        flush_print(f'epoch: {e}, train loss: {all_losses[-1]}, valid loss: {valid_loss}, elapsed: {end - start} s')
        flush_print(f'on test set: accu: {accu}, average answer similarity: {avg_answer}, fake: {avg_fake}')
        
        # save model
        if valid_loss <= min_loss:
            min_loss = valid_loss
            torch.save(model.state_dict(), target)
            saved_model_eval_data = (accu, avg_answer, avg_fake)
            not_update = 0
            flush_print('best model saved')
        else:
            not_update += 1
            if not_update > 1:
                break   # training finished as model not updated for 2 epochs
    print(f'finished training, with saved model accu, avg_answer, avg_fake: {saved_model_eval_data}')
            

def main(data_path):
    data_path = data_path.rstrip('/') + '/'
    vocab_path = data_path + 'vocab.pkl'
    model_path = data_path + 'test_model.param'
    file_names = [f'insuranceqa_processed_{set_name}.json' for set_name in ['train', 'valid', 'test']]
    train_set = DataLoader(data_path + file_names[0],
                           vocab_size=40000, seq_len_q=100, seq_len_a=200,\
                           batch_size=20, vocab_path=vocab_path, shuffle=True,
                           num_workers=4, nohup=False)
    valid_set = DataLoader(data_path + file_names[1],
                           vocab_size=40000, seq_len_q=100, seq_len_a=200,\
                           batch_size=64, vocab_path=vocab_path, shuffle=True,
                           num_workers=4, nohup=False)
    #train_set = valid_set
    test_set = DataLoader(data_path + file_names[2],
                          vocab_size=40000, seq_len_q=100, seq_len_a=200,\
                          batch_size=64, vocab_path=vocab_path, shuffle=True,
                          num_workers=4, nohup=False)
    model = AttentiveLSTM(valid_set.get_vocab_size(), embed_size=100, hidden_size=141)
    train(model, model_path, train_set, valid_set, test_set, epoch=20, lr=1e-3, _continue=False)


if __name__ == '__main__':
    main(sys.argv[1])
