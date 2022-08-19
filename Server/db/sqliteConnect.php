<?php
    class MyDB extends SQLite3
    {
        
        function __construct() {
            $this->open('db/data/database.db');
        }

        function get_current_state() {
            $result = $this->query('SELECT * from readings ORDER BY timestamp DESC LIMIT 1')->fetchArray();

            return $this->parse($result);
        }

        function get_forecasts() {
            $hMin24 = time() - 86400;
            $hPlu24 = time() + 86400;

            $fetchedResult = [];
            $dataStatement = $this->prepare("SELECT * FROM forecasts WHERE timestamp BETWEEN :left and :right ORDER BY timestamp ASC;");
            $dataStatement->bindValue(':left', $hMin24);
            $dataStatement->bindValue(':right', $hPlu24);
            $dataResult = $dataStatement->execute();
            
            $result = [];

            while ($element = $dataResult->fetchArray()) {

                $timestamp = $element[0];
                $nearestValueStatement = $this->prepare("SELECT * FROM readings WHERE ABS(:searchStamp - timestamp) < 1800 ORDER BY ABS(:searchStamp - timestamp) LIMIT 1;");
                $nearestValueStatement->bindValue(':searchStamp', $timestamp);
                $foundHistory = $nearestValueStatement->execute()->fetchArray();

                $result[] = $this->parseForecast($element, $foundHistory);
            }
            
            return $result;
        }

        function get_daily_history() {
            $h24 = time() - 86400;

            $fetchedResult = [];

            $dataStatement = $this->prepare("SELECT avg(id), avg(grid_output), avg(battery_charge), avg(pv_input), round(avg(battery_state)), avg(timestamp) FROM readings WHERE timestamp BETWEEN :left and :right GROUP BY timestamp / 60 / 20  ORDER BY timestamp ASC;");
            $dataStatement->bindValue(':left', $h24);
            $dataStatement->bindValue(':right', time() + 3600);
            $dataResult = $dataStatement->execute();

            $result = [];

            while ($element = $dataResult->fetchArray()) {
                $result[] = $this->parse($element);
            }
            
            return $result;

        }

        private function parse($data) {
            return [
                "gridOutput" => $data[1],
                "batteryCharge" => $data[2],
                "pvInput" => $data[3] + max($data[2], 0),
                "batteryState" => $data[4],
                "consumption" => $data[3] - min($data[2], 0) - $data[1],
                "pvSystemOutput" => $data[3] - min($data[2], 0),
                "timestamp" => $data[5]
            ];
        }

        private function parseForecast($data, $realData) {
            return [
                "timestamp" => $data[0],
                "forecast" => $data[1],
                "data" => $realData ? $realData[3] + max($realData[2], 0) : NULL
            ];
        }
    }
?>