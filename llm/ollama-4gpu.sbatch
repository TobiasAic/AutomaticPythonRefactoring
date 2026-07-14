#!/bin/bash
# This is a SLURM batch script to start multiple Ollama servers on different GPUs and ports.
# It works in tandem with the ollama_llm.py class to provide concurrent LLM responses.
#SBATCH --job-name=ollama
#SBATCH --partition=gpu
#SBATCH --gres=gpu:4
#SBATCH --cpus-per-task=14
#SBATCH --time=04:00:00
#SBATCH --output=slurm-%j.out

set -euo pipefail

start_ollama() {
    local gpu=$1
    local port=$2

    echo "Starting GPU ${gpu} on port ${port}"

    CUDA_VISIBLE_DEVICES=${gpu} \
    OLLAMA_HOST=127.0.0.1:${port} \
    ollama serve \
        > ollama-gpu${gpu}.log 2>&1 &
}

start_ollama 0 11437
start_ollama 1 11438
start_ollama 2 11439
start_ollama 3 11440

trap 'kill $(jobs -p)' EXIT

echo "All servers started."

# Keep the job alive while any Ollama server is alive
wait
