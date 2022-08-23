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

        function get_forecasts($backwardsSeconds, $forwardsSeconds) {
            $begin = time() - $backwardsSeconds;
            $end = time() + $forwardsSeconds;

            $fetchedResult = [];
            $dataStatement = $this->prepare("
            SELECT a.'timestamp' - 3600, a.forecast * c.factor, avg(b.pv_input), avg(b.battery_charge) 
            from forecasts a 
                left join readings b on b.'timestamp' between a.'timestamp' - 7200 and a.'timestamp' - 3600 
                left join forecastFactor c on c.'month' = strftime('%m', DATETIME(a.'timestamp', 'unixepoch')) and c.'hour' = strftime('%H', DATETIME(a.'timestamp', 'unixepoch'))
            where a.'timestamp' between :left and :right 
            group by a.'timestamp' 
            order by a.'timestamp' ASC ;
            ");
            $dataStatement->bindValue(':left', $begin);
            $dataStatement->bindValue(':right', $end);
            $dataResult = $dataStatement->execute();
            
            $result = [];

            while ($element = $dataResult->fetchArray()) {

                $result[] = $this->parseForecast($element);
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

        function get_next_hours_forecast($number) {
            $current = time();
            $timespan = $number * 3600;

            $currentState = $this->get_current_state();
            $forecasts = $this->get_forecasts(3600, $timespan);

            $secondsIntoHour = $current - $forecasts[0]["timestamp"];
            $partOfHour = $secondsIntoHour / 3600;

            // $result = [
            //     [
            //         "consumption" => 1,
            //         "timestamp" => time(),
            //         "maxValue" => 2,
            //         "excess" => 1,
            //         "state" => 1
            //     ],
            //     [
            //         "consumption" => 1,
            //         "timestamp" => time() + 3600,
            //         "maxValue" => 1.5,
            //         "excess" => 0.5,
            //         "state" => 0
            //     ],
            //     [
            //         "consumption" => 1,
            //         "timestamp" => time() + 3600 + 3600,
            //         "maxValue" => 2.5,
            //         "excess" => 1.5,
            //         "state" => 1
            //     ],
            //     [
            //         "consumption" => 1,
            //         "timestamp" => time() + 3600 + 3600 + 3600,
            //         "maxValue" => 3.5,
            //         "excess" => 2.5,
            //         "state" => 2
            //     ],
            //     [
            //         "consumption" => 1,
            //         "timestamp" => time() + 3600 + 3600 + 3600 + 3600,
            //         "maxValue" => 3.5,
            //         "excess" => 2.5,
            //         "state" => 2
            //     ],
            //     [
            //         "consumption" => 1,
            //         "timestamp" => time() + 3600 + 3600 + 3600 + 3600 + 3600,
            //         "maxValue" => 1.5,
            //         "excess" => 0.5,
            //         "state" => 1
            //     ]
            // ];

            $result = [];

            for ($step = 0; $step < $number; $step++) {
                $forecast = $forecasts[$step];
                $consumption = $currentState["consumption"];
                
                // THIS PART SHOULD BE CHANGED WHEN PV IS NOT LOWERED!!!
                
                $maxValue = $step == 0 ?
                    $currentState["pvSystemOutput"] :
                    $forecast["forecast"] + ($forecasts[$step + 1]["forecast"] - $forecast["forecast"]) * $partOfHour;

                // $maxValue = max($forecast["forecast"] + ($forecasts[$step + 1]["forecast"] - $forecast["forecast"]) * $partOfHour, $currentState["pvInput"]);
                
                $excess = max($maxValue - $consumption, 0);

                $state = 0;
                if ($excess > 2) {
                    $state = 2;
                } else if ($excess > 1) {
                    $state = 1;
                }

                $percent = min($excess, 2) / 2;

                $result[] = [
                    "consumption" => $consumption,
                    "timestamp" => $forecast["timestamp"] + $secondsIntoHour,
                    "maxValue" => $maxValue,
                    "excess" => $excess,
                    "state" => $state,
                    "percent" => $percent
                ];
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

        private function parseForecast($data) {
            return [
                "timestamp" => $data[0],
                "forecast" => $data[1],
                "data" => $data[2] ? max($data[2] + max($data[3], 0), 0) : NULL
            ];
        }
    }
?>