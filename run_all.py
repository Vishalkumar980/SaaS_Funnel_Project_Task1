# run_all.py - Runs all analysis steps
import subprocess
import os

print("=" * 60)
print("RUNNING COMPLETE ANALYSIS PIPELINE")
print("=" * 60)

scripts = [
    "scripts/0_create_sample_data.py",
    "scripts/1_data_cleaning.py",
    "scripts/2_funnel_analysis.py",
    "scripts/3_cohort_analysis.py",
    "scripts/4_segmentation_analysis.py"
]

for script in scripts:
    print(f"\n▶️ Running {script}...")
    result = subprocess.run(["python", script], capture_output=False)
    if result.returncode != 0:
        print(f"❌ Error in {script}")
        break
    print(f"✅ Completed {script}")

print("\n" + "=" * 60)
print("🎉 ALL ANALYSIS COMPLETE!")
print("=" * 60)