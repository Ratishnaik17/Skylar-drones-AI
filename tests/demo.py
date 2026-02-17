"""
Demo script showing the full workflow of the AI Operations Brain
"""

import sys
sys.path.insert(0, '../src')

from train_model import PilotMatchModel
from features import FeatureEngineer
from conflict_detector import ConflictDetector
from drone_matcher import DroneMatcher
from urgent_reassignment import UrgentReassignmentEngine
import pandas as pd


def demo_workflow():
    """Run complete demo workflow"""
    
    print("=" * 70)
    print("🚀 AI OPERATIONS BRAIN - DEMO WORKFLOW")
    print("=" * 70)
    print()
    
    # 1. Load sample data
    print("📊 1. Loading sample data...")
    pilots_df = pd.read_csv("../data/pilot_roster.csv")
    missions_df = pd.read_csv("../data/missions.csv")
    drones_df = pd.read_csv("../data/drones.csv")
    
    print(f"   ✅ Loaded {len(pilots_df)} pilots, {len(missions_df)} missions, {len(drones_df)} drones")
    print()
    
    # 2. Train model
    print("🧠 2. Training ML model...")
    model = PilotMatchModel()
    training_df = model.create_training_dataset("../data/pilot_roster.csv", "../data/missions.csv")
    metrics = model.train(training_df)
    model.save_model()
    print(f"   ✅ Model trained! ROC-AUC: {metrics['roc_auc']:.4f}")
    print()
    
    # 3. Get feature importance
    print("📈 3. Feature Importance:")
    importance = model.get_feature_importance()
    for feature, score in importance.items():
        bar = "█" * int(score * 30)
        print(f"   {feature:20s} {bar:30s} {score:.4f}")
    print()
    
    # 4. Demonstrate pilot ranking for a mission
    print("🏆 4. Ranking pilots for Mission M001...")
    mission = missions_df.iloc[0].to_dict()
    pilots = [p.to_dict() for p in pilots_df.iterrows()]
    
    predictions = model.batch_predict(pilots, mission)
    
    print(f"   Mission: {mission['name']} ({mission['priority']} priority)")
    print(f"   Location: {mission['location']}, Duration: {mission['duration_days']} days, Budget: ${mission['budget']}")
    print()
    print("   Top 3 Candidates:")
    for i, pred in enumerate(predictions[:3]):
        status = "✅ SUITABLE" if pred['suitable'] else "❌ NOT SUITABLE"
        print(f"   {i+1}. {pred['pilot_name']:20s} - {pred['probability']:.1%} {status}")
    print()
    
    # 5. Conflict detection
    print("⚠️  5. Conflict Detection for Top Candidate...")
    top_pilot = pilots_df.iloc[0].to_dict()
    conflicts = ConflictDetector.detect_all_conflicts(top_pilot, mission)
    
    if conflicts:
        print(f"   Found {len(conflicts)} conflict(s):")
        for conflict in conflicts:
            severity_icon = "🔴" if conflict.severity == "high" else "🟡"
            print(f"   {severity_icon} [{conflict.conflict_type.upper()}] {conflict.message}")
    else:
        print("   ✅ No conflicts detected!")
    print()
    
    # 6. Drone matching
    print("🛸 6. Ranking drones for this mission...")
    drones = [d.to_dict() for d in drones_df.iterrows()]
    ranked_drones = DroneMatcher.rank_drones_for_mission(drones, mission)
    
    print(f"   Compatible drones:")
    for i, drone in enumerate(ranked_drones[:3]):
        status = "✅" if drone["compatible"] else "❌"
        print(f"   {i+1}. {drone['drone_name']:20s} {status} (score: {drone['score']:.2f})")
        if drone['warnings']:
            for warning in drone['warnings']:
                print(f"       ⚠️  {warning}")
    print()
    
    # 7. Urgent reassignment scenario
    print("🚨 7. Urgent Reassignment Scenario...")
    high_priority_mission = missions_df[missions_df['priority'] == 'critical'].iloc[0].to_dict() \
                           if any(missions_df['priority'] == 'critical') \
                           else missions_df.iloc[0].to_dict()
    
    current_pilot = pilots_df.iloc[0].to_dict()
    available_pilots = [p.to_dict() for p in pilots_df.iterrows()]
    
    print(f"   Mission: {high_priority_mission['name']} ({high_priority_mission['priority']})")
    print(f"   Currently assigned: {current_pilot['name']}")
    print()
    
    # Get predictions for urgent reassignment
    predictions = model.batch_predict(available_pilots, high_priority_mission)
    ranked = UrgentReassignmentEngine.rank_pilot_candidates(
        available_pilots,
        high_priority_mission,
        predictions
    )
    
    if ranked:
        best = ranked[0]
        print(f"   🏆 Best reassignment candidate: {best['pilot_name']}")
        print(f"       Reassignment score: {best['reassignment_score']:.3f}")
        print(f"       Experience: {best['experience_years']} years")
        print(f"       ML Probability: {best['ml_probability']:.1%}")
        print()
        
        print("   Top 3 options:")
        for i, candidate in enumerate(ranked[:3]):
            print(f"   {i+1}. {candidate['pilot_name']:20s} (score: {candidate['reassignment_score']:.3f})")
    print()
    
    # 8. Summary statistics
    print("📊 8. Summary Statistics")
    print(f"   Total pilots: {len(pilots_df)}")
    print(f"   Total missions: {len(missions_df)}")
    print(f"   Total drones: {len(drones_df)}")
    print(f"   Average pilot cost: ${pilots_df['cost_per_day'].mean():.2f}/day")
    print(f"   Average mission budget: ${missions_df['budget'].mean():.2f}")
    print(f"   High priority missions: {len(missions_df[missions_df['priority'].isin(['high', 'critical'])])}")
    print()
    
    print("=" * 70)
    print("✅ DEMO COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Start the API: python ../src/main.py")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Try ranking pilots and detecting conflicts")
    print("4. Configure Google Sheets for 2-way sync")
    print("5. Deploy to production!")


if __name__ == "__main__":
    demo_workflow()
