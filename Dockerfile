FROM php:8.1-apache

# Install required PHP extensions
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    && docker-php-ext-install curl

# Enable mod_rewrite for Apache
RUN a2enmod rewrite

# Set the working directory
WORKDIR /var/www/html

# Copy the application files
COPY . /var/www/html

# Set permissions for the web server
RUN chown -R www-data:www-data /var/www/html && chmod -R 777 /var/www/html

# Start the Apache server
CMD ["apache2-foreground"]
