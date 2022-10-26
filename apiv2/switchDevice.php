<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    header('Content-type: application/json');

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $deviceIdentifier = $_POST['identifier'];
        $switch = $_POST['switch'];

        $command = escapeshellcmd('../Server/control.py "'.$deviceIdentifier.'" switch='.$switch);
        $output = shell_exec('cd ../Server; '.$command);

        echo json_encode([
            'result' => true
        ]);
    } else {
        echo json_encode([
            'result' => false
        ]);
    }
    
?>