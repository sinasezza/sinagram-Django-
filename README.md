# sinagram-Django-
a minimal messenger like Telegram 

<pre>
1- it can send message and delete it and so on.
2- user can create account and login to account to use messenger
3- user should create some contact and send message to contacts(if the contact has account too)
4- user can change profile and delete it , can change contact information or delte it and ...
</pre>


# Requirements
<pre>
asgiref==3.6.0
Django==4.1.5
Pillow==9.4.0
psycopg2==2.9.5
sqlparse==0.4.3
tzdata==2022.7
</pre>

# Database
in this project I used Postgresql database
<br/>
instead you can use Django`s default database(Sqlite)
<br/>
add this commands to /sinagram/settings.py:
<br/>
<pre>
DATABASES = {
    'default': {
       'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
  }
}
</pre>

