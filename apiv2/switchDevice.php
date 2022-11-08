<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    header('Content-type: application/json');

    require_once('mysqlConnect.php');

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

        $result = false;
        $output = "";

        switch ($type) {
            case 'switch':
                switch ($device['device']) {
                    case 'shelly':
                        require_once('devicecontrol/shelly.php');
                }

                if (switchDevice($device, $value == 'on')) {
                    (new MyDB())->saveDeviceStatus($device['identifier'], $value == 'on', time(), true);
                    $result = true;
                    $output = 'done';
                } else {
                    $result = false;
                    $output = 'Switching the device did not work.';
                }

                break;
            case 'mode':
                (new MyDB())->saveDeviceStatus($device['identifier'], NULL, NULL, $value == 'on');
                $result = true;
                $output = 'done';
                break;
        }

        echo json_encode([
            'result' => true,
            'output' => $output
        ]);
    } else {
        echo json_encode([
            'result' => false,
            'output' => 'Only POST method is allowed.'
        ]);
    }
    
?>