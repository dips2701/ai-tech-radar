@echo off
chcp 65001
cd /d "C:\Users\Asus HN256T\Desktop\AI-Tech-Radar"

python daily_runner.py >> task_log.txt 2>&1

exit