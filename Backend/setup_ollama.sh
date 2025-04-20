#!/bin/bash

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Installing Ollama..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux installation
        curl -fsSL https://ollama.com/install.sh | sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS installation
        brew install ollama
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows installation
        echo "Please install Ollama manually from https://ollama.com/download"
        exit 1
    else
        echo "Unsupported OS. Please install Ollama manually from https://ollama.com/download"
        exit 1
    fi
else
    echo "Ollama is already installed."
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    # Wait for Ollama to start
    sleep 5
fi

# Pull the DeepSeek model
echo "Pulling DeepSeek-R1-Distill-Llama-8B model... This may take a while."
ollama pull deepseek-ai/deepseek-r1-distill-llama-8b

echo "Setup complete! Ollama is running with DeepSeek-R1-Distill-Llama-8B model."
echo "You can now run the backend server." 