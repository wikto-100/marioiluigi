import torch
import torch.nn as nn
from src.mask_layer import MaskLayer

class LuigiCNN(nn.Module):
    def __init__(self):
        super(LuigiCNN, self).__init__()

        # Initial layer - keeping 16 input channels but adding more features
        self.conv1 = nn.Sequential(
            nn.Conv2d(16, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2),
            nn.Dropout2d(0.1),
        )

        # Residual blocks for better gradient flow
        self.res_block1 = ResidualBlock(64, 128)
        self.res_block2 = ResidualBlock(128, 256)

        # Policy head
        self.policy_head = nn.Sequential(
            nn.Linear(256 * 64, 1024),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.2),
            nn.Linear(1024, 64 * 64),
        )

        self.mask = MaskLayer()

    def forward(self, x, mask=None, debug=False):
        # Initial convolution
        x = self.conv1(x)

        # Residual blocks
        x = self.res_block1(x)
        x = self.res_block2(x)

        # Flatten and policy head
        x = x.view(x.size(0), -1)
        x = self.policy_head(x)

        # Apply mask if provided
        if mask is not None:
            x = self.mask(x, mask)

        return x


class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(ResidualBlock, self).__init__()

        self.conv_block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU(0.2),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
        )

        # Shortcut connection
        self.shortcut = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=1),
            nn.BatchNorm2d(out_channels),
        )

        self.leaky_relu = nn.LeakyReLU(0.2)

    def forward(self, x):
        residual = x
        x = self.conv_block(x)
        x += self.shortcut(residual)
        x = self.leaky_relu(x)
        return x
