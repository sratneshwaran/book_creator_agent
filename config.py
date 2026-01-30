import os

class Config:
    # vLLM Configuration
    # Example vLLM local URL: "http://localhost:8000/v1"
    VLLM_API_BASE = os.getenv("VLLM_API_BASE", "http://localhost:11434/v1") 
    VLLM_API_KEY = os.getenv("VLLM_API_KEY", "EMPTY") # Often 'EMPTY' for local vLLM
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-oss:20b") 
    
    # App Settings
    SECRET_KEY = os.urandom(24)