import subprocess
import sys

def check_breaking_change():
    result = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True,
        text=True
    )

    commit_msg = result.stdout.strip()
    print(f"Latest commit: {commit_msg}")

    is_fastapi = "isolated-service" in commit_msg
    is_breaking = "!" in commit_msg or "BREAKING CHANGE" in commit_msg

    if is_fastapi and is_breaking:
        print("\n⚠️  BREAKING CHANGE detected in isolated-service!")
        print("👉  glucode-service depends on isolated-service.")
        print("👉  Review glucode-service and bump its version manually.")
        print("👉  Update VERSION_MATRIX.md with new compatibility entry.")
        sys.exit(1)

    print("✅ No cascade bump required.")
    sys.exit(0)

if __name__ == "__main__":
    check_breaking_change()