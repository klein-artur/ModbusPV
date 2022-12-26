<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    header('Content-type: application/json');

    $type = isset($_GET['type']) ? $_GET['type'] : '';

    include 'mysqlConnect.php';

    $string = file_get_contents("../deviceconfig.json");
    $config = json_decode($string,true);

    function findDeviceByIdentifier($identifier){
        global $config;

        foreach ( $config as $element ) {
            if ( $identifier == $element['identifier'] ) {
                return $element;
            }
        }

        return false;
    }

    function getDeviceForIdentifier($deviceConfig) {
        global $dbRepo;
        $device = $dbRepo->getDeviceInfo($deviceConfig['identifier']);
        if ($device) {
            $name = $deviceConfig['identifier'];
            if (isset($deviceConfig['name'])) {
                $name = $deviceConfig['name'];
            }
            $device['name'] = $name;
            $device['priority'] = $deviceConfig['priority'];
            $device['estimatedConsumption'] = $deviceConfig['estimated_consumption'];
        }
        return $device;
    }

    $result = [];

    $dbRepo = new MyDB();

    if (isset($_GET['identifier'])) {

        $deviceConfig = findDeviceByIdentifier($_GET['identifier']);

        if ($deviceConfig) {
            $result = getDeviceForIdentifier($deviceConfig);
        }

    } else {

        foreach ( $config as $deviceConfig ) {
    
            if ($deviceConfig['type'] == $type) {
                
                $result[] = getDeviceForIdentifier($deviceConfig);
            }
    
        }
    }

    echo json_encode($result);
?>
