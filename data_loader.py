import os
import numpy as np
import torch
import torch.utils.data as data
import torchvision.transforms as transforms
from PIL import Image
from utils import text_processing


class VqaDataset(data.Dataset):

    def __init__(self, input_dir, input_vqa, max_qst_length=30, transform=None):
        self.input_dir = input_dir
        self.vqa = np.load(input_dir+'/'+input_vqa)
        self.qst_vocab = text_processing.VocabDict(input_dir+'/vocab_questions.txt')
        self.ans_vocab = text_processing.VocabDict(input_dir+'/vocab_answers.txt')
        self.max_qst_length = max_qst_length
        self.load_ans = ('valid_answers' in self.vqa[0]) and (self.vqa[0]['valid_answers'] is not None)
        self.transform = transform

    def __getitem__(self, idx):

        vqa = self.vqa
        qst_vocab = self.qst_vocab
        ans_vocab = self.ans_vocab
        max_qst_length = self.max_qst_length
        transform = self.transform
        load_ans = self.load_ans

        image = vqa[idx]['image_path']
        image = Image.open(image).convert('RGB')
        qst2idc = np.array([qst_vocab.word2idx('<pad>')] * max_qst_length)
        qst2idc[:len(vqa[idx]['question_tokens'])] = [qst_vocab.word2idx(w) for w in vqa[idx]['question_tokens']]
        sample = {'image': image, 'question': qst2idc}
        if load_ans:
            ans2idc = [ans_vocab.word2idx(w) for w in vqa[idx]['valid_answers']]
            ans2idx = np.random.choice(ans2idc)
            sample['answer'] = ans2idx
        if transform:
            sample['image'] = transform(sample['image'])

        return sample

    def __len__(self):

        return len(self.vqa)


def get_loader(input_dir, input_vqa, max_qst_length, transform, batch_size, shuffle, num_workers):

    vqa_dataset = VqaDataset(
        input_dir=input_dir,
        input_vqa=input_vqa,
        max_qst_length=max_qst_length,
        transform=transform)

    data_loader = torch.utils.data.DataLoader(
        dataset=vqa_dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers)

    return data_loader
