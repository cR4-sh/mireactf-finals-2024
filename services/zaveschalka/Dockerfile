FROM php:7.4-apache

RUN apt update && apt-get install -y supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ADD apache.conf /etc/apache2/sites-available/000-default.conf

WORKDIR /var/www/mireactf

COPY ./app /var/www/mireactf

RUN mkdir /var/www/mireactf/wills
RUN mkdir /var/www/mireactf/users

RUN chmod -R 777 /var/www/mireactf
RUN chown -R www-data /var/www/mireactf

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN a2enmod rewrite

ENTRYPOINT ["sh", "/entrypoint.sh"]