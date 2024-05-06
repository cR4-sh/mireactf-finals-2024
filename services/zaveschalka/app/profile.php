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
<title>Завещательница</title>
</head>
<body>

<div class="content-wrap">
  <div class="navbar">
    <span class="navbar-brand">Завещательница</span>
    <div>
      <a href="profile.php">Профиль</a>
      <a href="create_will.php">Создать завещание</a>
      <a href="logout.php">Выйти</a>
    </div>
  </div>    
  <div class="form-wrapper">
  <div class="form-title">Профиль пользователя</div>
  <?php
    include("models/user.php");

    $username = $_SESSION['user'];
    $secret = getenv('SECRET');

    $uid = substr(`echo -n '$username$secret' | md5sum`, 0, 32);
    $user = unserialize(file_get_contents('users/'.$uid.'.txt'));

    echo '<div class="profile-info">
            <p><strong>Имя пользователя:</strong> '.$user->login.'</p>
            <p><strong>Почта:</strong> '.$user->email.'</p>
            <p><strong>Номер телефона:</strong> '.$user->phone.'</p>
          </div>';

    if (!isset($user->wills) || count($user->wills) == 0){
      echo '<h4>У вас еще нет завещаний. <a href="/create_will.php">Создать</a>.</h4>';
    }
    else {

      echo '<div class="notes-table">
              <table>
                <thead>
                  <tr>
                    <th>ID завещания</th>
                  </tr>
                </thead>
                <tbody>';
                
      foreach ($user->wills as $will) {
        echo  '<tr>
                <td><a href="will.php?id='.$will.'">'.$will.'</td>
              </tr>';
      }
      echo '</tbody>
          </table>
        </div>';
}
?>
</div>
</div>
<div class="footer">
Сервис завещаний - с нами надежнее! | 8-800-5555-35-35
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
