import torch
import torch.nn as nn


class MaskLayer(nn.Module):
    def __init__(self):
        super(MaskLayer, self).__init__()

    def forward(self, x, mask):
        return torch.mul(x, mask)
