<?php
  include("utils/auth_check.php");
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
    <?php
      if (isset($_GET['id']) && file_exists('wills/'.$_GET['id'].'.txt')){
        include("models/user.php");
        include("models/will.php");
    
        $username = $_SESSION['user'];
        $secret = getenv('SECRET');
      
        $uid = md5($username.$secret);

        $user = unserialize(file_get_contents('users/'.$uid.'.txt'));

        if (isset($user->wills) && in_array($_GET['id'], $user->wills)) {
          $will = unserialize(file_get_contents('wills/'.$_GET['id'].'.txt'));

          echo '<div class="form-wrapper">
                  <div class="form-title">Ознакомьтесь с последними словами ушедшего</div>
                  <div class="notes-table">
                  <table>
                    <thead>
                      <tr>
                        <th>ID завещания</th>
                        <th>'.$will->will_id.'</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th>Название</th>
                        <th>'.$will->title.'</th>
                      </tr>
                      <tr>
                        <th>Содержание</th>
                        <th>'.$will->will.'</th>
                      </tr>
                    </tbody>
                  </table>
                  </div>
                </div>';
        } else {
          echo '<div class="message message-error">У вас нет доступа к этому завещанию</div>';
        }

      } else {
        echo '<div class="message message-error">Такого завещания несуществует</div>';
      }
    ?>
  
    </div>
  <div class="footer">
  SCP-завещалка - с нами надежнее!
  </div>
</div>
</body>
</html>