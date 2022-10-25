<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    require_once('log.php');

    logMessage('Starting device log fetch.');

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

    logMessage('deviceconfig is loaded.');

    $identifier = isset($_GET['identifier']) ? $_GET['identifier'] : NULL;

    logMessage('identifier is set to '.$identifier);

    $result = [];

    logMessage('opening the database and fetching the device logs.');
    $deviceLog = (new MyDB())->getDeviceLog(50, $identifier);
    logMessage('device logs fetched.');

    foreach ( $deviceLog as &$device ) {
        $deviceConfig = findDevice($device['identifier'], $config);
        if ($deviceConfig) {
            $name = $deviceConfig['identifier'];
            if (isset($deviceConfig['name'])) {
                $name = $deviceConfig['name'];
            }
            $device['name'] = $name;
            $result[] = $device;
        }
    }

    echo json_encode(prepareReturn($result));
?>