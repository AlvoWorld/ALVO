#!/bin/bash
cd /opt/alvo
git reset HEAD -- "*.pyc" "osya.db" "__pycache__" 2>/dev/null
git add -A
git reset HEAD -- "*.pyc" "osya.db" "osya.db-shm" "osya.db-wal" 2>/dev/null
find . -path './__pycache__' -prune -o -path '*/__pycache__' -prune | xargs -I{} git reset HEAD {} 2>/dev/null
git diff --cached --quiet || {
    git commit -m "auto: $(date '+%Y-%m-%d %H:%M UTC')"
    GIT_SSH_COMMAND="ssh -i ~/.ssh/alvo_github -o StrictHostKeyChecking=no" git push origin main 2>/dev/null
    echo "Saved"
}
