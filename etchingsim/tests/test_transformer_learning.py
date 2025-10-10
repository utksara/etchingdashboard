import torch
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
from etchingsim.transformer_learning import VariableCurveDataset, collate_variable_curves, CurveTransformer, \
train_model

if __name__ == "__main__":
    
    reuse_model = True
    
    dataset = VariableCurveDataset()
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True, collate_fn=collate_variable_curves)

    # compute input dimension (based on padding)
    _, (x_test, y_test, mask_test) = next(enumerate(dataloader))
    input_dim = x_test.shape[-1]
    
    if reuse_model:
        checkpoint = torch.load("curve_transformer_checkpoint.pth", map_location="cpu")
        model = CurveTransformer(
        input_dim=checkpoint['input_dim'],
        d_model=checkpoint['d_model']
    )
        model.load_state_dict(checkpoint['model_state_dict'])   
    else:
        model = CurveTransformer(input_dim=input_dim)
    train_model(model, dataloader, epochs=1000, lr=1e-4)

    # visualize last frame prediction
    inp, out, mask = next(iter(dataloader))
    with torch.no_grad():
        pred = model(inp.transpose(0,1)).transpose(0,1).cpu().numpy()

    B, T, F = pred.shape
    N = F // 2
    idx = 0  # pick first sample
    frame = -1
    plt.plot(pred[idx, frame, :N], pred[idx, frame, N:], label="Predicted")
    plt.plot(out[idx, frame, :N], out[idx, frame, N:], label="True")
    plt.legend()
    plt.show()
    
    torch.save({
        'model_state_dict': model.state_dict(),
        'input_dim': model.input_proj.in_features,
        'd_model': model.input_proj.out_features,
    }, "curve_transformer_checkpoint.pth")

