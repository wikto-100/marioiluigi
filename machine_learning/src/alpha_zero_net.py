import torch
import torch.nn as nn
import torch.nn.functional as F
from src.mask_layer import MaskLayer

class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        residual = x
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x += residual
        x = F.relu(x)
        return x

class AlphaZeroNet(nn.Module):
    def __init__(self, board_size=8, num_blocks=19, num_channels=256):
        super(AlphaZeroNet, self).__init__()

        self.input_layer = nn.Sequential(
                nn.Conv2d(16, num_channels, kernel_size=3, padding=1, bias=False),
                nn.BatchNorm2d(num_channels),
                nn.ReLU()
        )

        self.res_blocks = nn.ModuleList(
                [ResidualBlock(num_channels) for _ in range(num_blocks)]
        )

        self.policy_head = nn.Sequential(
                nn.Conv2d(num_channels, 2, kernel_size=1),
                nn.BatchNorm2d(2),
                nn.ReLU(),
                nn.Flatten(),
                nn.Linear(2 * board_size * board_size, 1),
                nn.Tanh()
        )

        self.mask = MaskLayer()

    def forward(self, x, mask=None, debug=False):
        x = self.input_layer(x)

        for block in self.res_blocks:
            x = block(x)

        #x = x.view(x.size(0), -1)
        x = self.policy_head(x)

        if mask is not None:
            x = self.mask(x, mask)

        return x
