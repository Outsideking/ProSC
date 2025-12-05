#!/bin/bash

echo "Starting automatic deployment..."

# ติดตั้ง dependencies (ถ้ามี)
npm install

# Build โปรเจกต์ Next.js
npm run build

# รันด้วย PM2 (เริ่มใหม่ถ้ามีอยู่แล้ว)
if pm2 describe next-app > /dev/null; then
  echo "Restarting existing PM2 process..."
  pm2 restart next-app
else
  echo "Starting new PM2 process..."
  pm2 start npm --name "next-app" -- start
fi

echo "Deployment complete!"
