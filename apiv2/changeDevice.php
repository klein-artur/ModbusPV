<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    header('Content-type: application/json');

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $deviceIdentifier = $_POST['identifier'];

        $string = file_get_contents("../deviceconfig.json");
        $config = json_decode($string,true);

        $found;

        foreach ($config as &$device) {
            if (isset($device['priority'])) {
                if ($device['identifier'] == $deviceIdentifier) {
                    $found = $device;
                }
            }
        }

        if (!$found) {
            echo json_encode([
                'result' => false,
                'output' => "device identifier not valid."
            ]);
            exit;
        }

        if (isset($_GET['prio'])) {

            $prio = $_POST['prio'];

            $samePrio;
            
            if ($device['priority'] == $prio) {
                $samePrio = $found;
            }

            if ($prio < 0 || $prio > 100) {
                echo json_encode([
                    'result' => false,
                    'output' => "value not valid."
                ]);
                exit;
            }
    
            if (isset($samePrio) && $found !== $samePrio) {
                echo json_encode([
                    'result' => false,
                    'output' => "A device with the same priority already exists."
                ]);
                exit;
            }
    
            $found['priority'] = intval($prio);

        }

        if (isset($_POST['name'])) {
            $found['name'] = $_POST['name'];
        }

        if (isset($_POST['estimated_consumption'])) {
            $found['estimated_consumption'] = intval($_POST['estimated_consumption']);
        }

        if (isset($_POST['min_on_time'])) {
            $found['min_on_time'] = intval($_POST['min_on_time']);
        }

        if (isset($_POST['min_off_time'])) {
            $found['min_off_time'] = intval($_POST['min_off_time']);
        }

        $result = [];
        foreach ($config as $device) {
            if ($device['identifier'] == $deviceIdentifier) {
                $result[] = $found;
            } else {
                $result[] = $device;
            }
        }

        $newContent = json_encode($result, JSON_PRETTY_PRINT);

        file_put_contents("../deviceconfig.json", $newContent);

        echo json_encode([
            'result' => true,
            'output' => 'done'
        ]);
    } else {
        echo json_encode([
            'result' => false,
            'output' => 'Only POST method is allowed.'
        ]);
    }
    
?>