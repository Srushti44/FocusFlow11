"""Demo script to show drift monitoring - works standalone"""
import sys
from pathlib import Path
import sqlite3
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def show_drift_monitoring():
    """Show drift monitoring status"""
    db_path = Path(__file__).parent / "artifacts" / "ml_monitoring.db"
    
    if not db_path.exists():
        print("❌ Monitoring database not found")
        return
    
    print("\n" + "="*60)
    print("📊 DRIFT MONITORING STATUS")
    print("="*60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get recent predictions
    cursor.execute("""
        SELECT COUNT(*) as total, 
               AVG(psi_score) as avg_psi,
               MAX(psi_score) as max_psi,
               MIN(created_at) as first_pred,
               MAX(created_at) as last_pred
        FROM predictions
    """)
    
    row = cursor.fetchone()
    if row and row[0] > 0:
        print(f"\n📈 Prediction Statistics:")
        print(f"   Total Predictions: {row[0]}")
        print(f"   Average PSI Score: {row[1]:.4f if row[1] else 'N/A'}")
        print(f"   Max PSI Score: {row[2]:.4f if row[2] else 'N/A'}")
        print(f"   First Prediction: {row[3]}")
        print(f"   Last Prediction: {row[4]}")
        
        # Check for drift
        drift_threshold = 0.2
        if row[2] and row[2] > drift_threshold:
            print(f"\n⚠️  DRIFT DETECTED! Max PSI ({row[2]:.4f}) > Threshold ({drift_threshold})")
        else:
            print(f"\n✅ No significant drift detected")
    else:
        print("\n📊 No predictions recorded yet")
    
    conn.close()
    print("="*60 + "\n")

if __name__ == "__main__":
    show_drift_monitoring()
