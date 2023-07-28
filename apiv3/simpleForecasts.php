<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    header('Content-type: application/json');

    $start = isset($_GET['starttime']) ? $_GET['starttime'] : time();


    include 'mysqlConnect.php';

    echo json_encode((new MyDB())->getForecasts($start, 0 ,86400, true));
?>