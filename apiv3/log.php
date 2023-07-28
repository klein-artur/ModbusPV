<?php

$logs = [];

$logs[] = [
    'timestamp' => microtime(true),
    'timespan' => .0,
    'message' => 'Starting the logs right now.'
];

function logMessage(string $message) {
    if (!isset($_GET['log'])) {
        return;
    }
    global $logs;
    $lastLog = $logs[array_key_last($logs)];
    $lastLogTime = $lastLog['timestamp'];

    $currentTime = microtime(true);
    $duration = $currentTime - $lastLogTime;

    $logs[] = [
        'timestamp' => $currentTime,
        'timespan' => $duration,
        'message' => $message
    ];
}

function prepareReturn($data) {
    global $logs;
    if (isset($_GET['log'])) {
        $newData = $data;
        $newData['logs'] =  $logs;
        return $newData;
    } else {
        return $data;
    }
}

?>