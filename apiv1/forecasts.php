<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    header('Content-type: application/json');

    include 'sqliteConnect.php';

    echo json_encode((new MyDB())->getForecasts(86400, 86400));
?>