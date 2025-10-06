#!/bin/sh
set -e

echo "🔧 Fixing permissions for mounted volumes..."

# Fix permissions for storage directories
if [ -d "/var/www/html/storage/logs" ]; then
    chown -R www-data:www-data /var/www/html/storage/logs 2>/dev/null || true
    chmod -R 775 /var/www/html/storage/logs 2>/dev/null || true
    echo "✅ Fixed permissions for storage/logs"
fi

if [ -d "/var/www/html/storage/app/public" ]; then
    chown -R www-data:www-data /var/www/html/storage/app/public 2>/dev/null || true
    chmod -R 775 /var/www/html/storage/app/public 2>/dev/null || true
    echo "✅ Fixed permissions for storage/app/public"
fi

if [ -d "/var/www/html/bootstrap/cache" ]; then
    chown -R www-data:www-data /var/www/html/bootstrap/cache 2>/dev/null || true
    chmod -R 775 /var/www/html/bootstrap/cache 2>/dev/null || true
    echo "✅ Fixed permissions for bootstrap/cache"
fi

echo "✅ Permission fixes complete"