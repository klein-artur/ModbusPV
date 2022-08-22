var activeArrows = {}
var chartBattery
var chartConsumption
var chartForecast

var charPointRadius = 1

const days = [
    'So',
    'Mo',
    'Di',
    'Mi',
    'Do',
    'Fr',
    'Sa'
  ]

function number_format(number, decimals, dec_point, thousands_sep) {
    var n = !isFinite(+number) ? 0 : +number, 
        prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
        sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
        dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
        toFixedFix = function (n, prec) {
            // Fix for IE parseFloat(0.55).toFixed(0) = 0;
            var k = Math.pow(10, prec);
            return Math.round(n * k) / k;
        },
        s = (prec ? toFixedFix(n, prec) : Math.round(n)).toString().split('.');
    if (s[0].length > 3) {
        s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }
    if ((s[1] || '').length < prec) {
        s[1] = s[1] || '';
        s[1] += new Array(prec - s[1].length + 1).join('0');
    }
    return s.join(dec);
}

$.fn.extend({

    rotateArrow: function (radiants) {
        $(this).css({'transform-origin' : 'center left'});
        $(this).css({'transform' : 'rotate('+ radiants +'rad)'});
        return $(this);
    },

    flipText: function () {
        $(this).css({'transform-origin' : 'center center'});
        $(this).css({'transform' : 'rotate('+ 180 +'deg) translate(50%, 50%)'});
        return $(this);
    },

    arrowLength: function (length) {
        $(this).css({'width' : `${length}px`});
        return $(this);
    },

    showArrow: function (from, to, id, positive, value, speed, redraw = false) {
        var elementExists = id in activeArrows

        let forceRedraw = !elementExists || activeArrows[id].positive != positive || (activeArrows[id].value == 0 && value != 0) || (activeArrows[id].value != 0 && value == 0) || redraw

        if (forceRedraw) {
            if (elementExists) {
                $("#"+id).remove()
            }

            var arrowHtml = "<div class='arrow-holder' id='" + id + "'>\
                <span class='arrow-kw'>" + (value != 0 ? `${number_format(value, 3, ',')} KW` : "") + "</span> \
                <div class='arrow-line'>\
                </div>\
            </div>"
        
            this.append(arrowHtml);
        } else {
            $(`#${id} > .arrow-kw`).text(value != 0 ? `${number_format(value, 3, ',')} KW` : "")
        }

        let xOffset = to[0] - from[0];
        let yOffset = to[1] - from[1];

        let angle = Math.atan(yOffset / xOffset);

        let isInLeftHalf = xOffset < 0;

        if (isInLeftHalf) {
            angle += Math.PI;
            $(`#${id} > .arrow-kw`).flipText();
        }

        let length = Math.sqrt(xOffset ** 2 + yOffset ** 2);

        let nrOfPushers = Math.ceil(length / 20 + 2);

        if (nrOfPushers % 2 != 0) {
            nrOfPushers += 1;
        }

        if (forceRedraw) {

            $(`#${id} > .arrow-line`).empty();

            for (let i = 0; i < nrOfPushers; i++) {
                let pusherId = `${id}-pusher-${i}`;
                let leftPosition = i * 20 - 20;

                let zIndex = 100000000 - leftPosition;

                let firstOrSecond = i % 2 == 0 ? 'first' : 'second';

                let positiveOrNegative = positive ? 'positive' : 'negative';

                let pusher = `<div id="${pusherId}" class="${(value != 0 ? 'arrow-pusher' : 'arrow-pusher-still')} arrow-pusher-${firstOrSecond}-${positiveOrNegative}" style="z-index: ${zIndex}; left: ${leftPosition}px"></div>`;

                $(`#${id} > .arrow-line`).append(pusher);
            }
        }

        if (elementExists) {
            window.clearTimeout(activeArrows[id]["intervalId"]);
            delete activeArrows[id];
        }

        let intervalId = window.setInterval(
            function () {

                $(`#${id}`).rotateArrow(0);

                let mostLeftPosition = 0;

                [...$(`#${id} > .arrow-line`).children().sort((a, b) => {
                    return $(a).position().left - $(b).position().left;
                })].forEach((pusher, idx, array)=> {
                    let currentLeftPosition = $(pusher).position().left;

                    let newLeftPosition = currentLeftPosition + speed;

                    if (newLeftPosition > length + 10 && idx === array.length - 1) {
                        newLeftPosition = mostLeftPosition - 20;
                    }

                    mostLeftPosition = mostLeftPosition > newLeftPosition ? newLeftPosition : mostLeftPosition;

                    let zIndex = Math.floor(10000 - newLeftPosition);
        
                    $(pusher).css({left: `${newLeftPosition}px`, 'z-index': `${zIndex}`});
                });

                $(`#${id}`).rotateArrow(angle);
            },
            33
        );

        $(`#${id}`).css({top: from[1] - 10, left: from[0], position:'absolute'});
        $(`#${id}`).arrowLength(length);
        $(`#${id}`).rotateArrow(angle);

        activeArrows[id] = {
            "intervalId": intervalId,
            "positive": positive,
            "value": value
        }

        return $(this);
    }
});

var setBatteryProgress = function(progress) {
    $("#battery-progress").css({height: `${progress}%`});
    $("#battery-progress-label").text(`${progress}`);

};

var setArrow = function (from, to, fromId, toId, value, isPositive) {
    let arrowId = `${fromId}-to-${toId}`;

    if (value === null) {
        return;
    }

    $('body').showArrow(
        from, 
        to,
        arrowId,
        isPositive,
        value,
        5 * (1 - Math.pow(0.5, value))
    );
}

var setPVToHomeArrow = function (value) {
    let pvSystem = $("#pv-system");
    let house = $("#house");

    setArrow(
        [pvSystem.offset().left + pvSystem.outerWidth() + 10, house.offset().top + house.outerHeight() / 2], 
        [house.offset().left - 10, house.offset().top + house.outerHeight() / 2],
        'pv-system',
        'home',
        value,
        true
    )
};

var setHomeToPVArrow = function (value) {
    let pvSystem = $("#pv-system");
    let house = $("#house");

    setArrow(
        [house.offset().left - 10, house.offset().top + house.outerHeight() / 2],
        [pvSystem.offset().left + pvSystem.outerWidth() + 10, house.offset().top + house.outerHeight() / 2], 
        'pv-system',
        'home',
        value,
        false
    )
};


var setPVToBatteryArrow = function (value) {
    let pvImage = $("#pv-output");
    let batteryHolder = $("#battery-holder");

    setArrow(
        [pvImage.offset().left + pvImage.outerWidth() / 2, pvImage.offset().top + pvImage.outerHeight() + 10], 
        [batteryHolder.offset().left + batteryHolder.outerWidth() / 2, batteryHolder.offset().top - 10],
        'pv',
        'battery-holder',
        value,
        true
    )
};

var setBatteryToPVArrow = function (value) {
    let batteryHolder = $("#battery-holder");
    let pvImage = $("#pv-output");

    setArrow( 
        [batteryHolder.offset().left + batteryHolder.outerWidth() / 2, batteryHolder.offset().top - 10],
        [pvImage.offset().left + pvImage.outerWidth() / 2, pvImage.offset().top + pvImage.outerHeight() + 10], 
        'pv',
        'battery-holder',
        value,
        false
    )
};

var setPowerPlantToHomeArrow = function (value) {
    let grid = $("#grid");
    let house = $("#house");

    setArrow(
        [grid.offset().left + grid.outerWidth() / 2, grid.offset().top - 10], 
        [house.offset().left + house.outerWidth() / 2, house.offset().top + house.outerHeight() + 10],
        'power-plant',
        'house-plug',
        value,
        false
    )
};

var setHomeToPowerPlantArrow = function (value) {
    let grid = $("#grid");
    let house = $("#house");

    setArrow(
        [house.offset().left + house.outerWidth() / 2, house.offset().top + house.outerHeight() + 10],
        [grid.offset().left + grid.outerWidth() / 2, grid.offset().top - 10], 
        'power-plant',
        'house-plug',
        value,
        true
    )
};

var setGridOutput = function (gridOutput) {
    $("#grid-consumption").text(`${number_format(Math.abs(gridOutput), 3, ',')} KW`)

    $('#grid-consumption').removeClass('fatal');
    $('#grid-consumption').removeClass('cool');

    if (gridOutput >= 0) {
        $('#grid-consumption').addClass('cool')
    } else {
        $('#grid-consumption').addClass('fatal');
    }
}

var setConsumption = function (usage, pvNetOutput) {
    $('#house-consumption').text(`${number_format(usage, 3, ',')} KW`);

    $('#house-consumption').removeClass('fatal');
    $('#house-consumption').removeClass('warning');
    $('#house-consumption').removeClass('cool');

    if (usage / pvNetOutput < 0.7) {
        $('#house-consumption').addClass('cool')
    } else if (usage / pvNetOutput > 1) {
        $('#house-consumption').addClass('fatal');
    } else {
        $('#house-consumption').addClass('warning');
    }

    // let topValue = Math.max(usage, pv) * 1.05;
    // let pvPercent = Math.round(pv / topValue * 100);
    // let homePercent = Math.round(usage / topValue * 100);
}

var setPVOutput = function (pv) {
    $('#pv-output').text(`${number_format(pv, 3, ',')} KW`);
}

var setData = function (gridOutput, batteryCharge, batteryState, consumption, pvSystemOutput, pvInput) {

    setConsumption(
        consumption,
        pvSystemOutput
    );

    setPVOutput(
        pvInput
    );

    setGridOutput(
        gridOutput
    );

    setBatteryProgress(batteryState);

    if (pvSystemOutput >= 0) {
        setPVToHomeArrow(pvSystemOutput);
    } else {
        setHomeToPVArrow(pvSystemOutput * -1);
    }

    if (gridOutput >= 0) {
        setHomeToPowerPlantArrow(gridOutput);
    } else {
        setPowerPlantToHomeArrow(gridOutput * -1);
    }

    if (batteryCharge >= 0) {
        setPVToBatteryArrow(batteryCharge);
    } else {
        setBatteryToPVArrow(batteryCharge * -1);
    }

    fillConsumptionBars(
        pvInput, gridOutput, batteryCharge
    )
}

var placeFooterBox = function () {
    $("#footer-box").css({top: `${ $("#info-box").offset().top + $("#info-box").outerHeight() }px`});
}

var fillConsumptionBars = function (pvInput, gridOutput, batteryCharge) {
    let consumption = pvInput - Math.min(batteryCharge, 0) - gridOutput;

    let upperBound = Math.max(consumption, pvInput, gridOutput * -1, Math.min(batteryCharge, 0) * -1);
    let consumptionPercent = consumption / upperBound * 100;
    let pvPercent = pvInput / upperBound * 100;
    let batteryPercent = Math.min(batteryCharge, 0) / upperBound * -100;
    let gridPercent = Math.min(gridOutput, 0) / upperBound * -100;

    $('#consumption-bar').css({
        bottom: 0,
        height: `${consumptionPercent}%`
    });

    $('#pv-bar').css({
        bottom: 0,
        height: `${pvPercent}%`
    });

    $('#battery-bar').css({
        bottom: `${pvPercent}%`,
        height: `${batteryPercent}%`
    });

    $('#grid-bar').css({
        bottom: `${pvPercent + batteryPercent}%`,
        height: `${gridPercent}%`
    });

}

var createBatteryChart = function (data) {
    let ctx = $("#chart-battery")

    let batteryStates = data.map(element => {

        const date = new Date(element.timestamp * 1000);

        return {
            x: `${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`,
            y: element.batteryState
        }
        
    })

    if (chartBattery) {
        chartBattery.destroy()
    }

    chartBattery = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Batterieladung',
                data: batteryStates,
                cubicInterpolationMode: 'monotone',
                fill: false,
                borderColor: 'rgb(92, 169, 69)',
                tension: 3
            }]
        },
        options: {
            scales: {
                yAxis: {
                    max: 100,
                    min: 0,
                    ticks: {
                        color: "white"
                    }
                },
                xAxis: {
                    ticks: {
                        color: "white"
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Batterieladung',
                    color: "white"

                },
            },
            animation: false,

            elements: {
                point:{
                    radius: charPointRadius
                }
            }
        }
    });

    chartBattery.height = 430
    chartBattery.width = 740
}

var createConsumptionChart = function (data) {
    let ctx = $("#chart-consumption")

    let consumptions = data.map(element => {

        const date = new Date(element.timestamp * 1000);

        return {
            x: `${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`,
            y: element.consumption
        }
        
    })

    let batteryConsumption = data.map(element => {

        const date = new Date(element.timestamp * 1000);

        return {
            x: `${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`,
            y: element.batteryCharge * -1
        }
        
    })

    let creations = data.map(element => {

        const date = new Date(element.timestamp * 1000);

        return {
            x: `${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`,
            y: element.pvInput
        }
        
    })

    let gridOutput = data.map(element => {

        const date = new Date(element.timestamp * 1000);

        return {
            x: `${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`,
            y: element.gridOutput
        }
        
    })

    if (chartConsumption) {
        chartConsumption.destroy()
    }

    chartConsumption = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Verbrauch',
                data: consumptions,
                cubicInterpolationMode: 'monotone',
                fill: false,
                borderColor: 'rgb(219, 53, 69)',
                tension: 0.1
            }, {
                label: 'Erzeugung',
                data: creations,
                cubicInterpolationMode: 'monotone',
                fill: false,
                borderColor: 'rgb(92, 169, 69)',
                tension: 0.1
            }, {
                label: 'Einspeisung',
                data: gridOutput,
                cubicInterpolationMode: 'monotone',
                fill: false,
                borderColor: 'rgb(249, 160, 27)',
                tension: 0.1
            }, {
                label: 'Batterie',
                data: batteryConsumption,
                cubicInterpolationMode: 'monotone',
                fill: false,
                borderColor: 'rgb(254, 254, 254)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                yAxis: {
                    ticks: {
                        color: "white"
                    }
                },
                xAxis: {
                    ticks: {
                        color: "white"
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: "white"
                    }
                },
                title: {
                    display: true,
                    text: 'Leistung',
                    color: "white"

                },
            },
            animation: false,

            elements: {
                point:{
                    radius: charPointRadius
                }
            }
        }
    });

    chartConsumption.height = 430
    chartConsumption.width = 740
}

var createForecastChart = function (data) {
    let ctx = $("#chart-forecast")

    let forecastData = data.map(element => {

        const date = new Date(element.timestamp * 1000);
        const day = days[date.getDay()];

        return {
            x: `${day}, ${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`,
            y: element.forecast
        }
        
    })

    let creations = data.map(element => {

        const date = new Date(element.timestamp * 1000);
        const day = days[date.getDay()];

        return {
            x: `${day}, ${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`,
            y: element.data
        }
        
    })

    if (chartForecast) {
        chartForecast.destroy()
    }

    chartForecast = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Realwert',
                data: creations,
                cubicInterpolationMode: 'monotone',
                fill: false,
                borderColor: 'rgb(92, 169, 69)',
                tension: 0.1
            }, {
                label: 'Vorhersage',
                data: forecastData,
                cubicInterpolationMode: 'monotone',
                fill: false,
                borderColor: 'rgb(254, 254, 254)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                yAxis: {
                    ticks: {
                        color: "white"
                    }
                },
                xAxis: {
                    ticks: {
                        color: "white"
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: "white"
                    }
                },
                title: {
                    display: true,
                    text: 'Vorhersage',
                    color: "white"

                },
            },
            animation: false,

            elements: {
                point:{
                    radius: charPointRadius
                }
            }
        }
    });

    chartForecast.height = 430
    chartForecast.width = 740
}

function setNextHours(nextHours) {
    let numberOfHours = nextHours.length

    for (i=0; i<numberOfHours; i++) {
        let hour = nextHours[i]
        let barId = `#tl-bar-${i}`

        $(barId).removeClass('bg-cool')
        $(barId).removeClass('bg-warning')
        $(barId).removeClass('bg-fatal')

        switch (hour.state) {
            case 0:
                $(barId).addClass('bg-fatal')
                break;
            case 1:
                $(barId).addClass('bg-warning')
                break;
            case 2:
                $(barId).addClass('bg-cool')
                break;
        }

        let percentage = Math.min(hour.excess, 2) / 2.0
        let realPercentage = 80 * percentage + 20

        $(barId).css({'height': `${realPercentage}%`})

        var date = new Date(hour.timestamp * 1000);

        if (i > 0)
            $(`#tl-${i}-text`).text(date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}))

    }
}

function startTimeout() {
    window.tid = setTimeout(() => {
        $(document).scrollTop(0);
    }, 30000)
}

$(window).on('load', function () {

    $(document).scrollTop(0);

    var doneFunction = function( data ) {
        setData(data.gridOutput, data.batteryCharge, data.batteryState, data.consumption, data.pvSystemOutput, data.pvInput)
    }

    var historyDoneFunction = function (data) {
        createBatteryChart(data)
        createConsumptionChart(data)
    }

    var forecastDoneFunction = function (forecasts) {
        createForecastChart(forecasts)
    }

    var nextHoursDoneFunction = function (nextHours) {
        setNextHours(nextHours)
    }

    var loadData = function () {
        console.log("Load new data.")
        $.ajax({
            url: `Server/state.php`
        })
            .done(doneFunction)
            .always(() => {
                console.log("Data got, set new timeout for data.")
                setTimeout(() => {
                    loadData()
                }, 1000)
            })
    }

    var loadHistory = function () {
        console.log("load new history.")
        $.ajax({
            url: `Server/history.php`
        })
            .done(historyDoneFunction)
            .always(() => {
                console.log("History got, set new timeout for history.")
                setTimeout(() => {
                    loadHistory()
                }, 1000)
            })
    }

    var loadForecast = function () {
        console.log("load new forecast.")
        $.ajax({
            url: `Server/forecasts.php`
        })
            .done(forecastDoneFunction)
            .always(() => {
                console.log("Forecast got, set new timeout for forecast.")
                setTimeout(() => {
                    loadForecast()
                }, 1000)
            })
    }

    var loadNextHours = function () {
        console.log("load new nextHours")
        $.ajax({
            url: `Server/nextHours.php`
        })
            .done(nextHoursDoneFunction)
            .always(() => {
                console.log("nextHours got, set new timeout for nextHours.")
                setTimeout(() => {
                    loadNextHours()
                }, 1000)
            })
    }

    loadData();
    loadHistory();
    loadForecast();
    loadNextHours();

    placeFooterBox();

    startTimeout();
  
})

$(document).scroll(() => {
    window.tid && clearTimeout(window.tid);
    startTimeout();
})
