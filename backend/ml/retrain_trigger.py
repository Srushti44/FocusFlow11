"""
FocusFlow ACLI - Automated Retraining Trigger Logic
===================================================
Determines when model retraining is needed based on:
1. Data drift (PSI threshold exceeded)
2. Time-based schedule (max days without retraining)
3. Performance degradation (optional monitoring)
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import json

from .monitoring import get_monitoring_summary, DRIFT_THRESHOLD
from .registry import get_approved_model_metadata, get_approved_model_version

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
RETRAIN_STATE_FILE = ARTIFACTS_DIR / "retrain_state.json"

# Retraining policy thresholds
MAX_DAYS_WITHOUT_RETRAIN = 30  # Maximum days before forced retraining
MIN_DAYS_BETWEEN_RETRAINS = 3   # Minimum cooldown between retraining runs
DRIFT_RETRAIN_THRESHOLD = 0.2    # PSI threshold to trigger retraining (higher than alert threshold)


def get_days_since_last_training() -> int:
    """
    Calculate days since last successful training run.
    
    Returns:
        Number of days since training, or 999 if never trained
    """
    try:
        metadata = get_approved_model_metadata()
        if not metadata:
            return 999  # No model exists, needs training
        
        trained_at = metadata.get("trained_at")
        if not trained_at:
            return 999
        
        # Parse ISO format timestamp
        trained_date = datetime.fromisoformat(trained_at.replace('Z', '+00:00'))
        days_elapsed = (datetime.now(trained_date.tzinfo) - trained_date).days
        
        return max(0, days_elapsed)
    except Exception as e:
        print(f"[Retrain] Warning: Could not determine training date: {e}")
        return 999


def get_latest_drift_score() -> float:
    """
    Get the maximum PSI score from recent monitoring data.
    
    Returns:
        Maximum PSI value across all features, or 0.0 if no data
    """
    try:
        summary = get_monitoring_summary(days=7)  # Last 7 days
        if not summary or "feature_psi_max" not in summary:
            return 0.0
        
        return summary["feature_psi_max"]
    except Exception as e:
        print(f"[Retrain] Warning: Could not retrieve drift score: {e}")
        return 0.0


def get_last_retrain_attempt() -> Optional[datetime]:
    """
    Get timestamp of last retraining attempt (successful or not).
    
    Returns:
        Datetime of last attempt, or None if never attempted
    """
    if not RETRAIN_STATE_FILE.exists():
        return None
    
    try:
        with open(RETRAIN_STATE_FILE, 'r') as f:
            state = json.load(f)
        
        last_attempt = state.get("last_attempt")
        if last_attempt:
            return datetime.fromisoformat(last_attempt)
    except Exception as e:
        print(f"[Retrain] Warning: Could not read retrain state: {e}")
    
    return None


def record_retrain_attempt(success: bool, reason: str, new_version: Optional[str] = None):
    """
    Record a retraining attempt in state file.
    
    Args:
        success: Whether retraining succeeded
        reason: Reason for retraining
        new_version: New model version if successful
    """
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    
    state = {
        "last_attempt": datetime.now().isoformat(),
        "last_success": success,
        "last_reason": reason,
        "last_version": new_version
    }
    
    with open(RETRAIN_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def should_retrain(verbose: bool = True) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Determine if model retraining should be triggered.
    
    Args:
        verbose: Whether to print decision reasoning
        
    Returns:
        (should_retrain, reason, context_dict)
    """
    context = {}
    
    # 1. Check cooldown period
    last_attempt = get_last_retrain_attempt()
    if last_attempt:
        days_since_attempt = (datetime.now() - last_attempt).days
        context["days_since_last_attempt"] = days_since_attempt
        
        if days_since_attempt < MIN_DAYS_BETWEEN_RETRAINS:
            # Still populate required fields even during cooldown
            context["days_since_training"] = get_days_since_last_training()
            context["max_days_threshold"] = MAX_DAYS_WITHOUT_RETRAIN
            context["latest_psi"] = get_latest_drift_score()
            context["drift_threshold"] = DRIFT_RETRAIN_THRESHOLD
            
            reason = f"Cooldown period active ({days_since_attempt}/{MIN_DAYS_BETWEEN_RETRAINS} days since last attempt)"
            if verbose:
                print(f"[Retrain] ❌ {reason}")
            return False, reason, context
    else:
        context["days_since_last_attempt"] = 999
    
    # 2. Check time since last successful training
    days_since_training = get_days_since_last_training()
    context["days_since_training"] = days_since_training
    context["max_days_threshold"] = MAX_DAYS_WITHOUT_RETRAIN
    
    if days_since_training >= MAX_DAYS_WITHOUT_RETRAIN:
        # Populate remaining context fields
        context["latest_psi"] = get_latest_drift_score()
        context["drift_threshold"] = DRIFT_RETRAIN_THRESHOLD
        
        reason = f"Time-based trigger: {days_since_training} days since last training (max: {MAX_DAYS_WITHOUT_RETRAIN})"
        if verbose:
            print(f"[Retrain] ✅ {reason}")
        context["trigger"] = "time_based"
        return True, reason, context
    
    # 3. Check drift score
    latest_drift = get_latest_drift_score()
    context["latest_psi"] = latest_drift
    context["drift_threshold"] = DRIFT_RETRAIN_THRESHOLD
    
    if latest_drift > DRIFT_RETRAIN_THRESHOLD:
        reason = f"Drift-based trigger: PSI={latest_drift:.4f} exceeds threshold {DRIFT_RETRAIN_THRESHOLD}"
        if verbose:
            print(f"[Retrain] ✅ {reason}")
        context["trigger"] = "drift_based"
        return True, reason, context
    
    # 4. No triggers activated
    reason = f"No retraining needed (days: {days_since_training}/{MAX_DAYS_WITHOUT_RETRAIN}, drift: {latest_drift:.4f}/{DRIFT_RETRAIN_THRESHOLD})"
    if verbose:
        print(f"[Retrain] ℹ️  {reason}")
    context["trigger"] = None
    
    return False, reason, context


def format_retrain_decision(should_retrain_flag: bool, reason: str, context: Dict[str, Any]) -> str:
    """
    Format retraining decision as human-readable summary.
    
    Returns:
        Formatted markdown string
    """
    lines = []
    lines.append("# Automated Retraining Decision")
    lines.append("")
    
    # Decision
    if should_retrain_flag:
        lines.append("## ✅ RETRAIN RECOMMENDED")
    else:
        lines.append("## ❌ NO RETRAINING NEEDED")
    
    lines.append("")
    lines.append(f"**Reason:** {reason}")
    lines.append("")
    
    # Context details
    lines.append("## Context")
    lines.append("")
    lines.append(f"- **Days since training:** {context.get('days_since_training', 'unknown')}")
    lines.append(f"- **Max days threshold:** {context.get('max_days_threshold', MAX_DAYS_WITHOUT_RETRAIN)}")
    lines.append(f"- **Latest PSI score:** {context.get('latest_psi', 0.0):.4f}")
    lines.append(f"- **Drift threshold:** {context.get('drift_threshold', DRIFT_RETRAIN_THRESHOLD)}")
    
    if context.get("days_since_last_attempt") is not None:
        lines.append(f"- **Days since last attempt:** {context['days_since_last_attempt']}")
    
    lines.append("")
    
    # Current model info
    current_version = get_approved_model_version()
    if current_version:
        lines.append(f"**Current production model:** v{current_version}")
    
    lines.append("")
    
    # Recommendation
    if should_retrain_flag:
        trigger_type = context.get("trigger", "unknown")
        lines.append("### Recommended Actions")
        lines.append("")
        lines.append("1. Trigger model retraining workflow")
        lines.append("2. Review training metrics and approval criteria")
        lines.append("3. Test new model before production deployment")
        lines.append(f"4. Document reason: `{trigger_type}`")
    else:
        lines.append("### Status")
        lines.append("")
        lines.append("Model is performing within acceptable parameters. Continue monitoring.")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Check if model retraining should be triggered")
    parser.add_argument("--dry-run", action="store_true", help="Show decision without recording attempt")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    # Make decision
    should_retrain_flag, reason, context = should_retrain(verbose=not args.quiet)
    
    # Format output
    if args.format == "json":
        import json
        output = {
            "should_retrain": should_retrain_flag,
            "reason": reason,
            "context": context
        }
        print(json.dumps(output, indent=2))
    elif args.format == "markdown":
        print(format_retrain_decision(should_retrain_flag, reason, context))
    else:
        # Text format
        status = "RETRAIN" if should_retrain_flag else "SKIP"
        print(f"\n{'='*60}")
        print(f"Decision: {status}")
        print(f"Reason: {reason}")
        print(f"{'='*60}\n")
    
    # Exit code: 0 = retrain needed, 1 = no retrain needed
    exit_code = 0 if should_retrain_flag else 1
    
    if not args.quiet:
        print(f"Exit code: {exit_code} ({'retrain' if exit_code == 0 else 'skip'})")
    
    exit(exit_code)
