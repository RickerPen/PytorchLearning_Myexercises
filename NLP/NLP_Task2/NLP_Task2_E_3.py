from io import open
import glob
import os
import unicodedata
import string

all_letters = string.ascii_letters + " .,;'-"
n_letters = len(all_letters) + 1 # Plus EOS marker

def findFiles(path): return glob.glob(path)

# Turn a Unicode string to plain ASCII, thanks to https://stackoverflow.com/a/518232/2809427
def unicodeToAscii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
        and c in all_letters
    )

# Read a file and split into lines
def readLines(filename):
    with open(filename, encoding='utf-8') as some_file:
        return [unicodeToAscii(line.strip()) for line in some_file]

# Build the category_lines dictionary, a list of lines per category
category_lines = {}
all_categories = []
for filename in findFiles('pytorch_learn/data/names/*.txt'):
    category = os.path.splitext(os.path.basename(filename))[0]
    all_categories.append(category)
    lines = readLines(filename)
    category_lines[category] = lines

n_categories = len(all_categories)

if n_categories == 0:
    raise RuntimeError('Data not found. Make sure that you downloaded data '
        'from https://download.pytorch.org/tutorial/data.zip and extract it to '
        'the current directory.')

print('# categories:', n_categories, all_categories)
print(unicodeToAscii("O'Néàl"))
import torch
import torch.nn as nn

class LSTM_Improved(nn.Module):
    def __init__(self, n_categories, input_size, hidden_size, output_size):
        super(LSTM_Improved, self).__init__()
        self.hidden_size = hidden_size
        self.n_categories = n_categories

        # 关键修改 1: 用LSTM替代原始RNN计算
        self.lstm = nn.LSTM(
            input_size=input_size + n_categories,  # 输入维度增加类别信息
            hidden_size=hidden_size,
            batch_first=True  # 保持(batch, seq, features)格式
        )
        
        # 关键修改 2: 调整输出层适配LSTM输出
        self.fc = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(0.1)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, category, input, hidden):
        """
        保持与原始RNN完全相同的输入输出接口：
        - 输入: 
            category: (batch_size, n_categories)
            input:    (batch_size, input_size)
            hidden:   (h: (1, batch_size, hidden_size), c: (1, batch_size, hidden_size))
        - 输出:
            output:   (batch_size, output_size)
            hidden:   更新后的LSTM隐藏状态
        """
        # 维度转换确保兼容性
        batch_size = input.size(0)
        
        # 关键修改 3: 将类别信息与输入拼接
        combined = torch.cat([category, input], dim=1)  # (batch, n_cat+input_size)
        combined = combined.unsqueeze(1)  # 添加序列维度 -> (batch, 1, n_cat+input_size)
        
        # LSTM前向传播
        # lstm_out: (batch, seq_len=1, hidden_size)
        # hidden: (h_n, c_n) 每个的形状都是(1, batch, hidden_size)
        lstm_out, hidden = self.lstm(combined, hidden)
        
        # 关键修改 4: 处理输出层
        out = self.fc(lstm_out.squeeze(1))  # 移除序列维度
        out = self.dropout(out)
        out = self.softmax(out)
        return out, hidden

    def initHidden(self, batch_size=1):
        """返回与原始RNN兼容的隐藏状态格式"""
        # LSTM需要返回元组(h_0, c_0)
        return (
            torch.zeros(1, batch_size, self.hidden_size),  # h0
            torch.zeros(1, batch_size, self.hidden_size)   # c0
        )
    
import random

# Random item from a list
def randomChoice(l):
    return l[random.randint(0, len(l) - 1)]

# Get a random category and random line from that category
def randomTrainingPair():
    category = randomChoice(all_categories)
    line = randomChoice(category_lines[category])
    return category, line
# One-hot vector for category
def categoryTensor(category):
    li = all_categories.index(category)
    tensor = torch.zeros(1, n_categories)
    tensor[0][li] = 1
    return tensor

# One-hot matrix of first to last letters (not including EOS) for input
def inputTensor(line):
    tensor = torch.zeros(len(line), 1, n_letters)
    for li in range(len(line)):
        letter = line[li]
        tensor[li][0][all_letters.find(letter)] = 1
    return tensor

# ``LongTensor`` of second letter to end (EOS) for target
def targetTensor(line):
    letter_indexes = [all_letters.find(line[li]) for li in range(1, len(line))]
    letter_indexes.append(n_letters - 1) # EOS
    return torch.LongTensor(letter_indexes)
# Make category, input, and target tensors from a random category, line pair
def randomTrainingExample():
    category, line = randomTrainingPair()
    category_tensor = categoryTensor(category)
    input_line_tensor = inputTensor(line)
    target_line_tensor = targetTensor(line)
    return category_tensor, input_line_tensor, target_line_tensor
criterion = nn.NLLLoss()

learning_rate = 0.0005

def train(category_tensor, input_line_tensor, target_line_tensor):
    target_line_tensor.unsqueeze_(-1)
    hidden = lstm.initHidden()

    lstm.zero_grad()

    loss = torch.Tensor([0]) # you can also just simply use ``loss = 0``

    for i in range(input_line_tensor.size(0)):
        output, hidden = lstm(category_tensor, input_line_tensor[i], hidden)
        l = criterion(output, target_line_tensor[i])
        loss += l

    loss.backward()

    for p in lstm.parameters():
        p.data.add_(p.grad.data, alpha=-learning_rate)

    return output, loss.item() / input_line_tensor.size(0)
import time
import math

def timeSince(since):
    now = time.time()
    s = now - since
    m = math.floor(s / 60)
    s -= m * 60
    return '%dm %ds' % (m, s)
lstm = LSTM_Improved(n_categories,n_letters, 128, n_letters)

n_iters = 100000
print_every = 5000
plot_every = 500
all_losses = []
total_loss = 0 # Reset every ``plot_every`` ``iters``

start = time.time()

for iter in range(1, n_iters + 1):
    output, loss = train(*randomTrainingExample())
    total_loss += loss

    if iter % print_every == 0:
        print('%s (%d %d%%) %.4f' % (timeSince(start), iter, iter / n_iters * 100, loss))

    if iter % plot_every == 0:
        all_losses.append(total_loss / plot_every)
        total_loss = 0
import matplotlib.pyplot as plt

plt.figure()
plt.plot(all_losses)

max_length = 20

# Sample from a category and starting letter
def sample(category, start_letter='A'):
    with torch.no_grad():  # no need to track history in sampling
        category_tensor = categoryTensor(category)
        input = inputTensor(start_letter)
        hidden = lstm.initHidden()

        output_name = start_letter

        for i in range(max_length):
            output, hidden = lstm(category_tensor, input[0], hidden)
            topv, topi = output.topk(1)
            topi = topi[0][0]
            if topi == n_letters - 1:
                break
            else:
                letter = all_letters[topi]
                output_name += letter
            input = inputTensor(letter)

        return output_name

# Get multiple samples from one category and multiple starting letters
def samples(category, start_letters='ABC'):
    for start_letter in start_letters:
        print(sample(category, start_letter))

samples('Russian', 'RUS')

samples('German', 'GER')

samples('Spanish', 'SPA')

samples('Chinese', 'CHI')
