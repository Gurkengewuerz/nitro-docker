FROM php:8.2-apache as builder

ARG COMMIT=d0c28fb

WORKDIR /var/www/html

RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    libonig-dev \
    libssl-dev \
    libzip-dev \
    git \
    zip \
    unzip \
    && docker-php-ext-install -j$(nproc) curl gd mbstring pdo_mysql sockets fileinfo zip \
    && docker-php-ext-enable curl gd mbstring pdo_mysql sockets fileinfo zip

COPY --from=composer:lts /usr/bin/composer /usr/local/bin/composer

RUN git config --global --add safe.directory /var/www/html
RUN git clone --recurse-submodules https://github.com/ObjectRetros/atomcms.git .
RUN git checkout $COMMIT

RUN composer install


# ---------------------------------------------
FROM node:lts as npm-builder

WORKDIR /var/www/html

COPY --from=builder /var/www/html /var/www/html

RUN yarn install
RUN yarn run build:atom


# ---------------------------------------------
FROM php:8.2-apache

WORKDIR /var/www/html

RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    libonig-dev \
    libssl-dev \
    libzip-dev \
    && docker-php-ext-install -j$(nproc) curl gd mbstring pdo_mysql sockets fileinfo \
    && docker-php-ext-enable curl gd mbstring pdo_mysql sockets fileinfo
RUN apt remove apt --autoremove -y --allow-remove-essential

RUN a2enmod rewrite

COPY --from=npm-builder /var/www/html /var/www/html
RUN rm -rf /var/www/html/node_modules

RUN chown -R www-data:www-data /var/www/html/storage \
    && chown -R www-data:www-data /var/www/html/bootstrap/cache

EXPOSE 80

ENV APACHE_DOCUMENT_ROOT /var/www/html/public

RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/sites-available/*.conf \
    && sed -ri -e 's!AllowOverride None!AllowOverride All!g' /etc/apache2/apache2.conf /etc/apache2/conf-available/*.conf

RUN echo 'max_execution_time = 120' >> /usr/local/etc/php/conf.d/docker-php-maxexectime.ini;

CMD ["apache2-foreground"]
