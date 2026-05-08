#!/bin/bash
# PCL2 主页同步到阿里云 ECS
# PCL2 域名: qawsedrftgyhujiko.fun (Cloudflare proxy)
set -e

HOST="ecs"
DEST="/var/www/pcl2-homepage"
TMP="/tmp/pcl2-sync-$$"

echo "📤 同步到阿里云 ECS..."

# 打包后通过 SSH 管道传输（绕过权限问题）
ssh "$HOST" "mkdir -p $DEST/icons"
tar czf - output/Custom.xaml output/Custom.xaml.ini output/version.txt \
  $( [ -d icons ] && echo "icons" || echo "" ) | \
  ssh "$HOST" "sudo tar xzf - -C $DEST && sudo chown -R www-data:www-data $DEST"

echo "✅ 同步完成 — PCL2 刷新即可 (ECS 本地 serve)"
