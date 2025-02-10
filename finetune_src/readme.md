
# Fine-Tuning Guide

## How to Fine-Tune

To fine-tune the model, use the following command:

```bash
llamafactory-cli train examples/train_lora/llama3_lora_sft.yaml
```

## Reproducibility Logs

We have uploaded the fine-tuning logs to GitHub to facilitate reproducibility. 

Please refer to the logs in the `saves_ijcai` directory.

## Training Dataset

The dataset can be downloaded from Google Drive.

Additionally, we have provided a script to curate the trace-rich full dataset. You can find this script in the root folder, named `curate_trace_dataset`.
