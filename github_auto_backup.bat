@echo off
cd /d "C:\Users\jaafa\Desktop\5555\New folder"

git add -A

git commit -m "Auto-backup %DATE% %TIME%"

git push https://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@github.com/JAAFAR1996/ai-teddy-bear-.git main

git status
git log -1
pause
