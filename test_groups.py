#!/usr/bin/env python3

# Direct test for functional groups
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("1. Testing basic imports...")
    from src.analyzers.project_progress_tracker import ProjectProgressTracker
    from src.utils.config import ConfigManager
    print("✅ Imports successful")
    
    print("2. Creating tracker...")
    config = ConfigManager()
    tracker = ProjectProgressTracker("/mnt/h/Projects/project-prompt", config)
    print("✅ Tracker created")
    
    print("3. Testing directory-based groups...")
    dir_groups = tracker._create_directory_based_groups()
    print(f"✅ Directory groups: {len(dir_groups)} found")
    for name, data in list(dir_groups.items())[:3]:
        print(f"  - {name}: {data.get('files', 0)} files")
    
    print("4. Testing basic functional groups...")
    try:
        func_groups = tracker._create_basic_functional_groups()
        print(f"✅ Functional groups: {len(func_groups)} found")
        for name, data in list(func_groups.items())[:3]:
            print(f"  - {name}: {data.get('files', 0)} files")
    except Exception as e:
        print(f"⚠️ Functional groups failed: {e}")
        func_groups = {}
    
    print("5. Merging groups...")
    all_groups = dir_groups.copy()
    all_groups.update(func_groups)
    print(f"✅ Total groups: {len(all_groups)}")
    
    # Sort and show top groups
    sorted_groups = sorted(all_groups.items(), 
                          key=lambda x: (x[1].get('importance', 0), x[1].get('files', 0)), 
                          reverse=True)
    
    print("6. Top functional groups:")
    for name, data in sorted_groups[:5]:
        completion = data.get('completion_estimate', 0)
        files_count = data.get('files', 0)
        group_type = data.get('type', 'unknown')
        print(f"  📁 {name}")
        print(f"     Type: {group_type}, Files: {files_count}, Completion: {completion}%")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
