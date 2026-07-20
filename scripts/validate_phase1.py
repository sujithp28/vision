"""
Validate Phase 1 completion
"""

import sys
import os
from pathlib import Path

def check_folder_structure():
    """Check if all required folders exist"""
    required_dirs = [
        "apps/api/src",
        "apps/web",
        "apps/worker",
        "apps/mcp",
        "packages/shared",
        "packages/database",
        "packages/auth",
        "packages/ai-core",
        "packages/sdk",
        "packages/plugins",
        "tests",
        "docs",
        "infrastructure",
    ]
    
    print("Checking folder structure...")
    for path in required_dirs:
        full_path = Path(path)
        if full_path.exists():
            print(f"  [OK] {path}")
        else:
            print(f"  [FAIL] {path} - MISSING")
            return False
    
    return True


def check_python_files():
    """Check if all required Python files exist"""
    required_files = [
        "packages/shared/__init__.py",
        "packages/shared/exceptions.py",
        "packages/shared/di.py",
        "packages/database/models/user.py",
        "packages/database/models/video_result.py",
        "packages/database/session.py",
        "packages/ai-core/providers/base.py",
        "packages/ai-core/providers/mock.py",
        "apps/api/src/config/settings.py",
        "apps/api/tests/conftest.py",
        "apps/api/tests/test_providers.py",
    ]
    
    print("\nChecking Python files...")
    for filepath in required_files:
        if Path(filepath).exists():
            size = Path(filepath).stat().st_size
            print(f"  [OK] {filepath} ({size} bytes)")
        else:
            print(f"  [FAIL] {filepath} - MISSING")
            return False
    
    return True


def check_imports():
    """Verify critical imports work"""
    print("\nChecking imports...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, '.')
        
        # Test imports
        from packages.shared.exceptions import VisionForgeException
        print("  [OK] packages.shared.exceptions")
        
        from packages.shared.di import ServiceContainer, get_container
        print("  [OK] packages.shared.di")
        
        from packages.database.models import Base, User, VideoResult
        print("  [OK] packages.database.models")
        
        from packages.ai_core.providers.mock import MockProvider
        print("  [OK] packages.ai_core.providers")
        
        from apps.api.src.config.settings import Settings
        print("  [OK] apps.api.src.config.settings")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Import error: {e}")
        return False


def check_bugs_fixed():
    """Verify bug fixes are in place"""
    print("\nChecking bug fixes...")
    
    # Bug 1: planner.py variable name
    with open("visionforgeai/api/routes/videos/planner.py", "r") as f:
        planner_content = f.read()
        if "additional_context +=" in planner_content and "additional_content +=" not in planner_content:
            print("  [OK] Bug 1: planner.py variable name fixed")
        else:
            print("  [FAIL] Bug 1: planner.py variable name NOT fixed")
            return False
    
    # Bug 2: llm.py media type
    with open("visionforgeai/api/routes/llm.py", "r") as f:
        llm_content = f.read()
        if 'media_type="text/event-stream"' in llm_content:
            print("  [OK] Bug 2: llm.py media type fixed")
        else:
            print("  [FAIL] Bug 2: llm.py media type NOT fixed")
            return False
    
    # Bug 3: LocalLLMProvider asyncio wrapper
    with open("visionforgeai/providers/llm/local.py", "r") as f:
        local_content = f.read()
        if "asyncio.to_thread" in local_content and "import asyncio" in local_content:
            print("  [OK] Bug 3: LocalLLMProvider asyncio wrapper added")
        else:
            print("  [FAIL] Bug 3: LocalLLMProvider asyncio wrapper NOT added")
            return False
    
    # Bug 4: llama-cpp-python in requirements
    with open("requirements.txt", "r") as f:
        req_content = f.read()
        if "llama-cpp-python" in req_content:
            print("  [OK] Bug 4: llama-cpp-python added to requirements.txt")
        else:
            print("  [FAIL] Bug 4: llama-cpp-python NOT in requirements.txt")
            return False
    
    return True


def main():
    """Run all checks"""
    print("=" * 60)
    print("PHASE 1 VALIDATION")
    print("=" * 60)
    
    checks = [
        ("Folder Structure", check_folder_structure()),
        ("Python Files", check_python_files()),
        ("Imports", check_imports()),
        ("Bug Fixes", check_bugs_fixed()),
    ]
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for check_name, result in checks:
        status = "PASS" if result else "FAIL"
        print(f"{check_name}: {status}")
    
    all_passed = all(result for _, result in checks)
    
    print("=" * 60)
    if all_passed:
        print("PHASE 1 VALIDATION PASSED - READY FOR NEXT STEP")
        print("=" * 60)
        return 0
    else:
        print("PHASE 1 VALIDATION FAILED - FIX ISSUES ABOVE")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

