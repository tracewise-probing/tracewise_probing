#!/bin/bash

# Configuration with defaults
YAML_FILE="${YAML_FILE:-examples/train_examples/rq1_overview/rq1_full_rq1_notrace_baseline.yaml}"
CUDA_DEVICES="${CUDA_DEVICES:-0,1}"
NUM_ROUNDS="${NUM_ROUNDS:-5}"

# Check if YAML file exists
if [ ! -f "$YAML_FILE" ]; then
    echo "Error: YAML file '$YAML_FILE' not found"
    echo "Usage: YAML_FILE=path/to/config.yaml [other_params=value] bash run_5_times.sh"
    exit 1
fi

# Extract base output directory from YAML file
BASE_OUTPUT_DIR=$(grep "^output_dir:" "$YAML_FILE" | cut -d':' -f2 | sed 's/^ *//' | sed 's/ *$//')

if [ -z "$BASE_OUTPUT_DIR" ]; then
    echo "Error: Could not extract output_dir from $YAML_FILE"
    exit 1
fi

# Collect all additional parameters from environment variables
# Common training parameters that might be passed as environment variables
ADDITIONAL_ARGS=""

# List of common parameters to check for
PARAM_NAMES=(
    "per_device_train_batch_size"
    "per_device_eval_batch_size"
    "learning_rate"
    "num_train_epochs"
    "max_steps"
    "warmup_steps"
    "logging_steps"
    "save_steps"
    "eval_steps"
    "gradient_accumulation_steps"
    "dataloader_num_workers"
    "fp16"
    "bf16"
    "gradient_checkpointing"
    "overwrite_output_dir"
    "save_only_model"
    "save_total_limit"
    "resume_from_checkpoint"
)

# Build additional arguments string from environment variables
for param in "${PARAM_NAMES[@]}"; do
    if [ -n "${!param}" ]; then
        ADDITIONAL_ARGS="$ADDITIONAL_ARGS $param=${!param}"
    fi
done

echo "YAML file: $YAML_FILE"
echo "CUDA devices: $CUDA_DEVICES"
echo "Number of rounds: $NUM_ROUNDS"
echo "Base output directory: $BASE_OUTPUT_DIR"
if [ -n "$ADDITIONAL_ARGS" ]; then
    echo "Additional parameters:$ADDITIONAL_ARGS"
fi
echo "Running $NUM_ROUNDS training rounds..."
echo "----------------------------------------"

# Run training for each round
for i in $(seq 1 $NUM_ROUNDS); do
    echo "Starting training round $i..."
    
    # Create output directory path for this round
    OUTPUT_DIR="${BASE_OUTPUT_DIR}_rnd${i}"
    mkdir -p "$OUTPUT_DIR"
    
    echo "Output directory: $OUTPUT_DIR"
    
    # Build the complete command
    CMD="CUDA_VISIBLE_DEVICES=$CUDA_DEVICES llamafactory-cli train \"$YAML_FILE\" output_dir=\"$OUTPUT_DIR\" seed=$i resume_from_checkpoint=false save_total_limit=1 save_only_model=true overwrite_output_dir=false "
    
    # Add additional arguments if any
    if [ -n "$ADDITIONAL_ARGS" ]; then
        CMD="$CMD$ADDITIONAL_ARGS"
    fi
    
    echo "Running: $CMD"
    
    # Execute the command
    eval $CMD
    
    # Check if training was successful
    if [ $? -eq 0 ]; then
        echo "✓ Training round $i completed successfully"
    else
        echo "✗ Training round $i failed"
        exit 1
    fi
    
    echo "----------------------------------------"
done

echo "All $NUM_ROUNDS training rounds completed!"

