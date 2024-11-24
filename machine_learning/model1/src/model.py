# model.py

import torch
import torch.nn as nn
import torch.nn.functional as F

class ResidualBlock(nn.Module):
    """
    Standardowy blok resztkowy z dwoma warstwami konwolucyjnymi i połączeniem przeskakującym (skip connection).
    """
    def __init__(self, in_channels, out_channels, kernel_size=3, padding=1):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size, padding=padding)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size, padding=padding)
        self.bn2 = nn.BatchNorm2d(out_channels)

        if in_channels != out_channels:
            self.skip = nn.Conv2d(in_channels, out_channels, kernel_size=1)  # Dopasowanie wymiarów
        else:
            self.skip = nn.Identity()

    def forward(self, x):
        identity = self.skip(x)  # Połączenie przeskakujące
        out = F.relu(self.bn1(self.conv1(x)))  # Pierwsza warstwa konwolucyjna z ReLU
        out = self.bn2(self.conv2(out))        # Druga warstwa konwolucyjna
        out += identity                        # Dodanie połączenia przeskakującego
        out = F.relu(out)                      # Aktywacja ReLU
        return out

class LuigiCNN(nn.Module):
    def __init__(self, action_channels=1):  # action_channels ustawiony na 1
        super(LuigiCNN, self).__init__()
        
        self.action_channels = action_channels

        self.conv1 = nn.Conv2d(in_channels=12, out_channels=64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)

        # Bloki resztkowe
        self.residual_blocks = nn.Sequential(
            ResidualBlock(64, 128),
            ResidualBlock(128, 128),
            ResidualBlock(128, 256),
            ResidualBlock(256, 256)
        )

        self.conv_final = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        self.bn_final = nn.BatchNorm2d(256)

        # Globalne uśrednianie (global average pooling)
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))

        # Warstwy w pełni połączone (fully connected) dla głowy polityki (policy head)
        self.fc1 = nn.Linear(256, 1024)
        self.fc2 = nn.Linear(1024, self.action_channels * 4096)  # Aktualnie: 1 * 4096 = 4096

        # Głowa wartości (opcjonalna)
        self.value_conv = nn.Conv2d(256, 1, kernel_size=1)
        self.value_bn = nn.BatchNorm2d(1)
        self.value_fc = nn.Linear(8 * 8, 1)

    def forward(self, x, action_mask):
        batch_size = x.size(0)

        x = F.relu(self.bn1(self.conv1(x)))  # [batch_size, 64, 8, 8]
        x = self.residual_blocks(x)          # [batch_size, 256, 8, 8]
        x = F.relu(self.bn_final(self.conv_final(x)))  # [batch_size, 256, 8, 8]

        # Głowa polityki (policy head)
        pooled = self.global_pool(x).view(batch_size, -1)  # [batch_size, 256]
        x_policy = F.relu(self.fc1(pooled))               # [batch_size, 1024]
        x_policy = self.fc2(x_policy)                     # [batch_size, 4096]
        x_policy = x_policy.view(batch_size, self.action_channels, 4096)  # [batch_size, 1, 4096]

        # Zastosowanie maski akcji (jeśli potrzebne)
        # x_policy = x_policy * action_mask  # [batch_size, 1, 4096]

        # Głowa wartości (value head, opcjonalna)
        x_value = F.relu(self.value_bn(self.value_conv(x)))  # [batch_size, 1, 8, 8]
        x_value = x_value.view(batch_size, -1)              # [batch_size, 64]
        x_value = torch.tanh(self.value_fc(x_value))        # [batch_size, 1]

        return x_policy, x_value  # Wyniki polityki (logity) i przewidywana wartość
