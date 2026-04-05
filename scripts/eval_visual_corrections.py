"""Evaluation script for visual correction system.

Run after collecting screenshots from game sessions to verify:
1. Self-reflection prompt produces parseable visual_correction fields
2. Visual notes inject correctly into information-gathering prompts
3. Overall response structure hasn't broken

Usage:
    python scripts/eval_visual_corrections.py --screenshots-dir <path>

TODO: Fill in with real screenshot data after Week 3 validation phase.
"""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Evaluate visual correction system")
    parser.add_argument("--screenshots-dir", type=str, help="Directory containing test screenshots")
    args = parser.parse_args()

    print("Visual Corrections Eval Script")
    print("=" * 40)
    print()
    print("STATUS: Skeleton — needs real test data from game sessions.")
    print()
    print("Planned evaluations:")
    print("  1. Self-reflection visual_correction field parsing")
    print("  2. Visual notes injection formatting")
    print("  3. End-to-end: screenshot → info gathering → self reflection → correction → re-injection")
    print()

    if not args.screenshots_dir:
        print("No screenshots directory provided. Run game sessions first to collect test data.")
        print("See TODOS.md for details.")
        sys.exit(0)

    print(f"Screenshots dir: {args.screenshots_dir}")
    print("TODO: Implement evaluation pipeline")


if __name__ == "__main__":
    main()
