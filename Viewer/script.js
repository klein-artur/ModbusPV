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

    showArrow: function (from, to, id, positive, value, speed) {
        var arrowHtml = "<div class='arrow-holder' id='" + id + "'>\
            <span class='arrow-kw'>" + (value != 0 ? `${value.toFixed(3)} KW` : "") + "</span> \
            <div class='arrow-line'>\
            </div>\
        </div>"
    
        this.append(arrowHtml);

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

        for (let i = 0; i < nrOfPushers; i++) {
            let pusherId = `${id}-pusher-${i}`;
            let leftPosition = i * 20 - 20;

            let zIndex = 100000000 - leftPosition;

            let firstOrSecond = i % 2 == 0 ? 'first' : 'second';

            let positiveOrNegative = positive ? 'positive' : 'negative';

            let pusher = `<div id="${pusherId}" class="${(value != 0 ? 'arrow-pusher' : 'arrow-pusher-still')} arrow-pusher-${firstOrSecond}-${positiveOrNegative}" style="z-index: ${zIndex}; left: ${leftPosition}px"></div>`;

            $(`#${id} > .arrow-line`).append(pusher);
        }

        window.setInterval(
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

        return $(this);
    }
});

var setBatteryProgress = function(progress) {
    $("#battery-progress").css({height: `${progress}%`});
    $("#battery-progress-label").text(`${progress}`);

};

var setArrow = function (from, to, fromId, toId, value, isPositive) {
    let arrowId = `${fromId}-to-${toId}`;

    $(`#${arrowId}`).remove();

    if (value === null) {
        return;
    }

    $('body').showArrow(
        from, 
        to,
        arrowId,
        isPositive,
        value,
        Math.ceil(5 * (value/ 20))
    );
}

var setPVToHomeArrow = function (value) {
    let pvSystem = $("#pv-system");
    let house = $("#house");

    setArrow(
        [pvSystem.offset().left + pvSystem.outerWidth() + 10, pvSystem.offset().top + pvSystem.outerHeight() / 2], 
        [house.offset().left - 10, house.offset().top + house.outerHeight() / 2],
        'pv-system',
        'home',
        value,
        true
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
        'battery-holder',
        'pv',
        value,
        false
    )
};

var setPowerPlantToHomeArrow = function (value) {
    let grid = $("#grid");
    let house = $("#house");

    setArrow(
        [grid.offset().left - 10, grid.offset().top + grid.outerHeight() / 2], 
        [house.offset().left + house.outerWidth() + 10, house.offset().top + house.outerHeight() / 2],
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
        [house.offset().left + house.outerWidth() + 10, house.offset().top + house.outerHeight() / 2],
        [grid.offset().left - 10, grid.offset().top + grid.outerHeight() / 2], 
        'power-plant',
        'house-plug',
        value,
        true
    )
};

var setConsumption = function (usage, pv, batteryOutput) {
    $('#house-consumption').text(`${usage.toFixed(3)} KW`);

    $('#house-consumption').removeClass('fatal');
    $('#house-consumption').removeClass('warning');
    $('#house-consumption').removeClass('cool');

    console.log(usage / pv);
    if (usage / (pv + batteryOutput) < 0.7) {
        $('#house-consumption').addClass('cool')
    } else if (usage / (pv + batteryOutput) > 1) {
        $('#house-consumption').addClass('fatalr');
    } else {
        $('#house-consumption').addClass('warning');
    }

    let topValue = Math.max(usage, pv) * 1.05;
    let pvPercent = Math.round(pv / topValue * 100);
    let homePercent = Math.round(usage / topValue * 100);
}

var setPVOutput = function (pv) {
    $('#pv-output').text(`${pv.toFixed(3)} KW`);
}

var setData = function (batteryState, batteryOutput, consumption, pvOutput) {

    setConsumption(
        consumption,
        pvOutput,
        batteryOutput
    );

    setPVOutput(
        pvOutput
    );

    let pvRest = pvOutput - batteryOutput;

    let gridFeed = pvRest - consumption;

    setBatteryProgress(batteryState);

    setPVToHomeArrow(pvRest);

    if (gridFeed >= 0) {
        setHomeToPowerPlantArrow(gridFeed);
    } else {
        setPowerPlantToHomeArrow(gridFeed * -1);
    }

    if (batteryOutput >= 0) {
        setPVToBatteryArrow(batteryOutput);
    } else {
        setBatteryToPVArrow(batteryOutput * -1);
    }
}

var placeInfoBox = function () {
    $("#info-box").css({top: `${ $("#flow-graph").outerHeight() + 16 }px`});
}

$(window).on('load', function () {

    let batteryState = 100;
    let batteryOutput = 0;

    let consumption = 2.335;
    let pvOutput = 18.335;

    setData(batteryState, batteryOutput, consumption, pvOutput);

    placeInfoBox();
  
})
