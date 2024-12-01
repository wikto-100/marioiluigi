#train_openings.py

import sys
import os
import torch
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath('../'))

from model import LuigiCNN
from torch.utils.data import DataLoader, TensorDataset

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = LuigiCNN(action_channels=1).to(device)

#model.load_state_dict(torch.load('trained_with_openings.pth'))
#model.eval()

optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
criterion = torch.nn.CrossEntropyLoss()

data = torch.load("data_preprocessed.pt")
train_inputs = data['train_inputs']
val_inputs = data['val_inputs']
train_targets = data['train_targets']
val_targets = data['val_targets']

train_data = TensorDataset(train_inputs, train_targets)
val_data = TensorDataset(val_inputs, val_targets)

train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
val_loader = DataLoader(val_data, batch_size=64, shuffle=False)


def train_model(model, train_loader, val_loader, optimizer, criterion, epochs=50):
    train_losses = []
    val_losses = []
    val_accuracies = []

    for epoch in range(epochs):
        model.train()
        total_loss = 0

        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)

            outputs, _ = model(inputs, None)
            outputs = outputs.view(-1, 4096)

            loss = criterion(outputs, targets)
            total_loss += loss.item()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        train_losses.append(total_loss)

        val_loss, val_accuracy = validate_model(model, val_loader, criterion)
        val_losses.append(val_loss)
        val_accuracies.append(val_accuracy)

        print(f"epoch {epoch+1}/{epochs}, Loss: {total_loss:.4f}, Val loss: {val_loss:.4f}, Val Acc: {val_accuracy:.2f}%")

    return train_losses, val_losses, val_accuracies

def validate_model(model, val_loader, criterion):
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for inputs, targets in val_loader:
            inputs, targets = inputs.to(device), targets.to(device)

            outputs, _ = model(inputs, None)
            outputs = outputs.view(-1, 4096)

            loss = criterion(outputs, targets)
            total_loss += loss.item()

            _, predicted = torch.max(outputs, dim=1)
            correct += (predicted == targets).sum().item()
            total += targets.size(0)

    accuracy = 100 * correct / total
    return total_loss, accuracy



train_losses, val_losses, val_accuracies = train_model(model, train_loader, val_loader, optimizer, criterion, epochs=50)

torch.save(model.state_dict(), 'trained_with_openings.pth')

def predict_move(model, fen):
    board = chess.Board(fen)
    state = board_to_tensor(board).unsqueeze(0).to(device)

    with torch.no_grad():
        model.eval()
        outputs, _ = model(state, None)
        outputs = outputs.view(-1, 4096)

        _, move_index = torch.max(outputs, dim=1)
        move = index_to_move(board, move_index.item())

    return move.uci()


def plot_metrics():
    epochs = range(1, len(train_losses) + 1)

    plt.figure(figsize=(12,5))

    plt.subplot(1, 2, 1)
    plt.plot(epochs, train_losses, label='Training Loss', color='blue')
    plt.plot(epochs, val_losses, label='Validation Loss', color='red')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title("Training and validation loss")
    plt.legend()

    plt.subplot(1,2,2)
    plt.plot(epochs, val_accuracies, label='Validation Accuracy', color='green')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy (%)')
    plt.title('Validation Accuracy')
    plt.legend()

    plt.tight_layout()

    plt.savefig('postep.pdf')


plot_metrics()
    

