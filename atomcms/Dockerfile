# Stage 1: Composer dependencies
FROM php:8-cli-alpine AS composer-builder

ARG COMMIT=53ea66d

WORKDIR /app

# Install system dependencies and PHP extensions
RUN apk add --no-cache \
    git \
    zip \
    unzip \
    icu-dev \
    libzip-dev \
    linux-headers

RUN docker-php-ext-install -j$(nproc) \
    sockets \
    intl \
    pdo_mysql \
    zip

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Clone the repository
RUN git config --global --add safe.directory /app
RUN git clone --recurse-submodules https://github.com/ObjectRetros/atomcms.git .
RUN git checkout $COMMIT

# Install composer dependencies
RUN composer install \
    --no-interaction \
    --no-dev \
    --prefer-dist \
    --optimize-autoloader \
    --no-scripts

# Generate optimized autoload files
RUN composer dump-autoload --optimize


# Stage 2: Node/NPM build
FROM node:20-alpine AS npm-builder

WORKDIR /app

# Copy application files from composer stage
COPY --from=composer-builder /app /app

# Install dependencies and build assets
RUN yarn install --frozen-lockfile
RUN yarn run build:atom
RUN yarn run build:dusk

# Clean up node_modules to save space
RUN rm -rf node_modules


# Stage 3: Final image with serversideup/php (nginx + PHP-FPM)
FROM serversideup/php:8-fpm-nginx-alpine

ENV PHP_OPCACHE_ENABLE=1

WORKDIR /var/www/html

# Switch to root for setup
USER root

# Copy application from npm-builder
COPY --from=npm-builder --chown=www-data:www-data /app /var/www/html

# Create necessary directories and set permissions
RUN mkdir -p \
    storage/framework/cache \
    storage/framework/sessions \
    storage/framework/views \
    storage/logs \
    bootstrap/cache \
    && chown -R www-data:www-data /var/www/html/storage /var/www/html/bootstrap/cache \
    && chmod -R 775 /var/www/html/storage /var/www/html/bootstrap/cache

# Custom nginx configuration for Laravel
COPY <<'EOF' /etc/nginx/server-opts.d/laravel.conf
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;

# CORS headers for /gamedata directory and all subdirectories
location ~ ^/gamedata/ {
    # Always add CORS headers
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-CSRF-TOKEN" always;
    add_header Access-Control-Expose-Headers "Content-Length,Content-Range" always;
    add_header Access-Control-Allow-Credentials "false" always;
    
    # Handle preflight requests
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-CSRF-TOKEN" always;
        add_header Access-Control-Max-Age 86400 always;
        add_header Content-Type "text/plain; charset=utf-8" always;
        add_header Content-Length 0 always;
        return 204;
    }
    
    try_files $uri $uri/ @fallback;
}

# Fallback for gamedata requests
location @fallback {
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-CSRF-TOKEN" always;
    try_files $uri /index.php?$query_string;
}

# Static file caching
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
EOF

# PHP configuration overrides
RUN echo 'max_execution_time = 300' >> /usr/local/etc/php/conf.d/custom.ini \
    && echo 'upload_max_filesize = 20M' >> /usr/local/etc/php/conf.d/custom.ini \
    && echo 'post_max_size = 20M' >> /usr/local/etc/php/conf.d/custom.ini \
    && echo 'memory_limit = 256M' >> /usr/local/etc/php/conf.d/custom.ini \
    && echo 'opcache.enable=1' >> /usr/local/etc/php/conf.d/custom.ini \
    && echo 'opcache.memory_consumption=256' >> /usr/local/etc/php/conf.d/custom.ini \
    && echo 'opcache.interned_strings_buffer=16' >> /usr/local/etc/php/conf.d/custom.ini \
    && echo 'opcache.max_accelerated_files=10000' >> /usr/local/etc/php/conf.d/custom.ini

# Set correct ownership
RUN chown -R www-data:www-data /var/www/html

RUN install-php-extensions sockets intl gd

COPY --chmod=755 ./entrypoint.d/ /etc/entrypoint.d/

# Switch back to www-data user
USER www-data

RUN php artisan storage:link --force --silent

# serversideup/php uses S6 overlay to manage nginx + php-fpm
# No need to specify CMD, it's handled by the base image