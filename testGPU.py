import torch
print("CUDA available:", torch.cuda.is_available())
print("Torch CUDA version:", torch.version.cuda)
print("Compiled with CUDA:", torch.backends.cuda.is_built())
print("Device count:", torch.cuda.device_count())