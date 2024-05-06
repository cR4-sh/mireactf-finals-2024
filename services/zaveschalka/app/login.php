<?php
session_start();
include "models/user.php";

if (isset($_SESSION['user'])) {
    header('Location: /profile.php');
    die();
}

if (isset($_POST['login']) && isset($_POST['password'])) {
    $filename = './users/'.md5($_POST['login'].getenv('SECRET')).'.txt';
    if (!file_exists($filename)){
        $err = 'Такого сотрудника не сущесвует...';
        header('Location: /login.php?err='.urlencode($err));
        echo($err);
        die();
    }

    $user = unserialize(file_get_contents($filename));
    if ($_POST['password'] !== $user->password){
        $err = 'Неверный пароль, дорогой сотрудник';
        header('Location: /login.php?err='.urlencode($err));
        echo($err);
        die();
    }

    $_SESSION['user'] = $user->login;
    header('Location: /profile.php');
    echo('Успешный вход');
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
        <div class="form-title">Вход в аккаунт</div>
        <form action="login.php" method="post">
            <div class="form-field">
                <input name="login" class="textarea-text" placeholder="Логин" autocomplete="off"></textarea>
                <input type="password" name="password" class="textarea-text" placeholder="Пароль"></textarea>
            </div>
            <button type="submit" class="submit-button"><b>Вход</b></button>
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
<!-- about -->
<div class="footer">
SCP-завещалка - с нами надежнее!
</div>
</body>
</html>
