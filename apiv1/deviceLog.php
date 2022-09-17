<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    header('Content-type: application/json');

    include 'mysqlConnect.php';

    function findDevice($identifier, $array) {
        foreach ( $array as $element ) {
            if ( $identifier == $element['identifier'] ) {
                return $element;
            }
        }

        return false;
    }

    $string = file_get_contents("../deviceconfig.json");
    $config = json_decode($string,true);

    $deviceLog = (new MyDB())->getDeviceLog(50);

    foreach ( $deviceLog as &$device ) {
        $deviceConfig = findDevice($device['identifier'], $config);
        $name = $deviceConfig['identifier'];
        if (isset($deviceConfig['name'])) {
            $name = $deviceConfig['name'];
        }
        $device['name'] = $name;
    }

    echo json_encode($deviceLog);
?>