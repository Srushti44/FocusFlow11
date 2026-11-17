"""Demo script to show model registry - works standalone"""
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def show_registry():
    """Show all models in registry"""
    registry_path = Path(__file__).parent / "artifacts" / "registry.json"
    
    if not registry_path.exists():
        print("❌ Registry file not found")
        return
    
    with open(registry_path) as f:
        data = json.load(f)
    
    print("\n" + "="*60)
    print("📦 MODEL REGISTRY - ALL VERSIONS")
    print("="*60)
    
    models = data.get("models", {})
    for version, info in sorted(models.items()):
        status_icon = "✅" if info.get("status") == "approved" else "⏳"
        print(f"\n{status_icon} Version: {version}")
        print(f"   Status: {info.get('status', 'unknown')}")
        print(f"   Accuracy: {info.get('metrics', {}).get('accuracy', 'N/A')}")
        print(f("   F1 Score: {info.get('metrics', {}).get('f1_score', 'N/A')}")
        print(f"   Trained: {info.get('timestamp', 'N/A')}")
    
    current = data.get("current_production", "unknown")
    print(f"\n🎯 Current Production Model: {current}")
    print("="*60 + "\n")

if __name__ == "__main__":
    show_registry()
