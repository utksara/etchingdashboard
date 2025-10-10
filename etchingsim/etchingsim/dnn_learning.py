import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader, random_split
from . import etchingdb, etchingsim, mra_reconstruct
import numpy as np
import mrafit

# --- 1. NN Architecture and Hyperparameters ---
INPUT_SIZE = 5     # Five scalar parameters (input features)
HIDDEN_SIZE = 1   # Hidden layer size
OUTPUT_SIZE = 20   # Scalar regression output
LEARNING_RATE = 0.01
EPOCHS = 1000


collection = etchingdb.get_db_collection()
allkeys = etchingdb.get_all_keys(collection)

# Data Size
TOTAL_SAMPLES = len(allkeys)
TRAIN_SAMPLES = 0.1*TOTAL_SAMPLES
TEST_SAMPLES = TOTAL_SAMPLES - TRAIN_SAMPLES


# --- 2. Define the Neural Network Model (One Hidden Layer) ---
class SimpleNN(nn.Module):
    """
    A simple two-layer neural network for regression using PyTorch.
    Input (5) -> Hidden (10, ReLU) -> Output (1, Linear)
    """
    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleNN, self).__init__()
        # First layer: Input to Hidden
        self.layer1 = nn.Linear(input_size, hidden_size)
        # Activation function for the hidden layer
        self.relu = nn.ReLU()
        # Second layer: Hidden to Output (Linear for regression)
        self.layer2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        """Forward pass through the network."""
        out = self.layer1(x)
        out = self.relu(out)
        out = self.layer2(out)
        return out

# --- 3. Data Generation and Split (20 training vs 2 test) ---

def generate_data():
    """Generates synthetic data and converts it to PyTorch Tensors."""
    # X: n_samples x n_features
    X = np.zeros(INPUT_SIZE, TOTAL_SAMPLES)
    Y = np.zeros(OUTPUT_SIZE, TOTAL_SAMPLES)
    gausslet = mrafit.wavelet_bases.Gausslet_Basis(resolution=0.1)
    for key in allkeys:
        X[:,i] = np.array(etchingdb.extract_params(key))
        actual_curve_points = etchingdb.get_data(collection, key)["points"]
        y = [actual_curve_points[i][1] for i in range(len(actual_curve_points))]
        Y[:,i] = mra_reconstruct.get_mra_coefficients(y, gausslet, X)
    X = torch.from_numpy(X)
    # Y: True relationship: Y = 2*X1 + 0.5*X2 - 3*X3 + noise
    # Target values (Y): n_samples x 1
    Y = torch.from_numpy(Y)
    
    # Ensure data types are floats for the network
    return X.float(), Y.float()

X_full, Y_full = generate_data(TOTAL_SAMPLES, INPUT_SIZE)
full_dataset = TensorDataset(X_full, Y_full)

# Splitting data (10:1 ratio -> 20 train, 2 test)
train_dataset, test_dataset = random_split(full_dataset, [TRAIN_SAMPLES, TEST_SAMPLES])

# Create DataLoaders for easy iteration (Batch size 20 is the entire training set)
train_loader = DataLoader(train_dataset, batch_size=TRAIN_SAMPLES, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=TEST_SAMPLES, shuffle=False)

print(f"Total Samples Generated: {TOTAL_SAMPLES}")
print(f"Training Samples: {len(train_dataset)}")
print(f"Test Samples: {len(test_dataset)}")
print("-" * 30)

# --- 4. Model, Loss, and Optimizer Initialization ---
model = SimpleNN(INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE)
criterion = nn.MSELoss() # Loss function for regression
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# --- 5. Training Loop ---

for epoch in range(1, EPOCHS + 1):
    for inputs, targets in train_loader:
        # Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, targets)

        # Backward and optimize
        optimizer.zero_grad() # Clear previous gradients
        loss.backward()       # Compute gradient of the loss
        optimizer.step()      # Update model parameters

    # Logging
    if epoch % 100 == 0:
        print(f"Epoch {epoch}/{EPOCHS}, Training Loss (MSE): {loss.item():.4f}")


# --- 6. Evaluation on Test Set ---

print("-" * 30)
model.eval() # Set the model to evaluation mode (disables dropout/batchnorm, though not used here)

with torch.no_grad(): # Disable gradient calculation during testing
    for inputs, targets in test_loader:
        Y_test_pred = model(inputs)
        test_loss = criterion(Y_test_pred, targets)

print(f"Final Test Loss (MSE): {test_loss.item():.4f}")
print("\n--- Test Set Predictions vs True Values ---")
# Print actual values from the small test set
for i in range(TEST_SAMPLES):
    true_val = targets[i].item()
    pred_val = Y_test_pred[i].item()
    print(f"Sample {i+1}: True={true_val:.2f}, Predicted={pred_val:.2f}")
