<!doctype html>

<?php
    $SHOW_CONTRIBUTIONS = false;
?>

<html lang="en">
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-gH2yIJqKdNHPEq0n4Mqa/HGKIhSkIHeL5AyhkYV8i59U5AR6csBvApHHNl/vI1Bx" crossorigin="anonymous">

    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js" integrity="sha512-ElRFoEQdI5Ht6kZvyzXhYG9NqjtkmlkfYk0wr6wHxU9JEHakS7UJZNeml5ALk+8IKlU6jDgMabC3vkumRokgJA==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>

    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>PV Leistung</title>
    <meta name="author" content="Artur Hellmann">

    <meta property="og:title" content="PV Leistung">

    <link rel="stylesheet" href="styles.css">

    <?php if (isset($_GET["kiosk"])): ?>
        <link rel="stylesheet" href="kiosk.css">
    <?php endif; ?>

    <script src="jquery-3.6.0.min.js"></script>
    <script src="script.js"></script>
</head>

<body class="text-bg-dark">
    <div id="content">
        <div class="align-items-center pvbox" id="trafficlights">
            <div id="traffic-light-bars">
                <div class="traffic-light-bar-holder float-left text-center" id="tl-0">
                    <div class="tl-bar-content">
                        <div class="tl-bar bg-cool" id="tl-bar-0"></div>
                    </div>
                    <span id="tl-0-text">Jetzt</span>
                </div>
                <div class="traffic-light-bar-holder float-left text-center" id="tl-1">
                    <div class="tl-bar-content">
                        <div class="tl-bar bg-cool" id="tl-bar-1"></div>
                    </div>
                    <span id="tl-1-text">Jetzt</span>
                </div>
                <div class="traffic-light-bar-holder float-left text-center" id="tl-2">
                    <div class="tl-bar-content">
                        <div class="tl-bar bg-cool" id="tl-bar-2"></div>
                    </div>
                    <span id="tl-2-text">Jetzt</span>
                </div>
                <div class="traffic-light-bar-holder float-left text-center" id="tl-3">
                    <div class="tl-bar-content">
                        <div class="tl-bar bg-cool" id="tl-bar-3"></div>
                    </div>
                    <span id="tl-3-text">Jetzt</span>
                </div>
                <div class="traffic-light-bar-holder float-left text-center" id="tl-4">
                    <div class="tl-bar-content">
                        <div class="tl-bar bg-cool" id="tl-bar-4"></div>
                    </div>
                    <span id="tl-4-text">Jetzt</span>
                </div>
                <div class="traffic-light-bar-holder float-left text-center" id="tl-5">
                    <div class="tl-bar-content">
                        <div class="tl-bar bg-cool" id="tl-bar-5"></div>
                    </div>
                    <span id="tl-5-text">Jetzt</span>
                </div>
            </div>
        </div>
        <div class="align-items-center pvbox" id="flow-graph">
            <div id="pv-system" class="position-relative align-items-center text-center float-left bordered">
                <img id="pv" class="pictogram" src="solar-panel.png" /><br />
                <span id="pv-output" class="power-string cool">29.500 KW</span><br />
                <div id="battery-holder" class="center-h" >
                    <div id="battery-top"></div>
                    <div id="battery-body">
                        <div id="battery-100" class="battery-element text-center align-middle">
                            <span id="battery-progress-label">
                                50%
                            </span>
                            <div id="battery-progress">
                                <div id="battery-progress-l" class="half"></div>
                                <div id="battery-progress-m" class="half"></div>
                                <div id="battery-progress-r" class="half"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div> 

            <div id="house" class="float-left right-top text-center align-right bordered">
                <img class="pictogram"  src="low-energy.png" /><br />
                <span id="house-consumption" class="power-string">29.500 KW</span>
            </div>

            <div id="grid" class="right-bottom text-center float-left align-right bordered">
                <img class="pictogram"  src="electricity.png" /><br />
                <span id="grid-consumption" class="power-string">29.500 KW</span>
            </div>
        </div>
        <div id="consumption-box" class="pvbox">
            <div id="relative-usage" class="position-relative align-items-center text-center float-left">
                <div id="bar-description-provide" class="bar-description float-left">
                    Versorgung
                </div>
                <div class="bar-description float-none">
                    Verbrauch
                </div>
                <div class="bar-holder">
                    <div class="bar-element bg-cool" id="pv-bar"></div>
                    <div class="bar-element bg-warning" id="battery-bar"></div>
                    <div class="bar-element bg-fatal" id="grid-bar"></div>
                </div>
                <div class="bar-holder" id="consumption-bar-holder">
                    <div class="bar-element bg-cool" id="consumption-bar"></div>
                </div>
            </div>
        </div>
        <div id="income-info-box" class="pvbox">
            <span id="income" class="power-string">15,00 €</span>
            <span id="income-yesterday">15,00 €</span>
        </div>
        <div class="align-items-center pvbox" id="chart-consumption-box">
            <div id="chart-holder-consumption">
                <canvas id="chart-consumption" width="740" height="430"></canvas>
            </div>
        </div>
        <div class="align-items-center pvbox" id="chart-battery-box">
            <div id="chart-holder-battery">
                <canvas id="chart-battery" width="740" height="430"></canvas>
            </div>
        </div>
        <div class="align-items-center pvbox" id="chart-forecast-box">
            <div id="chart-holder-forecast">
                <canvas id="chart-forecast" width="740" height="430"></canvas>
            </div>
        </div>

        <?php if ($SHOW_CONTRIBUTIONS): ?>
            <div id="footer-box">
                <a href="https://www.flaticon.com/free-icons/low-energy" title="low energy icons">Low energy icons created by Flat Icons - Flaticon</a><br />
            </div>
        <?php endif; ?>
    </div>

</body>
</html>
