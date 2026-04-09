# web-development
## как запустить проект
1. создать `.env`-файл в корне проекта с содержанием файла `.env.example`
2. поменять в нем `SECRET_KEY` на настоящий
3. создать и применить миграции к базе данных:
```
python manage.py makemigrations
python manage.py migrate
```
4. запустить сервер
```
python manage.py runserver
```