# Generating Names with a Character-Level RNN
 Original is From pytorch official tutorial：`https://pytorch.org/tutorials/intermediate/char_rnn_generation_tutorial.html`
## E1 uses CUDA to accelerate training:  
Total running time from **3m 53s** to **7m 20s**. Monitor the GPU using `gpustat` in powershell.  
**Why time spent has increased ???** From powershell we got that the GPU usage was kept below 50%, so I conclude that RNN couldn't fully use the GPU. Using an improved module like `nn.LSTM` or `nn.GRU` could probably improve the situation. 
