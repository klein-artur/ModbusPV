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

        function get_daily_history() {
            $currentTimestamp = time() + 1;
            $h24 = time() - 86400;

            $numberStatement = $this->prepare("SELECT COUNT(*) FROM readings WHERE timestamp BETWEEN :left and :right;");
            $numberStatement->bindValue(':left', $h24);
            $numberStatement->bindValue(':right', $currentTimestamp);
            $number = $numberStatement->execute()->fetchArray()[0];

            $ratio = ceil($number / 50);

            $dataStatement = $this->prepare("SELECT * FROM readings WHERE timestamp BETWEEN :left and :right AND ROWID % :ratio = 0 ORDER BY timestamp ASC;");
            $dataStatement->bindValue(':left', $h24);
            $dataStatement->bindValue(':right', $currentTimestamp);
            $dataStatement->bindValue(':ratio', $ratio);
            $dataResult = $dataStatement->execute();

            $result = [];

            while ($element = $dataResult->fetchArray()) {
                $result[] = $this->parse($element);
            }
            
            return $result;

        }

        private function parse($data) {
            return [
                "gridOutput" => $data["grid_output"],
                "batteryCharge" => $data["battery_charge"],
                "pvInput" => $data["pv_input"],
                "batteryState" => $data["battery_state"],
                "consumption" => $data["pv_input"] - min($data["battery_charge"], 0) - $data["grid_output"],
                "pvSystemOutput" => $data["pv_input"] - min($data["battery_charge"], 0),
                "timestamp" => $data["timestamp"]
            ];
        }
    }
?>