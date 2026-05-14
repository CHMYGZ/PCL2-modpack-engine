#!/bin/bash
cd /home/ftc13/pcl2
LOG="update_$(date +%Y%m%d_%H%M%S).log"

echo "=== PCL2 Update $(date) ===" | tee "$LOG"

python3 src/curseforge_fetcher.py --merge >> "$LOG" 2>&1
python3 src/scrape_links.py >> "$LOG" 2>&1
python3 src/generator.py >> "$LOG" 2>&1

python3 /tmp/cleanup_pcl2.py output/Custom.xaml >> "$LOG" 2>&1
sed -i 's/PCL2/PCL/g' output/Custom.xaml
sed -i 's/ Background="Transparent"//g; s/ HoverBackground="[^"]*"//g; s/ HoverForeground="[^"]*"//g' output/Custom.xaml

scp -i ~/.ssh/id_ecs -o StrictHostKeyChecking=no output/Custom.xaml root@139.196.113.49:/var/www/pcl2-homepage/output/Custom.xaml >> "$LOG" 2>&1

echo "Deploy done" | tee -a "$LOG"
echo "File: $(wc -c < output/Custom.xaml) bytes" | tee -a "$LOG"

git add -A >> "$LOG" 2>&1
git commit -m "auto sync $(date +%Y-%m-%d)" >> "$LOG" 2>&1
git push github main >> "$LOG" 2>&1
git push origin main >> "$LOG" 2>&1

echo "=== ALL DONE $(date) ===" | tee -a "$LOG"
