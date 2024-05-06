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
<title>Завещательница</title>
</head>
<body>

<!-- baseline -->
<div class="content-wrap">
  <div class="navbar">
    <span class="navbar-brand">Завещательница</span>
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
      Добро пожаловать в нашу завещательницу!
      <ul>
        <li>Здесь вы можете оставить свое завещание</li>
        <li>Его увидят только те, кому вы это позволите</li>
      </ul>
      </div>
    </div>
  </div>
</div>
<div class="footer">
Сервис завещаний - с нами надежнее! | 8-800-5555-35-35
</div>


</body>
</html>
