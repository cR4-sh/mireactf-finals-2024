<?php
session_start();
if (!isset($_SESSION['user'])){
    header('Location: /login.php');
    echo 'Вы не авторизованы';
    die();
}