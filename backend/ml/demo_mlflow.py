"""Demo script to show MLflow experiments - works standalone"""
import sqlite3
from pathlib import Path

def show_mlflow_experiments():
    """Show all MLflow experiments and runs"""
    db_path = Path(__file__).parent / "artifacts" / "mlflow.db"
    
    if not db_path.exists():
        print("❌ MLflow database not found")
        return
    
    print("\n" + "="*60)
    print("🧪 MLFLOW EXPERIMENTS & RUNS")
    print("="*60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get experiments
    cursor.execute("SELECT experiment_id, name FROM experiments WHERE lifecycle_stage='active'")
    experiments = cursor.fetchall()
    
    for exp_id, exp_name in experiments:
        print(f"\n📁 Experiment: {exp_name} (ID: {exp_id})")
        
        # Get runs for this experiment
        cursor.execute("""
            SELECT run_uuid, start_time, end_time, status
            FROM runs 
            WHERE experiment_id = ? AND lifecycle_stage='active'
            ORDER BY start_time DESC
            LIMIT 10
        """, (exp_id,))
        
        runs = cursor.fetchall()
        print(f"   Total Runs: {len(runs)}")
        
        for i, (run_id, start, end, status) in enumerate(runs[:5], 1):
            print(f"\n   Run {i}: {run_id[:8]}...")
            print(f"      Status: {status}")
            print(f"      Started: {start}")
            
            # Get metrics for this run
            cursor.execute("""
                SELECT key, value 
                FROM metrics 
                WHERE run_uuid = ?
            """, (run_id,))
            
            metrics = cursor.fetchall()
            if metrics:
                print(f"      Metrics:")
                for key, value in metrics:
                    print(f"         {key}: {value:.4f}")
    
    conn.close()
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    show_mlflow_experiments()
