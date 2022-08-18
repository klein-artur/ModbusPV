<?php
    header('Content-type: application/json');
    header("Access-Control-Allow-Origin: *");
    header("Access-Control-Allow-Headers: *");

    include 'db/sqliteConnect.php';

    echo json_encode((new MyDB())->get_current_state());
?>