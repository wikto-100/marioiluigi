from model import LuigiCNN

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = LuigiCNN(action_channels=1).to(device)

