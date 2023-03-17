<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    header('Content-type: application/json');

    $period = isset($_GET['period']) ? $_GET['period'] : "Day";

    include 'mysqlConnect.php';

    echo json_encode((new MyDB())->getIncome(TimePeriod::from($period)));
?>