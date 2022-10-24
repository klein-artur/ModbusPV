<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    header('Content-type: application/json');

    $type = $_GET['type'];

    include 'mysqlConnect.php';

    $string = file_get_contents("../deviceconfig.json");
    $config = json_decode($string,true);

    $result = [];

    $dbRepo = new MyDB();

    foreach ( $config as $deviceConfig ) {

        if ($deviceConfig['type'] == $type) {
            $device = $dbRepo->getDeviceInfo($deviceConfig['identifier']);
            if ($device) {
                $name = $deviceConfig['identifier'];
                if (isset($deviceConfig['name'])) {
                    $name = $deviceConfig['name'];
                }
                $device['name'] = $name;
                $result[] = $device;
            }
        }

    }

    echo json_encode($result);
?>
