<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    header('Content-type: application/json');

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $deviceIdentifier = $_POST['identifier'];
        $type = $_POST['type'];
        $value = $_POST['value'];

        if ($value != "on" && $value != "off") {
            echo json_encode([
                'result' => false,
                'output' => "value not valid."
            ]);
            exit;
        }
        if ($type != "switch" && $type != "mode") {
            echo json_encode([
                'result' => false,
                'output' => "type not valid."
            ]);
            exit;
        }

        $string = file_get_contents("../deviceconfig.json");
        $config = json_decode($string,true);

        $found = false;

        foreach ($config as $device) {
            if ($device['identifier'] == $deviceIdentifier) {
                $found = true;
                break;
            }
        }

        if (!$found) {
            echo json_encode([
                'result' => false,
                'output' => "device identifier not valid."
            ]);
            exit;
        }

        $command = escapeshellcmd('./control.py "'.$deviceIdentifier.'" '.$type.'='.$value);
        $output = shell_exec('cd ../Server; '.$command);

        echo json_encode([
            'result' => true,
            'output' => $output
        ]);
    } else {
        echo json_encode([
            'result' => false
        ]);
    }
    
?>