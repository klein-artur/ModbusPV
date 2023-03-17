<?php

include 'config.php';
require_once('log.php');

enum TimePeriod {
    case Day;
    case Month;
    case Week;
    case Year;
    case FullYear;

    function beginAndEndTimestamps(int $offset): array {
        $date = new DateTime();

        return match($this) {
            TimePeriod::Day => [
                $date->modify("-$offset day")->setTime(0, 0, 0)->getTimestamp(),
                $date->setTime(23, 59, 59)->getTimestamp()
            ],
            TimePeriod::Month => [
                $date->modify("-$offset month")->setDate((int)$date->format('Y'), (int)$date->format('m'), 1)->setTime(0, 0, 0)->getTimestamp(),
                $date->setDate((int)$date->format('Y'), (int)$date->format('m'), (int)cal_days_in_month(CAL_GREGORIAN, (int)$date->format('m'), (int)$date->format('Y')))->setTime(23, 59, 59)->getTimestamp()
            ],
            TimePeriod::Week => [
                $date->modify("-$offset week")->modify('monday this week')->setTime(0, 0, 0)->getTimestamp(),
                $date->modify('sunday this week')->setTime(23, 59, 59)->getTimestamp()
            ],
            TimePeriod::Year => [
                $date->modify("-$offset year")->setDate((int)$date->format('Y'), 1, 1)->setTime(0, 0, 0)->getTimestamp(),
                $date->setDate((int)$date->format('Y'), 12, 31)->setTime(23, 59, 59)->getTimestamp()
            ],
            TimePeriod::FullYear => [
                $date->modify("-" . (($offset + 1) * 365) . " day")->setTime(0, 0, 0)->getTimestamp(),
                (new DateTime())->modify("-" . ($offset * 366) . " day")->setTime(23, 59, 59)->getTimestamp()
            ],
        };
    }
 
    public static function fromString(string $string): ?TimePeriod {
        $stringToEnum = [
            'Day' => TimePeriod::Day,
            'Month' => TimePeriod::Month,
            'Week' => TimePeriod::Week,
            'Year' => TimePeriod::Year,
            'FullYear' => TimePeriod::FullYear,
        ];

        return isset($stringToEnum[$string]) ? $stringToEnum[$string] : null;
    }
};

function secondsInMonthWithOffset(int $offset) {
    // Get the current date minus the offset
    $date = new DateTime();
    $date->modify("-$offset month");

    // Get the month and year of the modified date
    $currentMonth = $date->format('m');
    $currentYear = $date->format('Y');

    // Get the number of days in the modified month
    $daysInMonth = cal_days_in_month(CAL_GREGORIAN, $currentMonth, $currentYear);

    // Calculate the number of seconds in the modified month
    $secondsInMonth = $daysInMonth * 24 * 60 * 60;

    return $secondsInMonth;
}

function secondsInYearWithOffset(int $offset) {
    // Get the current date minus the offset
    $date = new DateTime();
    $date->modify("-$offset year");

    // Get the year of the modified date
    $currentYear = $date->format('Y');

    // Check if the year is a leap year
    $isLeapYear = (($currentYear % 4 == 0) && ($currentYear % 100 != 0)) || ($currentYear % 400 == 0);

    // Calculate the number of seconds in the year
    $secondsInYear = ($isLeapYear ? 366 : 365) * 24 * 60 * 60;

    return $secondsInYear;
}

function secondsInWeekWithOffset(int $offset) {
    // Get the current date
    $date = new DateTime();

    // Find the number of days between the current date and the last Monday
    $daysSinceMonday = ($date->format('N') - 1) % 7;

    // Move to the last Monday (beginning of the week)
    $date->modify("-$daysSinceMonday days");

    // Apply the offset
    $date->modify("-$offset weeks");

    // Calculate the number of seconds in the week
    $secondsInWeek = 7 * 24 * 60 * 60;

    return $secondsInWeek;
}

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
        
        return $this->parse($dataResult->fetch_assoc());
    }

    function getForecasts($backwardsSeconds, $forwardsSeconds) {
        $current = time();
        $begin = $current - $backwardsSeconds;
        $end = $current + $forwardsSeconds;

        $fetchedResult = [];
        $dataStatement = $this->connection->prepare('
        SELECT * from forecasts where timestamp between ? and ?;');

        $dataStatement->bind_param('ss', $begin, $end);
        $dataStatement->execute(); 
        $dataResult = $dataStatement->get_result();
        
        $result = [];

        while ($forecast = $dataResult->fetch_assoc()) {

            if ($forecast['timestamp'] <= $current) {
                $pvDataStatement = $this->connection->prepare('
                select avg(pv_input) as `pv_input` from readings where timestamp between ? - 3600 and ?
                ');
                $pvDataStatement->bind_param('ss', $forecast['timestamp'], $forecast['timestamp']);
                $pvDataStatement->execute();
                $pvDataResult = $pvDataStatement->get_result();
                $pvData = $pvDataResult->fetch_assoc();
    
                $forecast['pv_input'] = $pvData['pv_input'];
            } else {
                $forecast['pv_input'] = NULL;
            }

            $date = getdate($forecast['timestamp']);
            $month = $date["mon"];
            $hour = $date["hours"];

            $factorStatement = $this->connection->prepare('
            select `factor` from `forecastFactor` where `month` = ? and `hour` = ?;
            ');
            $factorStatement->bind_param('ss', $month, $hour);
            $factorStatement->execute();
            $factor = $factorStatement->get_result()->fetch_assoc()['factor'];
            
            $forecast['orig_forecast'] = $forecast['forecast'];

            if ($forecast['timestamp'] > $current) {
                $date = getdate($forecast['timestamp']);
                $forecast['forecast'] *= $factor;
            }
            
            $result[] = $this->parseForecast($forecast);
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
                "forced" => $element['forced'] == 1 ? TRUE : FALSE
            ];
        }
        
        return [
            "identifier" => "",
            "isOn" => FALSE,
            "lastChange" => time(),
            "consumption" => 0.0,
            "temperature" => NULL,
            "forced" => FALSE
        ];
    }

    function getDailyHistory($days = 1, $resolution = 20) {
        $h24 = time() - 86400 * $days;

        $fetchedResult = [];

        $dataStatement = $this->connection->prepare("SELECT avg(id) as `id`, avg(grid_output) as `grid_output`, avg(battery_charge) as `battery_charge`, avg(pv_input) as `pv_input`, round(avg(battery_state)) as `battery_state`, avg(`timestamp`) as `timestamp` FROM readings WHERE `timestamp` BETWEEN ? and ? GROUP BY round(`timestamp` / 60 / ?)  ORDER BY `timestamp` ASC;");
        $timeInAnHour = time() + 3600;
        $dataStatement->bind_param('sss', $h24, $timeInAnHour, $resolution);
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

        $onDevicesPower = 0.0;
        
        $config = json_decode(file_get_contents("../deviceconfig.json"), true);

        foreach ($config as $deviceConfig) {
            $device = $this->getDeviceInfo($deviceConfig['identifier']);
            if ($device['consumption'] && !$device['forced'] && $device['isOn']) { 
                $onDevicesPower += $device['consumption'];
            }
        }

        $result = [];
        $consumption = $currentState["consumption"] - $onDevicesPower;

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

    private function getIncomeForMinusPeriod($minusPeriod, TimePeriod $period) {
        global $GRID_FEED_PRICE_CENT;
        global $GRID_DRAW_PRICE_CENT;
        $beginningAndEndTimestamps = $period->beginAndEndTimestamps($minusPeriod);
        $beginningOfPeriod = $beginningAndEndTimestamps[0];
        $endOfPeriod = $beginningAndEndTimestamps[1];
        $incomeSql = $this->connection->prepare('select IFNULL((select acc_grid_output from readings where `timestamp` between ? and ? order by `timestamp` desc limit 1), 0) - IFNULL((select acc_grid_output from readings where `timestamp` < ? and `acc_grid_output` is not null order by `timestamp` desc limit 1), 0) as income;');
        $expensesSql = $this->connection->prepare('select IFNULL((select acc_grid_input from readings where (`timestamp` between ? and ?) order by `timestamp` desc limit 1), 0) - IFNULL((select acc_grid_input from readings where `timestamp` < ? order by `timestamp` desc limit 1), 0) as expense;');

        $incomeSql->bind_param('sss', $beginningOfPeriod, $endOfPeriod, $beginningOfPeriod);
        $expensesSql->bind_param('sss', $beginningOfPeriod, $endOfPeriod, $beginningOfPeriod);

        $incomeSql->execute();

        $incomeKWh = $incomeSql->get_result()->fetch_assoc()['income'];

        $expensesSql->execute();

        $expensesKWh = $expensesSql->get_result()->fetch_assoc()['expense'];

        return ($incomeKWh * $GRID_FEED_PRICE_CENT - $expensesKWh * $GRID_DRAW_PRICE_CENT) / 100;
    }

    function getIncome(TimePeriod $period) {
        return [
            "today" => $this->getIncomeForMinusPeriod(0, $period),
            "yesterday" => $this->getIncomeForMinusPeriod(1, $period)
        ];
    }

    function getCurrentDeviceStatus(string $identifier) {
        $sql = $this->connection->prepare("select * from deviceStatus where identifier = ? order by `timestamp` desc limit 1;");
        $sql->bind_param('s', $identifier);
        $sql->execute();
        $dataResult = $sql->get_result();
        
        return $dataResult->fetch_assoc();
    }

    function saveDeviceStatus(string $identifier, ?bool $state, ?int $lastChange, ?bool $forced) {
        $current = $this->getCurrentDeviceStatus($identifier);
        
        $sql = $this->connection->prepare("insert into deviceStatus(identifier, state, timestamp, temperature_c, temperature_f, humidity, consumption, last_change, forced) values(?, ?, ?, ?, ?, ?, ?, ?, ?);");

        $toSaveState = $current['state'];
        if (!is_null($state)) {
            $toSaveState = $state ? 1 : 0;
        }

        $toSaveTemperature_c = $current['temperature_c'];
        $toSaveTemperature_f = $current['temperature_f'];
        $toSaveHumidity = $current['humidity'];
        $toSaveConsumption = $current['consumption'];
        
        $toSaveLastChange = $current['last_change'];
        if (!is_null($lastChange)) {
            $toSaveLastChange = $lastChange;
        }

        $toSaveForced = $current['forced'];
        if (!is_null($forced)) {
            $toSaveForced = $forced ? 1 : 0;
        }

        $time = time();

        $sql->bind_param('sssssssss', $identifier, $toSaveState, $time, $toSaveTemperature_c, $toSaveTemperature_f, $toSaveHumidity, $toSaveConsumption, $toSaveLastChange, $toSaveForced);
        $sql->execute();
    }


    private function parse($data) {
        return [
            "gridOutput" => $data['grid_output'],
            "batteryCharge" => $data['battery_charge'],
            "pvInput" => $data['pv_input'],
            "batteryState" => $data['battery_state'],
            "consumption" => $data['pv_input'] - $data['battery_charge'] - $data['grid_output'],
            "pvSystemOutput" => $data['pv_input'] - $data['battery_charge'],
            "timestamp" => intval($data['timestamp'])
        ];
    }

    private function parseForecast($data) {
        return [
            "timestamp" => $data['timestamp'],
            "forecast" => $data['forecast'],
            "data" => !is_null($data['pv_input']) ? max($data['pv_input'], 0) : NULL,
            "origForecast" => $data['orig_forecast']
        ];
    }

}

?>
