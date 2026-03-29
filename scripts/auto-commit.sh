#!/bin/bash
cd /opt/alvo
git add -A -- ':!*.pyc' ':!osya.db' ':!osya.db-shm' ':!osya.db-wal' ':!__pycache__'
git diff --cached --quiet || {
    git commit -m "auto: $(date '+%Y-%m-%d %H:%M UTC')"
    GIT_SSH_COMMAND="ssh -i ~/.ssh/alvo_github -o StrictHostKeyChecking=no" git push origin main 2>/dev/null
    echo "[$(date)] Auto-saved to GitHub"
}
