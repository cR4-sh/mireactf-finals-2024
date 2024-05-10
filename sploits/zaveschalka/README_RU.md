# Writeup for zaveschalka

![service](img/service.png)

## Description

Приложуха на php представляла из себя сервис завещаний для сотрудников класса D. При создании завещания можно было расшарить к нему доступ. Все сущности, завещания и пользователи, хранились как сериализованные объекты в папках `wills` и `users` соответственно. 

## Bugs

### Bug №1

При регистрации объект пользователя создавался на основе всей мапы `$_POST`, однако перед этим валидируются только интендед параметры для регистрации (login, password, email, phone):

``` php
// register.php
$user = new User($_POST);

// models/user.php
class User {
    public function __construct(array $attributes) {
        foreach ($attributes as $name => $value) {
            $this->{$name} = $value;
        }
        $this->save();
    }

    public function save() {
        file_put_contents('./users/'.md5($this->login.getenv('SECRET')).'.txt', serialize($this));
    }
}
```

С фронтенда при запросе на `/register.php` мы нигде не видим отправку других параметров, однако, исходя из логики создания и шаринга завещаний мы можем понять, что у класса `User` используется еще массив `wills`, в котором содержатся айдишники завещаний, к которым у пользователя есть доступ, однако сами проверки доступов к завещаниям безопасны:

```php
// Создание записок и обновление массива wills
$will = new Will(['title' => $_POST['title'], 'will' => $_POST['will']]);

$current_user = unserialize(file_get_contents('users/'.md5($_SESSION['user'].getenv('SECRET')).'.txt'));
if (!isset($current_user->wills)) {
    $current_user->wills = array();
}
array_push($current_user->wills, $will->will_id); 

// Проверка доступа к завещаниям
$user = unserialize(file_get_contents('users/'.$uid.'.txt'));

if (isset($user->wills) && in_array($_GET['id'], $user->wills)) {
    $will = unserialize(file_get_contents('wills/'.$_GET['id'].'.txt'));
    ...
}
```

Соберя в едино эти два факта, мы можем понять, что, благодаря кривой функции регистрации, мы можем создать пользователя, добавив в качестве его атрибута массив wills, в ячейках которых будут указаны id-шники из attack-dat'ы:

Выглядить это будет как-то так:

``` php
// Отправдяем post-параметр на ручку /register.php и в качестве даты указываем что-то типо:
login=FrakenboK&password=iloveRobertSama&email=noLifeOnlyPWN@crash.mirea&phone=1337&wills[0]=<will_id>&wills[1]=<will_id>&...
// И так далее
```

Вариант фикса:

``` php
if (count($_POST) > 4) {
    echo 'IDI NAHUI';
    die();
}
```

[Сплойт](./exploit_object_injection.py)

### Bug №2

Второй багой был миссконфиг в apache. Он позволял нам читать все файлы в директории `/var/www/mireactf`. Проблема заключалась в отсутствии rewrite-правила на блеклист все, что не входит в вайтлист. Таким образом, мы могли читать все файлы, а не только заватлисченные по расширениям. Сплойтим через чтение файлов завещаний с сериализованными объектами.

Уязвимый конфиг:

``` conf
<Directory "/var/www/mireactf">
    Options +FollowSymLinks
    AllowOverride None
    Require all granted
    RewriteEngine On
    DirectoryIndex index.php
    RewriteCond %{REQUEST_FILENAME} -f
    RewriteCond %{REQUEST_URI} !\.(php|css|png)$
</Directory>
```

Вариант фикса:

``` conf
    RewriteRule . - [F,NC]
```

[Сплойт](./exploit_apache_missconfig.py)

### Powered by [FrakenboK](https://t.me/helloworlddlrowolleh)