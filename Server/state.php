<?php
    header('Content-type: application/json');

    include 'db/sqliteConnect.php';

    echo json_encode((new MyDB())->get_current_state());
?>