<?php

include("utils/auth_check.php");
include "models/will.php";
include "models/user.php";

if (isset($_POST['title']) && isset($_POST['will'])) {
    if (strlen($_POST['title']) > 0 && strlen($_POST['will']) > 0 && !preg_match('/^[a-zA-Z0-9]+$/', $_POST['title']) || !preg_match('/^[a-zA-Z0-9=]+$/', $_POST['will'])){
        $err = 'Так мы не сможем запечетлить ваше последнее слово!';
        header('Location: /create_will.php?err='.urlencode($err));
        echo($err);
        die();
    }

    $will = new Will(['title' => $_POST['title'], 'will' => $_POST['will']]);

    $current_user = unserialize(file_get_contents('users/'.md5($_SESSION['user'].getenv('SECRET')).'.txt'));
    if (!isset($current_user->wills)) {
        $current_user->wills = array();
    }
    array_push($current_user->wills, $will->will_id); 
    
    $current_user->save();

    for($i = 0; $i < count($_POST) - 2; ++$i) {
        $username = $_POST['username'.$i];
        $user_id = md5($username.getenv('SECRET'));
        $filename = 'users/'.$user_id.'.txt';

        if (!file_exists($filename)) {
            continue;
        }
        $user = unserialize(file_get_contents($filename));

        if (!isset($user->wills)) {
            $user->wills = array();
        }
        if (in_array($will->will_id, $user->wills)) {
            continue;
        }

        array_push($user->wills, $will->will_id);
        $user->save();
    }

    header('Location: /will.php?id='.$will->will_id);
    echo('Успешно создано завещание');
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
            <a href="profile.php">Профиль</a>
            <a href="create_will.php">Создать завещание</a>
            <a href="logout.php">Выйти</a>
        </div>
    </div>    
    <div class="form-wrapper">
        <div class="form-title">Завещание</div>
        <div class="form-description">Здесь вы можете сказать свое последнее слово.</div>
        <form class= "hui" action="create_will.php" method="post">
            <div class="form-field">
            <label for="noteTextarea"></label>
            <input id="noteTextarea" name="title" class="input-area-text textarea-text" placeholder="Называние завещания">
            <textarea id="noteTextarea" name="will" class="textarea-text-big textarea-text" placeholder="Завещание" rows="4"></textarea>
            </div>
            <div class="form-field access-field">
                <label for="accessText">Кому выдать доступ</label>
                
                <button type="button" class="add-button">+</button>
            </div>
            <div class="sub">
                <button type="submit" class="submit-button"><b>Сохранить</b></button>
            </div>
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
let count = 0;
document.querySelector('.add-button').addEventListener('click', function() {    
    var newDiv = document.createElement('div');
    newDiv.innerHTML = '<input autocomplete="off" id="noteTextarea" name="username'+count+'" class="input-area-text textarea-text" placeholder="Логин сотрудника" rows="4"></textarea>';
    document.querySelector('.form-field').appendChild(newDiv);
    count += 1;
});
</script>
</body>
</html>
