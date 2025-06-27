#!/usr/bin/env python3
"""
SemEnhance Fine-tuning CLI wrapper
Provides a simplified interface for llamafactory-cli train commands
"""

import argparse
import subprocess
import sys
import os
import re
from pathlib import Path

def get_model_config_dir(model_name):
    """Map model names to their config directories"""
    model_mapping = {
        'deepseek-ai/deepseek-coder-6.7b-base': 'rq1_overview',
        'google/codegemma-2b': 'rq1_overview_codegemma',
        'meta-llama/Llama-3.2-1B': 'rq1_overview_llam32base',
        'meta-llama/Llama-3.1-8B': 'rq1_overview_llama318',
        # Add more model mappings as needed
    }
    
    # Check for exact match first
    if model_name in model_mapping:
        return model_mapping[model_name]
    
    # Fallback: try to match partial model names
    model_lower = model_name.lower()
    if 'codegemma' in model_lower or 'gemma' in model_lower:
        return 'rq1_overview_codegemma'
    elif 'llama-3.2' in model_lower or 'llam32' in model_lower:
        return 'rq1_overview_llam32base'
    elif 'llama-3.1' in model_lower or 'llama318' in model_lower:
        return 'rq1_overview_llama318'
    elif 'deepseek' in model_lower or 'coder' in model_lower:
        return 'rq1_overview'
    
    # Default fallback
    return 'rq1_overview'

def find_config_file(base_dir, model_name, dataset, trace_type, method, lora_rank=None):
    """Find the appropriate config file based on parameters"""
    
    # Get model-specific config directory
    model_config_dir = get_model_config_dir(model_name)
    
    # Build possible directory names with LoRA rank
    possible_dirs = [model_config_dir]
    
    if lora_rank:
        # Add LoRA-specific directories
        possible_dirs.extend([
            f"{model_config_dir}_lora{lora_rank}",
            f"rq1_overview_lora{lora_rank}",
            f"rq1_overview_lora{lora_rank}_a100"
        ])
    
    # Also try generic LoRA directories
    if lora_rank:
        possible_dirs.extend([
            f"rq1_overview_lora{lora_rank}",
            f"rq1_overview_lora{lora_rank}_a100"
        ])
    
    # Generate config filename patterns to search for
    patterns = []
    
    if method == 'baseline' and trace_type == 'none':
        # Baseline without trace
        if lora_rank:
            patterns.extend([
                f"rq1_lora{lora_rank}_rq1_notrace_baseline.yaml",
                f"rq1_lora{lora_rank}_rq1_notrace_baseline_tmp.yaml"
            ])
        patterns.extend([
            "rq1_full_rq1_notrace_baseline.yaml",
            "rq1_full_rq1_notrace_baseline_wrong.yaml"  # In case this is the only option
        ])
    
    elif method == 'full-trace' and trace_type == 'execution':
        # Full trace with execution - prioritize common formats
        trace_formats = ['our', 'concise', 'exe', 'naive', 'next', 
                        'semcoder_x', 'semcoder_y', 
                        'semcoder_rationale_x', 'semcoder_rationale_y']
        similarities = ['sim0.75', 'sim0', 'rnd']
        
        for fmt in trace_formats:
            for sim in similarities:
                if lora_rank:
                    patterns.extend([
                        f"rq1_lora{lora_rank}_rq1_tracefmt_{fmt}_{sim}.yaml",
                        f"rq1_lora{lora_rank}_rq1_tracefmt_{fmt}_{sim}-tmp.yaml"
                    ])
                patterns.extend([
                    f"rq1_full_rq1_tracefmt_{fmt}_{sim}.yaml",
                    f"rq1_full_rq1_tracefmt_{fmt}_{sim}-tmp.yaml"
                ])
    
    # Search for config files in multiple directories
    search_dirs = []
    
    for dir_name in possible_dirs:
        config_dir = os.path.join(base_dir, dir_name)
        if os.path.exists(config_dir):
            search_dirs.append(config_dir)
    
    # If no specific directories found, search all directories
    if not search_dirs and os.path.exists(base_dir):
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path):
                # Check if directory name contains relevant keywords
                item_lower = item.lower()
                model_keywords = model_config_dir.lower().split('_')
                if any(keyword in item_lower for keyword in model_keywords):
                    search_dirs.append(item_path)
                elif lora_rank and f"lora{lora_rank}" in item_lower:
                    search_dirs.append(item_path)
    
    # Search for matching files
    found_files = []
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            for pattern in patterns:
                config_file = os.path.join(search_dir, pattern)
                if os.path.exists(config_file):
                    found_files.append(config_file)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in found_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    
    return unique_files

def main():
    parser = argparse.ArgumentParser(
        prog='semenhance.finetune',
        description='SemEnhance fine-tuning wrapper for llamafactory-cli'
    )
    
    parser.add_argument('--model', type=str, required=True,
                       help='Model name (e.g., deepseek-ai/deepseek-coder-6.7b-base, google/codegemma-2b)')
    parser.add_argument('--dataset', type=str, default='mbpp',
                       help='Dataset name (default: mbpp)')
    parser.add_argument('--trace-type', type=str, choices=['execution', 'none'], 
                       default='execution', help='Trace type (default: execution)')
    parser.add_argument('--method', type=str, choices=['full-trace', 'baseline'],
                       default='full-trace', help='Training method (default: full-trace)')
    parser.add_argument('--lora-rank', type=int, choices=[8, 64],
                       help='LoRA rank (8 or 64)')
    parser.add_argument('--base-dir', type=str, 
                       default='finetune_src/LLaMA-Factory/examples/train_examples',
                       help='Base configuration directory path')
    parser.add_argument('--llamafactory-dir', type=str,
                       default='finetune_src/LLaMA-Factory',
                       help='LLaMA-Factory directory path')
    parser.add_argument('--list-configs', action='store_true',
                       help='List available configurations and exit')
    parser.add_argument('--dry-run', action='store_true',
                       help='Print the command without executing it')
    
    args = parser.parse_args()
    
    # Store the original working directory
    original_cwd = os.getcwd()
    
    # Check if LLaMA-Factory directory exists
    llamafactory_path = os.path.abspath(args.llamafactory_dir)
    if not os.path.exists(llamafactory_path):
        print(f"Error: LLaMA-Factory directory not found: {llamafactory_path}")
        print("Please make sure the path is correct or specify --llamafactory-dir")
        sys.exit(1)
    
    if args.list_configs:
        # List all available config files
        if os.path.exists(args.base_dir):
            print("Available configuration directories:")
            for item in sorted(os.listdir(args.base_dir)):
                item_path = os.path.join(args.base_dir, item)
                if os.path.isdir(item_path):
                    print(f"\n{item}:")
                    yaml_files = list(Path(item_path).glob("*.yaml"))
                    yaml_files = [f for f in yaml_files if not f.name.endswith('xxxx.yaml')]  # Filter out template files
                    for yaml_file in sorted(yaml_files):
                        print(f"  - {yaml_file.name}")
        else:
            print(f"Base directory not found: {args.base_dir}")
            print("Please make sure you're in the correct directory or specify --base-dir")
        return
    
    # Find matching config files
    config_files = find_config_file(args.base_dir, args.model, args.dataset, 
                                   args.trace_type, args.method, args.lora_rank)
    
    if not config_files:
        print(f"Error: No configuration file found for:")
        print(f"  Model: {args.model}")
        print(f"  Dataset: {args.dataset}")
        print(f"  Trace Type: {args.trace_type}")
        print(f"  Method: {args.method}")
        if args.lora_rank:
            print(f"  LoRA Rank: {args.lora_rank}")
        print(f"  Base Directory: {args.base_dir}")
        print(f"\nSearched in directories matching: {get_model_config_dir(args.model)}")
        print(f"\nUse --list-configs to see available configurations")
        
        # Show similar directories if available
        if os.path.exists(args.base_dir):
            similar_dirs = []
            model_keywords = get_model_config_dir(args.model).lower().split('_')
            for item in os.listdir(args.base_dir):
                item_path = os.path.join(args.base_dir, item)
                if os.path.isdir(item_path):
                    item_lower = item.lower()
                    if any(keyword in item_lower for keyword in model_keywords):
                        similar_dirs.append(item)
            
            if similar_dirs:
                print(f"\nSimilar directories found:")
                for dir_name in similar_dirs:
                    print(f"  - {dir_name}")
        
        sys.exit(1)
    
    # Use the first found config file
    config_path = config_files[0]
    
    if len(config_files) > 1:
        print(f"Multiple config files found, using: {config_path}")
        print("Other options:")
        for alt_config in config_files[1:]:
            print(f"  - {alt_config}")
        print()
    
    # Convert config path to relative path from LLaMA-Factory directory
    try:
        # Get the absolute path of the config file
        abs_config_path = os.path.abspath(config_path)
        # Get relative path from LLaMA-Factory directory
        rel_config_path = os.path.relpath(abs_config_path, llamafactory_path)
    except ValueError:
        # If relative path calculation fails, use absolute path
        rel_config_path = os.path.abspath(config_path)
    
    # Construct llamafactory-cli command
    cmd = [
        'llamafactory-cli',
        'train',
        rel_config_path
    ]
    
    print(f"SemEnhance Fine-tuning")
    print(f"Model: {args.model}")
    print(f"Dataset: {args.dataset}")  
    print(f"Trace Type: {args.trace_type}")
    print(f"Method: {args.method}")
    if args.lora_rank:
        print(f"LoRA Rank: {args.lora_rank}")
    print(f"Config: {config_path}")
    print(f"Working Directory: {llamafactory_path}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    if args.dry_run:
        print("Dry run - command would be:")
        print(f"cd {llamafactory_path}")
        print(' '.join(cmd))
        return
    
    try:
        # Change to LLaMA-Factory directory
        os.chdir(llamafactory_path)
        print(f"Changed working directory to: {os.getcwd()}")
        
        # Execute the command
        result = subprocess.run(cmd, check=True)
        print("Training completed successfully!")
        return result.returncode
        
    except subprocess.CalledProcessError as e:
        print(f"Error: Training failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Error: llamafactory-cli not found. Please ensure it's installed and in PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # Always restore original working directory
        os.chdir(original_cwd)

if __name__ == '__main__':
    main()

