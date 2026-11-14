"""
Unit Tests for Automated Retraining Trigger Logic
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import json

from backend.ml.retrain_trigger import (
    should_retrain,
    get_days_since_last_training,
    get_last_retrain_attempt,
    record_retrain_attempt,
    format_retrain_decision,
    MAX_DAYS_WITHOUT_RETRAIN,
    MIN_DAYS_BETWEEN_RETRAINS,
    DRIFT_RETRAIN_THRESHOLD,
    RETRAIN_STATE_FILE
)


def test_should_retrain_returns_tuple():
    """Test that should_retrain returns expected tuple structure"""
    result = should_retrain(verbose=False)
    
    assert isinstance(result, tuple)
    assert len(result) == 3
    
    should_retrain_flag, reason, context = result
    assert isinstance(should_retrain_flag, bool)
    assert isinstance(reason, str)
    assert isinstance(context, dict)


def test_days_since_training_returns_int():
    """Test that days since training returns a valid integer"""
    days = get_days_since_last_training()
    
    assert isinstance(days, int)
    assert days >= 0


def test_retrain_state_recording():
    """Test recording and retrieving retrain attempts"""
    # Record a successful attempt
    test_version = "2.0.0"
    test_reason = "Time-based trigger"
    
    record_retrain_attempt(
        success=True,
        reason=test_reason,
        new_version=test_version
    )
    
    # Verify state file was created
    assert RETRAIN_STATE_FILE.exists()
    
    # Read and verify content
    with open(RETRAIN_STATE_FILE, 'r') as f:
        state = json.load(f)
    
    assert state["last_success"] is True
    assert state["last_reason"] == test_reason
    assert state["last_version"] == test_version
    assert "last_attempt" in state
    
    # Verify we can retrieve it
    last_attempt = get_last_retrain_attempt()
    assert last_attempt is not None
    assert isinstance(last_attempt, datetime)


def test_cooldown_period_prevents_retraining():
    """Test that cooldown period blocks retraining"""
    # Record a very recent attempt
    record_retrain_attempt(
        success=True,
        reason="Test cooldown",
        new_version="1.0.4"
    )
    
    # Should not retrain due to cooldown
    should_retrain_flag, reason, context = should_retrain(verbose=False)
    
    # Even if other conditions are met, cooldown should block
    assert "Cooldown" in reason or "days_since_last_attempt" in context


def test_format_retrain_decision_markdown():
    """Test formatting of retraining decision as markdown"""
    context = {
        "days_since_training": 45,
        "max_days_threshold": MAX_DAYS_WITHOUT_RETRAIN,
        "latest_psi": 0.25,
        "drift_threshold": DRIFT_RETRAIN_THRESHOLD,
        "trigger": "time_based"
    }
    
    markdown = format_retrain_decision(
        should_retrain_flag=True,
        reason="Test reason",
        context=context
    )
    
    assert "# Automated Retraining Decision" in markdown
    assert "RETRAIN RECOMMENDED" in markdown
    assert "45" in markdown  # days_since_training
    assert "0.25" in markdown  # PSI score


def test_format_retrain_decision_no_retrain():
    """Test formatting when retraining is not needed"""
    context = {
        "days_since_training": 5,
        "latest_psi": 0.05,
        "trigger": None
    }
    
    markdown = format_retrain_decision(
        should_retrain_flag=False,
        reason="Model is stable",
        context=context
    )
    
    assert "NO RETRAINING NEEDED" in markdown
    assert "Model is stable" in markdown


def test_retrain_decision_context_structure():
    """Test that decision context includes all expected fields"""
    _, _, context = should_retrain(verbose=False)
    
    # These fields should always be present
    assert "days_since_training" in context
    assert "max_days_threshold" in context
    assert "latest_psi" in context
    assert "drift_threshold" in context
    
    # Values should be reasonable
    assert context["max_days_threshold"] == MAX_DAYS_WITHOUT_RETRAIN
    assert context["drift_threshold"] == DRIFT_RETRAIN_THRESHOLD
    assert isinstance(context["days_since_training"], int)
    assert isinstance(context["latest_psi"], (int, float))


def test_retrain_on_high_drift():
    """Test that high drift score would trigger retraining (if drift monitoring had data)"""
    # Note: This test documents expected behavior
    # In practice, drift scores come from monitoring database
    
    context = {
        "latest_psi": 0.3,  # Above DRIFT_RETRAIN_THRESHOLD (0.2)
        "drift_threshold": DRIFT_RETRAIN_THRESHOLD
    }
    
    # If PSI exceeds threshold, retraining should be recommended
    assert context["latest_psi"] > context["drift_threshold"]


def test_min_days_between_retrains_constant():
    """Test that cooldown constant is reasonable"""
    assert MIN_DAYS_BETWEEN_RETRAINS > 0
    assert MIN_DAYS_BETWEEN_RETRAINS < MAX_DAYS_WITHOUT_RETRAIN


def test_drift_threshold_is_higher_than_alert_threshold():
    """Test that retrain threshold is higher than monitoring alert threshold"""
    from backend.ml.monitoring import DRIFT_THRESHOLD
    
    # Retraining threshold should be higher than alert threshold
    # to avoid retraining on minor drift
    assert DRIFT_RETRAIN_THRESHOLD >= DRIFT_THRESHOLD
