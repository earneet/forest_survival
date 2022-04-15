import torch

class SubGoalSelector(torch.nn.Module):
    def __init__(self, input_dim=302, output_dim=12, layer_size=3):
        super(SubGoalSelector, self).__init__()
        self.model = torch.nn.Sequential(
            torch.nn.Linear(input_dim, input_dim // 2),
            torch.nn.ReLU(),
            torch.nn.Linear(input_dim // 2, input_dim // 4),
            torch.nn.ReLU(),
            torch.nn.Linear(input_dim // 4, output_dim)
        )
        self.output_layer = torch.nn.Softmax(dim=0)

    def forward(self, x):
        data = self.model(x)
        return self.output_layer(data)


def calc_equip_dim():
    return 0

def calc_slot_dim():
    return 0

def calc_player_dim():
    return 0

def calc_input_dim():
    total = 0
    return total