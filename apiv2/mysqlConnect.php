<?php

include 'config.php';
require_once('log.php');

class MyDB {

    protected $connection;

    public function __construct() {
        global $MYSQL_HOST;
        global $MYSQL_USER;
        global $MYSQL_PASSWORD;
        global $MYSQL_DATABASE;
        logMessage('opening the database now.');
		$this->connection = new mysqli($MYSQL_HOST, $MYSQL_USER, $MYSQL_PASSWORD, $MYSQL_DATABASE);
        logMessage('database openede.');
		if ($this->connection->connect_error) {
			$this->error('Failed to connect to MySQL - ' . $this->connection->connect_error);
		}
	}

    function getCurrentState() {
        $dataStatement = $this->connection->prepare('SELECT * from readings ORDER BY timestamp DESC LIMIT 1');
        $dataStatement->execute();
        $dataResult = $dataStatement->get_result();
        
        return $this->parse($dataResult->fetch_assoc());;
    }

    function getForecasts($backwardsSeconds, $forwardsSeconds) {
        $current = time();
        $begin = $current - $backwardsSeconds;
        $end = $current + $forwardsSeconds;

        $fetchedResult = [];
        $dataStatement = $this->connection->prepare('
        SELECT max(a.timestamp) as `timestamp`, max(a.forecast * IF(a.timestamp > ?, c.factor, 1)) as `forecast`, avg(b.pv_input) as `pv_input`, avg(b.battery_charge) as `battery_charge`, a.forecast as `orig_forecast`
        from forecasts a 
            left join readings b on b.timestamp between a.timestamp - 3600  and a.timestamp
            left join forecastFactor c on c.month = DATE_FORMAT(FROM_UNIXTIME(a.timestamp), "%m") and c.hour = DATE_FORMAT(FROM_UNIXTIME(a.timestamp), "%H")
        where a.timestamp between ? and ?
        group by a.timestamp
        order by a.timestamp ASC;');



        $dataStatement->bind_param('sss', $current, $begin, $end);
        $dataStatement->execute();
        $dataResult = $dataStatement->get_result();
        
        $result = [];

        while ($element = $dataResult->fetch_assoc()) {
            $result[] = $this->parseForecast($element);
        }
        
        return $result;
    }

    function getDeviceLog($limit, $identifier = NULL) {
        $sql;
        logMessage('getting device logs from the database.');
        if ($identifier) {
            $sql = $this->connection->prepare("
                select deviceStatus.* from deviceStatus inner join 
                (select `last_change`, `identifier`, max(`timestamp`) as `timestamp` from `deviceStatus` where `last_change` > 0 group by `last_change`, `identifier`) as max_states 
                on deviceStatus.last_change = max_states.last_change 
                and deviceStatus.`timestamp` = max_states.timestamp 
                and deviceStatus.identifier = max_states.identifier
                where deviceStatus.identifier = ?
                order by deviceStatus.last_change desc 
                limit $limit;	
            ");

            $sql->bind_param('s', $identifier);
        } else {
            $sql = $this->connection->prepare("
                select deviceStatus.* from deviceStatus inner join 
                (select `last_change`, `identifier`, max(`timestamp`) as `timestamp` from `deviceStatus` where `last_change` > 0 group by `last_change`, `identifier`) as max_states 
                on deviceStatus.last_change = max_states.last_change 
                and deviceStatus.`timestamp` = max_states.timestamp 
                and deviceStatus.identifier = max_states.identifier
                order by deviceStatus.last_change desc 
                limit $limit;	
            ");
        }
        
        logMessage('trying to execute the sql.');
        $sql->execute();

        logMessage('sql executed. Trying to get the result.');

        $dataResult = $sql->get_result();

        logMessage('result fetched.');

        $result = [];

        while ($element = $dataResult->fetch_assoc()) {
            $result[] =  [
                "identifier" => $element['identifier'],
                "isOn" => $element['state'] == 1 ? TRUE : FALSE,
                "lastChange" => $element['last_change']
            ];
        }

        logMessage('logs fetched. Return them now.');
        
        return $result;
    }

    function getDeviceInfo($identifier) {
        $sql = $this->connection->prepare("select * from deviceStatus where `identifier` = ? order by `timestamp` desc limit 1;");
        
        $sql->bind_param('s', $identifier);
        $sql->execute();
        $dataResult = $sql->get_result();

        while ($element = $dataResult->fetch_assoc()) {
            $consumption = NULL;
            if (array_key_exists('consumption', $element)) {
                $consumption = $element['consumption'] / 1000;
            }
            return [
                "identifier" => $element['identifier'],
                "isOn" => $element['state'] == 1 ? TRUE : FALSE,
                "lastChange" => $element['last_change'],
                "consumption" => $consumption,
                "temperature" => $element['temperature_c'],
                "forced" => $element['forced']
            ];
        }
        
        
    }

    function getDailyHistory() {
        $h24 = time() - 86400;

        $fetchedResult = [];

        $dataStatement = $this->connection->prepare("SELECT avg(id) as `id`, avg(grid_output) as `grid_output`, avg(battery_charge) as `battery_charge`, avg(pv_input) as `pv_input`, round(avg(battery_state)) as `battery_state`, avg(`timestamp`) as `timestamp` FROM readings WHERE `timestamp` BETWEEN ? and ? GROUP BY round(`timestamp` / 60 / 20)  ORDER BY `timestamp` ASC;");
        $timeInAnHour = time() + 3600;
        $dataStatement->bind_param('ss', $h24, $timeInAnHour);
        $dataStatement->execute();
        $dataResult = $dataStatement->get_result();

        $result = [];

        while ($element = $dataResult->fetch_assoc()) {
            $result[] = $this->parse($element);
        }
        
        return $result;
    }

    function getNextHoursForecast($number) {
        $current = time();
        $timespan = $number * 3600;

        $currentState = $this->getCurrentState();

        $forecasts = $this->getForecasts(3600, $timespan);

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

        $onDevicesSql = 'select deviceStatus.consumption as consumption from deviceStatus,
        (select identifier, max(`timestamp`) as `timestamp` from deviceStatus group by identifier) max_states
            where deviceStatus.identifier = max_states.identifier
            and deviceStatus.timestamp = max_states.timestamp
            and deviceStatus.`state` = 1;';
        $deviceStateSql = $this->connection->prepare($onDevicesSql);
        $deviceStateSql->execute();
        $deviceStateRows = $deviceStateSql->get_result();

        $onDevicesPower = 0.0;
        while ($element = $deviceStateRows->fetch_assoc()) {
            if ($element['consumption']) { 
                $onDevicesPower += $element['consumption'];
            }
        }

        $result = [];
        $consumption = $currentState["consumption"] - $onDevicesPower / 1000;

        for ($step = 0; $step < $number; $step++) {
            $forecast = $forecasts[$step];
            
            // THIS PART SHOULD BE CHANGED WHEN PV IS NOT LOWERED!!!
            
            $maxValue = $step == 0 ?
                $currentState["pvInput"] :
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

    private function getIncomeForMinusDay($minusDay) {
        global $GRID_FEED_PRICE_CENT;
        global $GRID_DRAW_PRICE_CENT;
        $beginningOfDay = time() - time() % 86400 - date('Z') - ($minusDay * 86400);
        $endOfDay = $beginningOfDay + 86400;

        $incomeSql = $this->connection->prepare('select (select acc_grid_output from readings where `timestamp` between ? and ? order by `timestamp` desc limit 1) - (select acc_grid_output from readings where `timestamp` < ? order by `timestamp` desc limit 1) as income;');
        $expensesSql = $this->connection->prepare('select (select acc_grid_input from readings where (`timestamp` between ? and ?) order by `timestamp` desc limit 1) - (select acc_grid_input from readings where `timestamp` < ? order by `timestamp` desc limit 1) as expense;');

        $incomeSql->bind_param('sss', $beginningOfDay, $endOfDay, $beginningOfDay);
        $expensesSql->bind_param('sss', $beginningOfDay, $endOfDay, $beginningOfDay);

        $incomeSql->execute();

        $incomeKWh = $incomeSql->get_result()->fetch_assoc()['income'];

        $expensesSql->execute();

        $expensesKWh = $expensesSql->get_result()->fetch_assoc()['expense'];

        return ($incomeKWh * $GRID_FEED_PRICE_CENT - $expensesKWh * $GRID_DRAW_PRICE_CENT) / 100;
    }

    function getIncome() {
        return [
            "today" => $this->getIncomeForMinusDay(0),
            "yesterday" => $this->getIncomeForMinusDay(1)
        ];
    }




    private function parse($data) {
        return [
            "gridOutput" => $data['grid_output'],
            "batteryCharge" => $data['battery_charge'],
            "pvInput" => $data['pv_input'],
            "batteryState" => $data['battery_state'],
            "consumption" => $data['pv_input'] - $data['battery_charge'] - $data['grid_output'],
            "pvSystemOutput" => $data['pv_input'] - $data['battery_charge'],
            "timestamp" => $data['timestamp']
        ];
    }

    private function parseForecast($data) {
        return [
            "timestamp" => $data['timestamp'],
            "forecast" => $data['forecast'],
            "data" => !is_null($data['pv_input']) ? max($data['pv_input'] + max($data['battery_charge'], 0), 0) : NULL,
            "origForecast" => $data['orig_forecast']
        ];
    }

}

?>