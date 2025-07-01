#!/usr/bin/env python3
"""
Cleanup DDD Duplicates Script
============================
Remove original _ddd folders after successful integration
"""

import os
import shutil
from pathlib import Path


def verify_integration_success():
    """Verify that DDD integration was successful"""
    src_dir = Path("src")

    # Check if new structure exists
    domain_dir = src_dir / "domain"
    app_dir = src_dir / "application"
    infra_dir = src_dir / "infrastructure"

    if not all([domain_dir.exists(), app_dir.exists(), infra_dir.exists()]):
        return False

    # Count domains in new structure
    domain_count = len(
        [d for d in domain_dir.iterdir() if d.is_dir() and not d.name.startswith("__")]
    )
    app_count = len(
        [d for d in app_dir.iterdir() if d.is_dir() and not d.name.startswith("__")]
    )

    print(f"✓ Found {domain_count} domains in new structure")
    print(f"✓ Found {app_count} application domains")

    return domain_count >= 10 and app_count >= 10


def get_ddd_folders():
    """Get list of _ddd folders to remove"""
    services_dir = Path("src/application/services")
    ddd_folders = []

    for item in services_dir.iterdir():
        if item.is_dir() and item.name.endswith("_ddd"):
            ddd_folders.append(item)

    return ddd_folders


def move_to_legacy(folder_path):
    """Move _ddd folder to legacy"""
    legacy_dir = Path("src/legacy/old_ddd_folders")
    legacy_dir.mkdir(parents=True, exist_ok=True)

    target_path = legacy_dir / folder_path.name

    try:
        shutil.move(str(folder_path), str(target_path))
        print(f"✓ Moved {folder_path.name} to legacy")
        return True
    except Exception as e:
        print(f"✗ Error moving {folder_path.name}: {e}")
        return False


def cleanup_ddd_folders():
    """Main cleanup function"""
    print("=" * 50)
    print("DDD Duplicates Cleanup Starting...")
    print("=" * 50)

    # Step 1: Verify integration success
    if not verify_integration_success():
        print("✗ Integration verification failed! Stopping cleanup.")
        return False

    print("✓ Integration verification passed")

    # Step 2: Get _ddd folders
    ddd_folders = get_ddd_folders()
    print(f"Found {len(ddd_folders)} _ddd folders to cleanup")

    # Step 3: Move to legacy
    success_count = 0
    for folder in ddd_folders:
        if move_to_legacy(folder):
            success_count += 1

    print(
        f"\n✓ Successfully moved {success_count}/{len(ddd_folders)} folders to legacy"
    )

    # Step 4: Create cleanup report
    create_cleanup_report(success_count, len(ddd_folders))

    print("=" * 50)
    print("DDD Cleanup Completed!")
    print("=" * 50)

    return True


def create_cleanup_report(success_count, total_count):
    """Create cleanup report"""
    report = f"""# DDD Cleanup Report
==================

## Summary
- Total _ddd folders found: {total_count}
- Successfully moved to legacy: {success_count}
- Cleanup success rate: {(success_count/total_count)*100:.1f}%

## Result
{'✓ All duplicates cleaned successfully!' if success_count == total_count else '⚠️ Some folders could not be moved'}

## Final Structure
- Original _ddd folders: Moved to src/legacy/old_ddd_folders/
- New DDD structure: Active in src/domain/, src/application/, src/infrastructure/
- Project is now clean and professional!
"""

    with open("DDD_CLEANUP_REPORT.md", "w") as f:
        f.write(report)

    print("✓ Cleanup report saved to DDD_CLEANUP_REPORT.md")


if __name__ == "__main__":
    cleanup_ddd_folders()
