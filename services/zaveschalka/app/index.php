<?php
session_start();
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
      <?php
      if (isset($_SESSION['user'])){
        echo '<a href="profile.php">Профиль</a>
              <a href="create_will.php">Создать завещание</a>
              <a href="logout.php">Выйти</a>';
      } else {
        echo '<a href="login.php">Вход в аккаунт</a>
              <a href="register.php">Регистрация</a>';
      }
      ?>
    </div>
  </div>


  <div class="welcome-page">
    <div>
      <div class="welcome-message">
        Дорогие сотрудники класса D.
      <ul>
        <li>На данном веб-ресурсе вам будет дана возможность ссказать свое последние влово.</li>
        <li>С уважением, руководство фонда.</li>
      </ul>
      </div>
    </div>
  </div>
</div>
<div class="footer">
SCP-завещалка - с нами надежнее!
</div>


</body>
</html>
