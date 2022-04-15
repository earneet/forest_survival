from datetime import datetime

import torch
from torch.nn import CrossEntropyLoss
from torch.optim import SGD
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from torchvision.transforms import transforms

from deepselector.data_loader import load_data_file
from deepselector.model import SubGoalSelector

data_set = []
data_set.extend(load_data_file(0))
train_dataloader = DataLoader(data_set, batch_size=64, shuffle=True)

transformer = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

model = SubGoalSelector().cuda()
loss_fn = CrossEntropyLoss()
optimizer = SGD(model.parameters(), lr=0.001, momentum=0.9)

def train_one_epoch(epoch_index, tb_writer=None):
    running_loss = 0.0
    for i, data in enumerate(train_dataloader):
        inputs, labels = data
        inputs, labels = inputs.cuda(), labels.cuda()
        optimizer.zero_grad()
        outputs = model(inputs)

        loss = loss_fn(outputs, labels)
        loss.backward()

        optimizer.step()
        running_loss += loss.item()
    return running_loss

def train():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    writer = SummaryWriter('runs/fashion_trainer_{}'.format(timestamp))
    model.train(True)

    for epoch in range(100001):
        avg_loss = train_one_epoch(epoch, writer)
        print(f" epoch {epoch} avg_loss {avg_loss}")
        if epoch % 1000 == 0:
            torch.save(model.state_dict(), f"../model/model_{epoch}.pth")


if __name__ == "__main__":
    train()
