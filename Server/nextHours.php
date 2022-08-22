<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    header('Content-type: application/json');

    include 'db/sqliteConnect.php';

    echo json_encode((new MyDB())->get_next_hours_forecast(6));
?>