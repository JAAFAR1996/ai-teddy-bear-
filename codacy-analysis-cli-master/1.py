#!/bin/bash

# Quick fix for README.md formatting

echo "🔧 Fixing README.md..."

# Fix all bullet points
perl -i -pe 's/^\* /- /g' README.md
perl -i -pe 's/^(\s+)\* /$1- /g' README.md

# Fix URLs (wrap in angle brackets)
perl -i -pe 's/\((https?:\/\/[^)]+)\)/(<$1>)/g' README.md

# Show what changed
echo "📋 Changes made:"
git diff --stat README.md

# Commit
git add README.md
git commit -m "fix: README markdown formatting

- Replace asterisk bullets with dashes
- Wrap URLs in angle brackets for proper markdown
- Maintain proper indentation"

echo "✅ Done!"