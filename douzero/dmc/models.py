"""
This file includes the torch models. We wrap the three
models into one class for convenience.
"""

import numpy as np

import torch
from torch import nn

class LandlordLstmModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(432, 256, batch_first=True)
        self.dense1 = nn.Linear(1087, 1024)
        self.dense2 = nn.Linear(1024, 1024)
        self.dense3 = nn.Linear(1024, 1024)
        self.dense4 = nn.Linear(1024, 1024)
        self.dense5 = nn.Linear(1024, 1024)
        self.dense6 = nn.Linear(1024, 1024)
        self.dense7 = nn.Linear(1024, 1024)
        self.dense8 = nn.Linear(1024, 1024)
        self.dense9 = nn.Linear(1024, 1024)
        self.dense10 = nn.Linear(1024, 1024)
        self.dense11 = nn.Linear(1024, 1)

    def forward(self, z, x, return_value=False, flags=None):
        lstm_out, (h_n, _) = self.lstm(z)
        lstm_out = lstm_out[:,-1,:]
        x = torch.cat([lstm_out,x], dim=-1)
        x = self.dense1(x)
        x = torch.relu(x)
        x = self.dense2(x)
        x = torch.relu(x)
        x = self.dense3(x)
        x = torch.relu(x)
        x = self.dense4(x)
        x = torch.relu(x)
        x = self.dense5(x)
        x = torch.relu(x)
        x = self.dense6(x)
        x = torch.relu(x)
        x = self.dense7(x)
        x = torch.relu(x)
        x = self.dense8(x)
        x = torch.relu(x)
        x = self.dense9(x)
        x = torch.relu(x)
        x = self.dense10(x)
        x = torch.relu(x)
        x = self.dense11(x)
        if return_value:
            return dict(values=x)
        else:
            if flags is not None and flags.exp_epsilon > 0 and np.random.rand() < flags.exp_epsilon:
                action = torch.randint(x.shape[0], (1,))[0]
            else:
                action = torch.argmax(x,dim=0)[0]
            return dict(action=action)

class FarmerLstmModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(432, 256, batch_first=True)
        self.dense1 = nn.Linear(1419, 1024)
        self.dense2 = nn.Linear(1024, 1024)
        self.dense3 = nn.Linear(1024, 1024)
        self.dense4 = nn.Linear(1024, 1024)
        self.dense5 = nn.Linear(1024, 1024)
        self.dense6 = nn.Linear(1024, 1024)
        self.dense7 = nn.Linear(1024, 1024)
        self.dense8 = nn.Linear(1024, 1024)
        self.dense9 = nn.Linear(1024, 1024)
        self.dense10 = nn.Linear(1024, 1024)
        self.dense11 = nn.Linear(1024, 1)

    def forward(self, z, x, return_value=False, flags=None):
        lstm_out, (h_n, _) = self.lstm(z)
        lstm_out = lstm_out[:,-1,:]
        x = torch.cat([lstm_out,x], dim=-1)
        x = self.dense1(x)
        x = torch.relu(x)
        x = self.dense2(x)
        x = torch.relu(x)
        x = self.dense3(x)
        x = torch.relu(x)
        x = self.dense4(x)
        x = torch.relu(x)
        x = self.dense5(x)
        x = torch.relu(x)
        x = self.dense6(x)
        x = torch.relu(x)
        x = self.dense7(x)
        x = torch.relu(x)
        x = self.dense8(x)
        x = torch.relu(x)
        x = self.dense9(x)
        x = torch.relu(x)
        x = self.dense10(x)
        x = torch.relu(x)
        x = self.dense11(x)
        if return_value:
            return dict(values=x)
        else:
            if flags is not None and flags.exp_epsilon > 0 and np.random.rand() < flags.exp_epsilon:
                action = torch.randint(x.shape[0], (1,))[0]
            else:
                action = torch.argmax(x,dim=0)[0]
            return dict(action=action)

# Model dict is only used in evaluation but not training
model_dict = {}
model_dict['landlord'] = LandlordLstmModel
model_dict['landlord_down1'] = FarmerLstmModel
model_dict['landlord_down2'] = FarmerLstmModel
model_dict['landlord_down3'] = FarmerLstmModel

class Model:
    """
    The wrapper for the four models. We also wrap several
    interfaces such as share_memory, eval, etc.
    """
    def __init__(self, device=0):
        self.models = {}
        if not device == "cpu":
            device = 'cuda:' + str(device)
        self.models['landlord'] = LandlordLstmModel().to(torch.device(device))
        self.models['landlord_down1'] = FarmerLstmModel().to(torch.device(device))
        self.models['landlord_down2'] = FarmerLstmModel().to(torch.device(device))
        self.models['landlord_down3'] = FarmerLstmModel().to(torch.device(device))

    def forward(self, position, z, x, training=False, flags=None):
        model = self.models[position]
        return model.forward(z, x, training, flags)

    def share_memory(self):
        self.models['landlord'].share_memory()
        self.models['landlord_down1'].share_memory()
        self.models['landlord_down2'].share_memory()
        self.models['landlord_down3'].share_memory()

    def eval(self):
        self.models['landlord'].eval()
        self.models['landlord_down1'].eval()
        self.models['landlord_down2'].eval()
        self.models['landlord_down3'].eval()

    def parameters(self, position):
        return self.models[position].parameters()

    def get_model(self, position):
        return self.models[position]

    def get_models(self):
        return self.models
