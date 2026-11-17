"""
Complete MLOps Demo Script for Professor
Run this single script to see all MLOps capabilities
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def demo_model_registry():
    """1. Model Registry & Versioning"""
    print_header("1️⃣  MODEL REGISTRY & VERSIONING")
    
    registry_path = Path("backend/ml/artifacts/registry.json")
    if not registry_path.exists():
        print("❌ Registry not found")
        return
    
    with open(registry_path) as f:
        data = json.load(f)
    
    models = data.get("models", {})
    print(f"\n📦 Total Versions: {len(models)}")
    
    for version, info in sorted(models.items()):
        status = info.get("status", "unknown")
        status_icon = "✅" if status == "approved" else "⏳"
        accuracy = info.get("metrics", {}).get("accuracy", "N/A")
        f1 = info.get("metrics", {}).get("f1_score", "N/A")
        
        print(f"\n{status_icon} {version}")
        print(f"   Status: {status}")
        print(f"   Accuracy: {accuracy}")
        print(f"   F1 Score: {f1}")
    
    current = data.get("current_production", "unknown")
    print(f"\n🎯 Production Model: {current}")

def demo_mlflow():
    """2. MLflow Experiment Tracking"""
    print_header("2️⃣  MLFLOW EXPERIMENT TRACKING")
    
    db_path = Path("backend/ml/artifacts/mlflow.db")
    if not db_path.exists():
        print("❌ MLflow DB not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM runs WHERE lifecycle_stage='active'")
    total_runs = cursor.fetchone()[0]
    
    print(f"\n🧪 Total Training Runs: {total_runs}")
    
    cursor.execute("""
        SELECT r.run_uuid, m.key, m.value
        FROM runs r
        JOIN metrics m ON r.run_uuid = m.run_uuid
        WHERE r.lifecycle_stage='active' AND m.key='accuracy'
        ORDER BY m.value DESC
        LIMIT 3
    """)
    
    print("\n🏆 Top 3 Models by Accuracy:")
    for i, (run_id, key, value) in enumerate(cursor.fetchall(), 1):
        print(f"   {i}. Run {run_id[:8]}... → Accuracy: {value:.4f}")
    
    conn.close()

def demo_drift_monitoring():
    """3. Drift Monitoring"""
    print_header("3️⃣  DRIFT MONITORING (PSI)")
    
    db_path = Path("backend/ml/artifacts/ml_monitoring.db")
    if not db_path.exists():
        print("❌ Monitoring DB not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*), AVG(psi_score), MAX(psi_score)
        FROM predictions
    """)
    
    row = cursor.fetchone()
    if row and row[0] > 0:
        count, avg_psi, max_psi = row
        print(f"\n📊 Predictions Monitored: {count}")
        print(f"📈 Average PSI Score: {avg_psi:.4f}")
        print(f"📈 Max PSI Score: {max_psi:.4f}")
        
        threshold = 0.2
        if max_psi > threshold:
            print(f"\n⚠️  DRIFT DETECTED (PSI > {threshold})")
        else:
            print(f"\n✅ No Significant Drift")
    else:
        print("\n📊 No predictions recorded yet")
    
    conn.close()

def demo_ci_cd():
    """4. CI/CD Workflows"""
    print_header("4️⃣  CI/CD GITHUB ACTIONS")
    
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("❌ Workflows directory not found")
        return
    
    workflows = list(workflows_dir.glob("*.yml"))
    print(f"\n⚙️  Total Workflows: {len(workflows)}")
    
    for wf in workflows:
        print(f"   ✓ {wf.stem}")

def demo_testing():
    """5. Automated Testing"""
    print_header("5️⃣  AUTOMATED TESTING")
    
    import subprocess
    import sys
    
    print("\n🧪 Running pytest suite...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "backend/tests/", "-v", "--tb=no", "-q"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    
    # Parse output
    output = result.stdout
    if "passed" in output:
        # Extract test results
        lines = output.split("\n")
        for line in lines:
            if "passed" in line:
                print(f"\n✅ {line.strip()}")
                break
    else:
        print("\n⚠️  Run 'pytest backend/tests/ -v' manually")

def demo_docker():
    """6. Docker Containerization"""
    print_header("6️⃣  DOCKER CONTAINERIZATION")
    
    if Path("Dockerfile.backend").exists():
        print("\n✅ Dockerfile.backend exists")
    if Path("docker-compose.yml").exists():
        print("✅ docker-compose.yml exists")
    
    print("\n📦 To run containers:")
    print("   docker-compose up -d")

def demo_rollback():
    """7. Model Rollback Capability"""
    print_header("7️⃣  MODEL ROLLBACK CAPABILITY")
    
    registry_path = Path("backend/ml/artifacts/registry.json")
    if not registry_path.exists():
        print("❌ Registry not found")
        return
    
    with open(registry_path) as f:
        data = json.load(f)
    
    versions = list(data.get("models", {}).keys())
    print(f("\n🔄 Rollback Available to {len(versions)} versions:")
    for v in sorted(versions):
        print(f"   • {v}")
    
    print("\n💡 Command: python backend/ml/rollback.py --version v1.0.2 --dry-run")

def main():
    """Run complete MLOps demo"""
    print("\n" + "🎓" * 35)
    print(" " * 15 + "MLOPS COMPLETE DEMO")
    print("🎓" * 35)
    
    demo_model_registry()
    demo_mlflow()
    demo_drift_monitoring()
    demo_ci_cd()
    demo_testing()
    demo_docker()
    demo_rollback()
    
    print("\n" + "="*70)
    print("✅ MLOps Demo Complete!")
    print("="*70)
    print("\n📍 Live Services:")
    print("   • Frontend: http://localhost:5173")
    print("   • Backend API: http://localhost:8000/docs")
    print("   • MLflow UI: http://localhost:5000")
    print("\n")

if __name__ == "__main__":
    main()
