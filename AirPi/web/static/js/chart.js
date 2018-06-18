'use strict';

let response;
//let body;
let Testwaarden = "";
let arraymin = [];
let arrayplus = [];
let arraydagen = [];
let place = "";

document.addEventListener('DOMContentLoaded', function() {
    init();
});

function init() {
    //body = document.getElementById("body");
    getWeather("Gent");
}

function drawChart() {
    let ctx = document.getElementById("myChart");
    let myChart = new Chart(ctx, {
        type: 'line',

        data: {
            datasets: [{
                    fill: false,
                    borderColor: '#1E90FF',
                    label: 'Min',
                    data: arraymin
                },
                {
                    fill: '-1',
                    borderColor: '#FF4500',
                    label: 'Max',
                    data: arrayplus
                }
            ],
            labels: ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        suggestedMin: 10,
                        suggestedMax: 30
                    }
                }]
            }
        }
    });
}

function getWeather(place) {
    //let place = "Kortrijk"

            place = "Gent";
            let query = 'select * from weather.forecast where woeid in (select woeid from geo.places(1) where text="' + place + '")';
            let xmlHttp = new XMLHttpRequest();
            arraymin = [];
            arrayplus = [];
            arraydagen = [];
            xmlHttp.onreadystatechange = function() {
                if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
                    Testwaarden = JSON.parse(this.responseText);
                    toonOverzicht();
                }
            }
            xmlHttp.open('GET', 'http://query.yahooapis.com/v1/public/yql?q=' + query + '&format=json', true);
            xmlHttp.send(null);

}

function toonOverzicht() {
    let voorspelling = "";

    voorspelling = Testwaarden.query.results.channel.item.forecast;

    for (let teller = 0; teller < voorspelling.length; teller++) {
        arraymin.push(voorspelling[teller].low);
        arrayplus.push(voorspelling[teller].high);
        arraydagen.push(voorspelling[teller].date);
    }

    convert2Celsius();
    drawChart();
}

function convert2Celsius() {
    for (let teller = 0; teller < arraymin.length; teller++) {
        arraymin[teller] = +((arraymin[teller] - 32) / 1.8).toFixed(1);
        arrayplus[teller] = +((arrayplus[teller] - 32) / 1.8).toFixed(1);
    }
}
