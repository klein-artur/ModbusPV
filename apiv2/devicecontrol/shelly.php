<?php

    function switchDevice($device, bool $on): bool {

        $isSuccess = false;
        $tries = 0;
        $shouldTry = true;

        while ($shouldTry && $tries != 4) {
            $tries++;
            $shouldTry = false;
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
            if ($response === false) 
                echo curl_error($curl);
            else {
                $result = json_decode($response);
                
                $isSuccess = $result->isok;
                if (!$isSuccess) {
                    if (property_exists($result, 'errors')) {
                        $errors = $result->errors;
                        if (property_exists($errors, 'max_req')) {
                            $shouldTry = true;
                            sleep(1);
                        } else {
                            print_r($result);
                        }
                    } else {
                        print_r($result);
                    }
                }
            }
            
            curl_close($curl);
        }
        return $isSuccess;
    }
?>