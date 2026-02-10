"""
Database Initialization Script
Sets up initial data structures and canon memory.
"""

import os
import json
from app.core.config import settings

def init_data_directories():
    """Initialize data directories for file-based storage"""
    directories = [
        settings.DATA_DIR,
        settings.USER_PREFERENCES_PATH,
        settings.SESSION_MEMORY_PATH,
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def init_canon_memory():
    """Initialize canon memory with default values"""
    if os.path.exists(settings.CANON_MEMORY_PATH):
        print(f"⚠ Canon memory already exists at {settings.CANON_MEMORY_PATH}")
        return
    
    canon_data = {
        "system_knowledge": {
            "developer": "VelaPlex Systems",
            "application": "Souent",
            "purpose": "Logic-first AI chatbot powered by Souent Logic Models"
        },
        "model_info": {
            "current_model": "SLM-A1",
            "model_name": "Anthroi-1",
            "version": "1.0.0",
            "characteristics": [
                "Logic-first reasoning",
                "Conservative inference",
                "Explicit uncertainty handling",
                "No emotional simulation",
                "No immersive roleplay"
            ],
            "capabilities": [
                "Question answering with uncertainty markers",
                "Code analysis and debugging",
                "Technical documentation analysis",
                "Problem-solving and strategic thinking",
                "Data analysis and interpretation"
            ]
        },
        "locked": True,
        "version": "1.0.0"
    }
    
    os.makedirs(os.path.dirname(settings.CANON_MEMORY_PATH), exist_ok=True)
    
    with open(settings.CANON_MEMORY_PATH, 'w') as f:
        json.dump(canon_data, f, indent=2)
    
    print(f"✓ Initialized canon memory at {settings.CANON_MEMORY_PATH}")


def main():
    """Main initialization function"""
    print("=" * 60)
    print("Souent Database Initialization")
    print("=" * 60)
    print()
    
    print("Initializing data directories...")
    init_data_directories()
    print()
    
    print("Initializing canon memory...")
    init_canon_memory()
    print()
    
    print("=" * 60)
    print("✓ Initialization complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
