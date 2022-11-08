<?php

    function switchDevice($device, bool $on) {
        $curl = curl_init();

        $url = $device['api_url'].'/device/relay/control';

        $postfields = $device['parameter'];
        $postfields['turn'] = $on ? 'on' : 'off';

        curl_setopt_array($curl, array(
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_ENCODING => '',
            CURLOPT_MAXREDIRS => 10,
            CURLOPT_TIMEOUT => 0,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
            CURLOPT_CUSTOMREQUEST => 'POST',
            CURLOPT_POSTFIELDS => $postfields
        ));
        
        $response = curl_exec($curl);

        $isSuccess = false;
        if ($response === false) 
            echo curl_error($curl);
        else {
            $isSuccess = json_decode($response)['isok'];
        }
        
        curl_close($curl);
        return $isSuccess;
    }
?>