import torch
from etchingsim.transformer_learning import CurveTransformer, VariableCurveDataset, train_model, \
    collate_variable_curves
from torch.utils.data import DataLoader
import etchingsim.etchingdb as etchingdb
import matplotlib.pyplot as plt
import numpy as np

checkpoint = torch.load("curve_transformer_checkpoint.pth", map_location="cpu")

model = CurveTransformer(
    input_dim=checkpoint['input_dim'],
    d_model=checkpoint['d_model']
)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()  # switch to evaluation mode
print("Model loaded and ready for prediction.")

def denoising(curve):
    curve = curve.numpy()
    for _ in range(26):
        curve = np.concatenate([curve, curve[-1:]], axis=0)
        curve = 0.5*(curve[:-1] + curve[1:])
    return torch.tensor(curve)
    
with torch.no_grad():
    m1 = 4.2
    m2 = 0.9
    m3 = 3
    m4 = 1.9
    t = 10

    dataset1 = VariableCurveDataset()
    dataset2 = VariableCurveDataset(params = [m1, m2, m3, m4])
    
    dataloader1 = DataLoader(dataset1, batch_size=1, shuffle=True, collate_fn=collate_variable_curves)
    dataloader2 = DataLoader(dataset2, batch_size=1, shuffle=True, collate_fn=collate_variable_curves)
    
    # visualize last frame prediction
    inp, out, mask = next(iter(dataloader1))
    # inp, out, mask = next(iter(dataloader2))
    # print("out.shape ", out.shape)
    
    idx = 0  # pick first sample
    frame = 5
    inp = torch.tensor(inp)
    
    B, T, F = inp.shape
    N = F // 2
    inp_plot = inp.view(B, T, N, 2)
    plt.plot(inp_plot [idx, frame, :, 0], inp_plot [idx, frame, :, 1], label="in")
    
    
    B, T, F = out.shape
    N = F // 2
    out_plot = out.view(B, T, N, 2)
    
    # plt.plot(out_plot [idx, frame, :, 0], out_plot [idx, frame, :, 1], label="out")
    # plt.legend()
    # plt.show()
    for i in range(11):
        with torch.no_grad():
            pred = model(inp.transpose(0,1)).transpose(0,1).cpu().numpy()
        idx = 0  # pick first sample
        B, T, F = pred.shape
        N = F // 2
        pred = torch.tensor(pred)        
        pred = pred.view(B, T, N, 2)
        pred[idx, frame, :, 0] = denoising(pred[idx, frame, :, 0])
        pred_plot = pred.clone()
        pred = pred.view(B, T, F)
        
        inp = pred
        
        if (i%5 == 0):
            plt.plot(pred_plot[idx, frame, :, 0], pred_plot[idx, frame, :, 1], label=f"Predicted {i}")
    
    plt.legend()
    plt.show()
