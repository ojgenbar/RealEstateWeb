# Как это таки включить?

## Установка БД:
Берем репозиторий для БД:

    git clone https://github.com/ojgenbar/RealEstateDB.git

Устанавливаем PostgreSQL и PostGIS (у меня 10 версия, но на последующих должно быть норм).

Запускаем **psql**.
Указываем путь до генерирующего скрипта и гененрируем базу данных:

    \i structure.sql

Создаем **вьюхи**:

    \i configure_groups.sql

Настраиваем **роли**:

    \i configure_groups.sql

Создаем роль **web_app**

    CREATE USER web_app;
    GRANT viewer TO web_app;

Восстанавливаем данные (я сделал сэмпл для тебя), например так:

    \i real_estate_sample_20190420_180328.sql


## Установка приложения:

Тащим репозиторий:

    git clone https://github.com/ojgenbar/RealEstateWeb.git

Ставим anaconda (или miniconda)

Запускаем **Anaconda Promt** и оттуда:
Переходим в папку RealEstateWeb

    cd RealEstateWeb

Устанавливаем локальную среду python:
    
    conda env create -p py35_web -f conda_env_file.yml

Запускаем:
    
    py35_web/python run.py

