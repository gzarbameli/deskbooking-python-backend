FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD="root"
ENV MYSQL_DATABASE="project"
ENV MYSQL_USER="admin"
ENV MYSQL_PASSWORD="admin"

ADD creation.sql /docker-entrypoint-initdb.d

EXPOSE 3306