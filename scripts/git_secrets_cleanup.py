from typing import Dict, List
from pathlib import Path
import subprocess
import os
import logging

logger = logging.getLogger(__name__)

"""
🗑️ Git Secrets Cleanup Helper
Helps identify and clean secrets from Git history
"""


class GitSecretsCleanup:
    """Helper class for cleaning secrets from Git history"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.secrets_patterns = {
            "OpenAI API Keys": "sk-[a-zA-Z0-9]{48,}",
            "Anthropic API Keys": "sk-ant-[a-zA-Z0-9-]{95,}",
            "Google API Keys": "AIza[0-9A-Za-z\\-_]{35}",
            "JWT Secrets": "[a-zA-Z0-9%!@#$&*+=\\-_]{32,}",
            "Encryption Keys": "[A-Za-z0-9+/]{32,}={0,2}",
            "Bearer Tokens": "Bearer [a-zA-Z0-9\\-_\\.]+",
        }
        self.known_secrets = [
            "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",
            "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",
            "AIzaSyCXDVCTFdvbzSiXf6JjHZAsAFxexo3OMbQ",
            "hK1NjE%TP!%9r^Z&jdIffpRsu@9Ezg^DDp8tf%frOUoP!AyId1tqh@Sqehy^C^ip",
            "QjMfAp5xLV520CNBy7chNxRsNolV_xwHYeBiV1EyIXY=",
        ]

    def create_secrets_replacement_file(self) -> str:
        """Create BFG replacement file for known secrets"""
        replacements_file = self.project_root / "secrets_to_replace.txt"
        with open(replacements_file, "w") as f:
            f.write("# BFG Repo-Cleaner replacement file\n")
            f.write("# Format: original_secret===>REPLACEMENT\n\n")
            for secret in self.known_secrets:
                if len(secret) > 20:
                    pattern = secret[:10] + "***" + secret[-10:]
                else:
                    pattern = secret
                f.write(f"{secret}===>***REMOVED_SECRET***\n")
        logger.info(f"✅ Created BFG replacement file: {replacements_file}")
        return str(replacements_file)

    def scan_git_history(self) -> List[Dict]:
        """Scan git history for potential secrets"""
        logger.info("🔍 Scanning Git history for secrets...")
        try:
            result = subprocess.run(
                ["git", "log", "--all", "--full-history", "--pretty=format:%H:%s"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode != 0:
                logger.info(f"❌ Git log failed: {result.stderr}")
                return []
            commits = result.stdout.strip().split("\n")
            secrets_found = []
            for commit_line in commits[:50]:
                if ":" in commit_line:
                    commit_hash, commit_msg = commit_line.split(":", 1)
                    diff_result = subprocess.run(
                        ["git", "show", commit_hash],
                        capture_output=True,
                        text=True,
                        cwd=self.project_root,
                    )
                    if diff_result.returncode == 0:
                        content = diff_result.stdout
                        for secret in self.known_secrets:
                            if secret in content:
                                secrets_found.append(
                                    {
                                        "commit": commit_hash,
                                        "message": commit_msg.strip(),
                                        "secret_preview": secret[:20] + "...",
                                        "secret_type": self._identify_secret_type(
                                            secret
                                        ),
                                    }
                                )
            return secrets_found
        except Exception as e:
            logger.info(f"❌ Error scanning git history: {e}")
            return []

    def _identify_secret_type(self, secret: str) -> str:
        """Identify the type of secret"""
        if secret.startswith("sk-proj-") or secret.startswith("sk-"):
            return "OpenAI API Key"
        elif secret.startswith("sk-ant-"):
            return "Anthropic API Key"
        elif secret.startswith("AIza"):
            return "Google API Key"
        elif len(secret) > 50 and "%" in secret:
            return "JWT Secret"
        elif secret.endswith("="):
            return "Encryption Key"
        else:
            return "Unknown Secret"

    def generate_cleanup_commands(self) -> List[str]:
        """Generate commands for cleaning Git history"""
        commands = [
            "# Git Secrets Cleanup Commands",
            "# Run these commands in order",
            "",
            "# 1. Install BFG Repo-Cleaner",
            "# Download from: https://rtyley.github.io/bfg-repo-cleaner/",
            "",
            "# 2. Create a fresh clone (backup)",
            "git clone --mirror your-repo.git backup-repo.git",
            "",
            "# 3. Run BFG to remove secrets",
            f"java -jar bfg.jar --replace-text {self.project_root}/secrets_to_replace.txt your-repo.git",
            "",
            "# 4. Clean up and optimize",
            "cd your-repo.git",
            "git reflog expire --expire=now --all",
            "git gc --prune=now --aggressive",
            "",
            "# 5. Push cleaned history (DANGER: This rewrites history)",
            "git push --force-with-lease origin --all",
            "",
            "# 6. Verify secrets are removed",
            "git log --all --full-history --grep='sk-'",
            "",
            "# Alternative: Use git-filter-repo (modern approach)",
            "pip install git-filter-repo",
            "git filter-repo --replace-text secrets_to_replace.txt",
            "",
            "# Install git-secrets for future protection",
            "git secrets --install",
            "git secrets --register-aws",
        ]
        return commands

    def create_pre_commit_hook(self) -> None:
        """Create pre-commit hook to prevent secrets"""
        hooks_dir = self.project_root / ".git" / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        pre_commit_hook = hooks_dir / "pre-commit"
        hook_content = """#!/bin/bash
# Pre-commit hook to prevent secrets from being committed

echo "🔍 Checking for secrets in staged files..."

# Patterns to detect
PATTERNS=(
    "sk-[a-zA-Z0-9]{48,}"        # OpenAI keys
    "sk-ant-[a-zA-Z0-9-]{95,}"   # Anthropic keys
    "AIza[0-9A-Za-z\\-_]{35}"     # Google keys
    "[A-Za-z0-9+/]{32,}={0,2}"   # Base64 encoded secrets
)

# Check staged files
for pattern in "${PATTERNS[@]}"; do
    if git diff --cached --name-only | xargs grep -l "$pattern" 2>/dev/null; then
        echo "❌ BLOCKED: Potential secret detected matching pattern: $pattern"
        echo "Please remove secrets and use environment variables instead."
        exit 1
    fi
done

echo "✅ No secrets detected in staged files"
exit 0
"""
        with open(pre_commit_hook, "w") as f:
            f.write(hook_content)
        os.chmod(pre_commit_hook, 448)
        logger.info(f"✅ Created pre-commit hook: {pre_commit_hook}")

    def generate_full_report(self) -> str:
        """Generate comprehensive cleanup report"""
        logger.info("\n🔒 GENERATING GIT SECRETS CLEANUP REPORT...")
        replacements_file = self.create_secrets_replacement_file()
        secrets_in_history = self.scan_git_history()
        cleanup_commands = self.generate_cleanup_commands()
        self.create_pre_commit_hook()
        report = []
        report.append("🗑️ GIT SECRETS CLEANUP REPORT")
        report.append("=" * 60)
        report.append("")
        if secrets_in_history:
            report.append(
                f"⚠️ SECRETS FOUND IN GIT HISTORY: {len(secrets_in_history)}")
            report.append("-" * 40)
            for secret_info in secrets_in_history:
                report.append(f"Commit: {secret_info['commit'][:8]}...")
                report.append(f"Type: {secret_info['secret_type']}")
                report.append(f"Message: {secret_info['message']}")
                report.append("")
        else:
            report.append("✅ No known secrets found in recent Git history")
            report.append("")
        report.append("📋 CLEANUP COMMANDS")
        report.append("-" * 40)
        report.extend(cleanup_commands)
        report.append("")
        report.append("🔐 SECURITY RECOMMENDATIONS")
        report.append("-" * 40)
        report.append("1. Immediately rotate all exposed API keys")
        report.append("2. Clean Git history using BFG or git-filter-repo")
        report.append("3. Install git-secrets for future protection")
        report.append("4. Use environment variables for all secrets")
        report.append("5. Set up pre-commit hooks (created automatically)")
        report.append("")
        report.append("🚨 CRITICAL ACTIONS REQUIRED")
        report.append("-" * 40)
        report.append("• Rotate OpenAI API key immediately")
        report.append("• Rotate Anthropic API key immediately")
        report.append("• Rotate Google API key immediately")
        report.append("• Update .env with new keys")
        report.append("• Clean Git history before pushing")
        report.append("")
        return "\n".join(report)


def main():
    """Main execution"""
    cleanup = GitSecretsCleanup()
    report = cleanup.generate_full_report()
    report_file = Path("GIT_SECRETS_CLEANUP_REPORT.md")
    with open(report_file, "w") as f:
        f.write(report)
    logger.info(f"\n✅ Report saved to: {report_file}")
    logger.info("\n" + report)


if __name__ == "__main__":
    main()
