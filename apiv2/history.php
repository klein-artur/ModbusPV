<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    header('Content-type: application/json');

    include 'mysqlConnect.php';

    $days = isset($_GET['days']) ? $_GET['days'] : 1;
    $resolution = isset($_GET['resolution']) ? $_GET['resolution'] : 20;
    $sum = isset($_GET['sum']) ? TRUE : FALSE;

    if ($sum) {
        echo json_encode((new MyDB())->getHistory($days, $resolution));
    } else {
        echo json_encode((new MyDB())->getDailyHistory($days, $resolution));
    }
?>