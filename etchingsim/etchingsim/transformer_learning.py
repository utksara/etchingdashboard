import torch
import torch.nn as nn
from torch.utils.data import Dataset
import numpy as np
import etchingsim.etchingdb as edb
import matplotlib.pyplot as plt
# -----------------------------
# 1. Dataset with variable-length curves
# -----------------------------
class VariableCurveDataset(Dataset):
    def __init__(self, num_samples=1, time_steps=20, min_points=30, max_points=60, params = [4.2, 0.9, 3, 1.9]):
        self.samples = []
        for _ in range(num_samples):
            seq = []
            m1 = params[0]
            m2 = params[1]
            m3 = params[2]
            m4 = params[3]
            collection = edb.get_db_collection()
            for t in range(time_steps):
                curve = np.array(edb.get_data(collection, f"{m1}_{m2}_{m3}_{m4}_{t}")["points"])[:,0:2]
                seq.append(curve)  # shape (N_t, 2)
            self.samples.append(seq)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        seq = self.samples[idx]
        # input = all but last; target = all but first
        return seq[:-1], seq[1:]


# -----------------------------
# 2. Collate function for variable-length batching
# -----------------------------
def collate_variable_curves(batch):
    # batch: list of (inp_seq, out_seq)
    batch_in, batch_out = zip(*batch)
    T = len(batch_in[0])  # number of timesteps per sequence (constant)

    max_points =  10*max(max(len(curve) for seq in batch_in for curve in seq),
                     max(len(curve) for seq in batch_out for curve in seq))
    # print("max points :", max_points)
    def pad_sequence(seq_list, plot_ = True):
        padded = []
        mask = []
        for seq in seq_list:
            seq_tensor = []
            seq_mask = []
            for curve in seq:
                pad_len = max_points - len(curve)
                padded_curve = np.pad(curve, ((0, pad_len), (0, 0)), mode='constant')
                mask_curve = np.concatenate([np.ones(len(curve)), np.zeros(pad_len)])
                seq_tensor.append(padded_curve)
                seq_mask.append(mask_curve)
            padded.append(np.stack(seq_tensor))  # (T, max_points, 2)
            mask.append(np.stack(seq_mask))      # (T, max_points)
        # if plot_:
        #     plt.plot(padded[0][10][:,0], padded[0][10][:,1], label="padded")
        return torch.tensor(padded, dtype=torch.float32), torch.tensor(mask, dtype=torch.bool)

    inp, inp_mask = pad_sequence(batch_in, plot_ = False)
    out, out_mask = pad_sequence(batch_out)
    # plt.plot(batch_out[0][10][:,0], batch_out[0][10][:,1], label="batch out")
    # plt.plot(out[0,10,:,0], out[0,10,:,1], label="out")
    # Flatten (x,y) pairs into feature dimension
    B, T, N, D = inp.shape
    inp = inp.view(B, T, N * D)
    out = out.view(B, T, N * D)
    return inp, out, inp_mask


# -----------------------------
# 3. Transformer model (time transformer)
# -----------------------------
class CurveTransformer(nn.Module):
    def __init__(self, input_dim, d_model=256, nhead=8, num_layers=3, dropout=0.1):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=512, dropout=dropout)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        self.output_proj = nn.Linear(d_model, input_dim)

    def forward(self, src, src_mask=None):
        # src: (T, B, input_dim)
        src = self.input_proj(src)
        src = self.pos_encoder(src)
        output = self.transformer(src, src_key_padding_mask=None)
        return self.output_proj(output)


# -----------------------------
# 4. Positional encoding
# -----------------------------
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0)].transpose(0, 1)
        return self.dropout(x)


# -----------------------------
# 5. Training loop
# -----------------------------
def train_model(model, dataloader, epochs=20, lr=1e-3, device='cuda' if torch.cuda.is_available() else 'cpu'):
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    for epoch in range(epochs):
        total_loss = 0.0
        for inp, out, mask in dataloader:
            inp, out = inp.to(device), out.to(device)
            inp = inp.transpose(0, 1)  # (T, B, F)
            out = out.transpose(0, 1)

            pred = model(inp)
            loss = loss_fn(pred, out)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"Epoch [{epoch+1}/{epochs}] - Loss: {total_loss/len(dataloader):.6f}")