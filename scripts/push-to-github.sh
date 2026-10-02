#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-menarzullayev/expense-tracker}"
REMOTE="https://github.com/${REPO}.git"
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"
printf 'Remote configured: %s\n' "$REMOTE"
printf '\nCreate the GitHub repository as public, then run:\n  git push -u origin main\n'
