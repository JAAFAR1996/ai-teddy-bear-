@echo off
cd /d "C:\Users\jaafa\Desktop\5555\New folder"

git add -A

git commit -m "Auto-backup %DATE% %TIME%"

git push https://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@github.com/JAAFAR1996/ai-teddy-bear-.git main
git status
git log -1

