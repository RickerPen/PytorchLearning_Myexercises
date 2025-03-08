# Generating Names with a Character-Level RNN
 Original is From pytorch official tutorial：`https://pytorch.org/tutorials/intermediate/char_rnn_generation_tutorial.html`
## E_1 uses CUDA to accelerate training:  
Total running time from **3m 53s** to **7m 20s**. Monitor the GPU using `gpustat` in powershell.  
**Why time spent has increased ???** From powershell we got that the GPU usage was kept below 50%, so I conclude that RNN couldn't fully use the GPU. Using an improved module like `nn.LSTM` or `nn.GRU` could probably improve the situation. 
## E_2 uses a "SOS" token so that sampling can be done without a start letter:  
Adjust InputTensor's first input from the first letter to 'SOS' token, and its corresponding TargetTensor is the first letter. 
## E_3 replaces RNN with LSTM or GRU:
*08/03/2025,15:40* : Since the original script mainly uses `nn.linear` to create its customized RNN rather than using `nn.RNN` directly, it's hard to recreate the network by using `nn.LSTM` . The whole network should be changed and the output format needs to be same as originals. 
