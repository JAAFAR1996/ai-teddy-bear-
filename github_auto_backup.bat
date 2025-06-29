@echo off
cd /d "C:\Users\jaafa\Desktop\5555\New folder"

git add -A

git commit -m "Auto-backup %DATE% %TIME%"

git push https://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@github.com/JAAFAR1996/ai-teddy-bear-.git main
git status
git log -1
pause
