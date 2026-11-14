"""
FocusFlow ACLI - Model Rollback Utility
========================================
Provides safe rollback to previous model versions.
Maintains version history and allows quick recovery from problematic deployments.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import shutil
from datetime import datetime

from .registry import (
    get_approved_model_version,
    get_approved_model_metadata,
    REGISTRY_FILE,
    MODELS_DIR
)

ROLLBACK_HISTORY_FILE = Path(__file__).resolve().parent / "artifacts" / "rollback_history.json"


def get_available_versions() -> List[str]:
    """
    Get list of all available model versions that can be rolled back to.
    
    Returns:
        List of version strings, sorted newest to oldest
    """
    if not MODELS_DIR.exists():
        return []
    
    versions = []
    for version_dir in MODELS_DIR.iterdir():
        if version_dir.is_dir() and (version_dir / "model.joblib").exists():
            # Strip 'v' prefix if present
            version_name = version_dir.name
            if version_name.startswith('v'):
                version_name = version_name[1:]
            versions.append(version_name)
    
    # Sort by version number (semantic versioning)
    def version_key(v):
        try:
            parts = v.replace('v', '').split('.')
            return tuple(int(p) for p in parts)
        except:
            return (0, 0, 0)
    
    return sorted(versions, key=version_key, reverse=True)


def get_version_metadata(version: str) -> Optional[Dict[str, Any]]:
    """
    Get metadata for a specific model version.
    
    Args:
        version: Model version string (e.g., "1.0.2" or "v1.0.2")
        
    Returns:
        Metadata dictionary or None if not found
    """
    # Try with and without 'v' prefix
    version_clean = version.replace('v', '')
    
    for possible_version in [version, version_clean, f"v{version_clean}"]:
        metadata_path = MODELS_DIR / possible_version / "metadata.json"
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Rollback] Error reading metadata for {possible_version}: {e}")
    
    return None


def record_rollback(from_version: str, to_version: str, reason: str, user: str = "system"):
    """
    Record a rollback operation in history log.
    
    Args:
        from_version: Version being rolled back from
        to_version: Version being rolled back to
        reason: Reason for rollback
        user: Who initiated the rollback
    """
    ROLLBACK_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing history
    history = []
    if ROLLBACK_HISTORY_FILE.exists():
        try:
            with open(ROLLBACK_HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except:
            history = []
    
    # Add new entry
    entry = {
        "timestamp": datetime.now().isoformat(),
        "from_version": from_version,
        "to_version": to_version,
        "reason": reason,
        "user": user
    }
    history.append(entry)
    
    # Save updated history
    with open(ROLLBACK_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def get_rollback_history(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent rollback history.
    
    Args:
        limit: Maximum number of entries to return
        
    Returns:
        List of rollback entries, newest first
    """
    if not ROLLBACK_HISTORY_FILE.exists():
        return []
    
    try:
        with open(ROLLBACK_HISTORY_FILE, 'r') as f:
            history = json.load(f)
        return history[-limit:][::-1]  # Last N entries, reversed
    except Exception as e:
        print(f"[Rollback] Error reading history: {e}")
        return []


def rollback_model(
    to_version: str,
    reason: str = "Manual rollback",
    user: str = "system",
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Rollback to a specific model version.
    
    Args:
        to_version: Target version to roll back to
        reason: Reason for rollback
        user: Who is performing the rollback
        dry_run: If True, simulate without making changes
        
    Returns:
        Dictionary with rollback result
    """
    # Validation
    current_version = get_approved_model_version()
    if not current_version:
        return {
            "success": False,
            "error": "No current model version found"
        }
    
    if current_version == to_version:
        return {
            "success": False,
            "error": f"Already on version {to_version}"
        }
    
    # Check if target version exists
    target_path = MODELS_DIR / to_version
    if not target_path.exists() or not (target_path / "model.joblib").exists():
        available = get_available_versions()
        return {
            "success": False,
            "error": f"Version {to_version} not found. Available: {', '.join(available)}"
        }
    
    # Get metadata for both versions
    current_meta = get_approved_model_metadata()
    target_meta = get_version_metadata(to_version)
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "from_version": current_version,
            "to_version": to_version,
            "current_metrics": current_meta.get("metrics") if current_meta else None,
            "target_metrics": target_meta.get("metrics") if target_meta else None,
            "message": f"[DRY RUN] Would rollback from {current_version} → {to_version}"
        }
    
    # Perform rollback by updating registry
    try:
        # Backup current registry
        backup_path = REGISTRY_FILE.parent / f"registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy2(REGISTRY_FILE, backup_path)
        
        # Load registry
        with open(REGISTRY_FILE, 'r') as f:
            registry = json.load(f)
        
        # Update approved version
        registry["approved_version"] = to_version
        registry["last_updated"] = datetime.now().isoformat()
        
        # Save updated registry
        with open(REGISTRY_FILE, 'w') as f:
            json.dump(registry, f, indent=2)
        
        # Record in history
        record_rollback(current_version, to_version, reason, user)
        
        print(f"[Rollback] ✅ Successfully rolled back: {current_version} → {to_version}")
        print(f"[Rollback] Registry backup saved to: {backup_path}")
        print(f"[Rollback] ⚠️  Restart application to load version {to_version}")
        
        return {
            "success": True,
            "from_version": current_version,
            "to_version": to_version,
            "reason": reason,
            "backup_path": str(backup_path),
            "current_metrics": current_meta.get("metrics") if current_meta else None,
            "target_metrics": target_meta.get("metrics") if target_meta else None,
            "message": f"Rolled back from {current_version} → {to_version}. Restart required."
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Rollback failed: {str(e)}"
        }


def compare_versions(version1: str, version2: str) -> Dict[str, Any]:
    """
    Compare metrics between two model versions.
    
    Args:
        version1: First version
        version2: Second version
        
    Returns:
        Comparison dictionary
    """
    meta1 = get_version_metadata(version1)
    meta2 = get_version_metadata(version2)
    
    if not meta1 or not meta2:
        return {
            "error": "One or both versions not found",
            "version1": version1,
            "version2": version2,
            "version1_exists": meta1 is not None,
            "version2_exists": meta2 is not None
        }
    
    metrics1 = meta1.get("metrics", {})
    metrics2 = meta2.get("metrics", {})
    
    comparison = {
        "version1": version1,
        "version2": version2,
        "metrics": {}
    }
    
    # Compare key metrics
    for metric in ["accuracy", "macro_f1", "macro_precision", "macro_recall"]:
        val1 = metrics1.get(metric, 0.0)
        val2 = metrics2.get(metric, 0.0)
        diff = val2 - val1
        
        comparison["metrics"][metric] = {
            "version1": val1,
            "version2": val2,
            "difference": diff,
            "percent_change": (diff / val1 * 100) if val1 > 0 else 0.0
        }
    
    # Determine which is better
    accuracy_diff = comparison["metrics"]["accuracy"]["difference"]
    f1_diff = comparison["metrics"]["macro_f1"]["difference"]
    
    if accuracy_diff > 0.01 and f1_diff > 0.01:
        comparison["recommendation"] = f"{version2} is better (higher accuracy and F1)"
    elif accuracy_diff < -0.01 and f1_diff < -0.01:
        comparison["recommendation"] = f"{version1} is better (higher accuracy and F1)"
    else:
        comparison["recommendation"] = "Performance is similar"
    
    return comparison


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Model rollback utility")
    parser.add_argument("--to-version", type=str, help="Target version to roll back to")
    parser.add_argument("--list", action="store_true", help="List available versions")
    parser.add_argument("--history", action="store_true", help="Show rollback history")
    parser.add_argument("--compare", nargs=2, metavar=("V1", "V2"), help="Compare two versions")
    parser.add_argument("--reason", type=str, default="Manual rollback", help="Reason for rollback")
    parser.add_argument("--user", type=str, default="cli", help="User performing rollback")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without making changes")
    
    args = parser.parse_args()
    
    if args.list:
        print("\n📦 Available Model Versions:")
        print("=" * 60)
        
        current = get_approved_model_version()
        versions = get_available_versions()
        
        for version in versions:
            marker = "✅ CURRENT" if version == current else ""
            meta = get_version_metadata(version)
            
            if meta:
                acc = meta.get("metrics", {}).get("accuracy", 0.0)
                f1 = meta.get("metrics", {}).get("macro_f1", 0.0)
                trained = meta.get("trained_at", "unknown")[:10]
                print(f"  v{version:8s} - Acc: {acc:.2%}, F1: {f1:.2%} (trained: {trained}) {marker}")
            else:
                print(f"  v{version:8s} - Metadata not found")
        
        print("=" * 60)
    
    elif args.history:
        print("\n📜 Rollback History:")
        print("=" * 60)
        
        history = get_rollback_history(limit=20)
        
        if not history:
            print("  No rollback history found")
        else:
            for entry in history:
                timestamp = entry["timestamp"][:19]
                from_v = entry["from_version"]
                to_v = entry["to_version"]
                reason = entry["reason"]
                user = entry.get("user", "unknown")
                print(f"  {timestamp} - {from_v} → {to_v}")
                print(f"    Reason: {reason} (by {user})")
        
        print("=" * 60)
    
    elif args.compare:
        v1, v2 = args.compare
        print(f"\n📊 Comparing v{v1} vs v{v2}:")
        print("=" * 60)
        
        comp = compare_versions(v1, v2)
        
        if "error" in comp:
            print(f"  Error: {comp['error']}")
        else:
            for metric, data in comp["metrics"].items():
                val1 = data["version1"]
                val2 = data["version2"]
                diff = data["difference"]
                pct = data["percent_change"]
                
                arrow = "↑" if diff > 0 else "↓" if diff < 0 else "="
                print(f"  {metric:20s}: {val1:.4f} → {val2:.4f} ({arrow} {diff:+.4f}, {pct:+.2f}%)")
            
            print()
            print(f"  Recommendation: {comp['recommendation']}")
        
        print("=" * 60)
    
    elif args.to_version:
        print(f"\n🔄 Rolling back to version {args.to_version}...")
        print("=" * 60)
        
        result = rollback_model(
            to_version=args.to_version,
            reason=args.reason,
            user=args.user,
            dry_run=args.dry_run
        )
        
        if result["success"]:
            print(f"  ✅ {result['message']}")
            
            if result.get("dry_run"):
                print("\n  This was a DRY RUN. No changes were made.")
            
            if result.get("current_metrics") and result.get("target_metrics"):
                print("\n  Metrics Comparison:")
                curr_acc = result["current_metrics"].get("accuracy", 0.0)
                targ_acc = result["target_metrics"].get("accuracy", 0.0)
                curr_f1 = result["current_metrics"].get("macro_f1", 0.0)
                targ_f1 = result["target_metrics"].get("macro_f1", 0.0)
                
                print(f"    Accuracy: {curr_acc:.2%} → {targ_acc:.2%}")
                print(f"    Macro F1: {curr_f1:.2%} → {targ_f1:.2%}")
        else:
            print(f"  ❌ Error: {result['error']}")
        
        print("=" * 60)
    
    else:
        parser.print_help()
