<?php

include "models/user.php";

session_start();
if (isset($_SESSION['user'])) {
    header('Location: /profile.php');
    die();
}

if (isset($_POST['login']) && isset($_POST['password']) && isset($_POST['phone']) && isset($_POST['email'])) {
    if (!preg_match('/^[a-zA-Z0-9]+$/', $_POST['login']) || !preg_match('/^[a-zA-Z0-9]+$/', $_POST['password'])){
        $err = 'Вы ввели неккоректные данные о себе, сотрудник';
        header('Location: /register.php?err='.urlencode($err));
        echo($err);
        die();
    }

    if (!preg_match('/^[0-9]+$/', $_POST['phone'])){
        $err = 'Вы ввели неккоректные данные о себе, сотрудник';
        header('Location: /register.php?err='.urlencode($err));
        echo($err);
        die();
    }

    if (!preg_match('/^[A-Z0-9._%+-]+@[A-Z0-9-]+.+.[A-Z]{2,4}$/i', $_POST['email'])){
        $err = 'Вы ввели неккоректные данные о себе, сотрудник';
        header('Location: /register.php?err='.urlencode($err));
        echo($err);
        die();
    }

    if (file_exists('./users/'.md5($_POST['login'].getenv('SECRET')).'.txt')){
        $err = 'Такой сотрудник уже зарегистрирован';
        header('Location: /register.php?err='.urlencode($err));
        echo($err);
        die();
    }

    $user = new User($_POST);
    $_SESSION['user'] = $user->login;
    header('Location: /profile.php');
    echo('Зарегистрировал сотрудника '.$_SESSION['user']);
    die();
} 

?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="static/css/styles.css">
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap" rel="stylesheet">
<title>Завещалка</title>
</head>
<body>

<div class="content-wrap">
    <div class="navbar">
        <div class="navbar-left">
            <a href="/index.php"><img src="/static/img/logo.png"></a>
            <a href="/index.php"><span class="navbar-brand">Завещалка</span></a>
        </div>
        <div>
            <a href="login.php">Вход в аккаунт</a>
            <a href="register.php">Регистрация</a>
        </div>
    </div>    
    <div class="form-login">
        <div class="form-title">Регистрация сотрудника</div>
        <form action="register.php" method="post">
            <div class="form-field">
                <input name="login" class="textarea-text" placeholder="Логин" autocomplete="off"></textarea>
                <input type="password" name="password" class="textarea-text" placeholder="Пароль" autocomplete="off"></textarea>
                <input name="email" class="textarea-text" placeholder="Email" autocomplete="off"></textarea>
                <input name="phone" class="textarea-text" placeholder="Телефон" autocomplete="off"></textarea>
            </div>
            <button type="submit" class="submit-button"><b>Зарегистрировать</b></button>
        </form>
    
    </div>
    <?php
    if (isset($_GET['err'])){
        echo '<div class="message message-error">
        '.htmlspecialchars($_GET['err'], ENT_QUOTES, 'UTF-8').'
        </div>';
    }
    ?>
</div>
<div class="footer">
SCP-завещалка - с нами надежнее!
</div>

<script>
let count = 1;
document.querySelector('.add-button').addEventListener('click', function() {    
    var newDiv = document.createElement('div');
    newDiv.innerHTML = '<textarea id="noteTextarea" name="user'+count+'" class="textarea-text" placeholder="Логин получателя доступа" rows="4"></textarea>';
    document.querySelector('.form-field').appendChild(newDiv);
    count += 1;
});
</script>
</body>
</html>
