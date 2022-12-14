<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    header('Content-type: application/json');

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $string = file_get_contents("../deviceconfig.json");
        $config = json_decode($string,true);

        foreach ($config as &$device) {
            $searchIdentifier = str_replace(' ', '_', $device['identifier']);
            if (isset($_POST[$searchIdentifier])) {
                $device['priority'] = intval($_POST[$searchIdentifier]);
            }
        }

        $newContent = json_encode($config, JSON_PRETTY_PRINT);

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