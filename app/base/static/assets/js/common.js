'use strict';
$(document).ready(function () {
    /*$(function() {
        var availableTutorials  =  [
           "ActionScript",
           "Bootstrap",
           "C",
           "C++",
        ];
        $( "#search" ).autocomplete({
           source: '/autocomplete'
        });
    });*/


    $("#search").keyup(function(event) {
      if (event.which === 13) {
        $('search_form').submit();
        return false;
      }
    });
});
function show_pytrend(data, id){
    var last = data['last'];
    var previous = data['previous'];
    var mean = data['mean']
    var change = (last - previous) / previous;

    if (change > 0){
        var change_html = '<span class="text-c-green">+' + parseFloat(change).toFixed(2)
        + '% <i class="feather icon-trending-up ml-1"></i></span>'
    }
    else {
        var change_html = '<span class="text-c-red">-' + parseFloat(change).toFixed(2)
        + '% <i class="feather icon-trending-down ml-1"></i></span>'
    }
    $('#gtrend').find('#last').append(last)
    $('#gtrend').find('#change').append(change_html);


    var options = {
        series: [{
          name: 'Value %',
          type: 'area',
          data: data['point']
        }],
        annotations: {
            yaxis: [{
                y: mean,
                borderColor: '#999',
                forceNiceScale: true,
                label: {
                    show: true,
                    text: 'Average',
                    align: 'right',
                    position: 'right',
                    offsetX: -5,
                    borderWidth: 0,
                    borderRadius: 0,
                    style: {
                        color: "#fff",
                        background: '#00E396'
                    }
                }
            }]
        },
        chart: {
            id: 'pytrend-chart',
            type: 'area',
            zoom: {
                autoScaleYaxis: true
            }
        },
        dataLabels: {
            enabled: false
        },
        markers: {
            size: 0,
            style: 'hollow',
        },
        xaxis: {
            type: 'datetime',
            min: new Date().setMonth(new Date().getMonth() - 12),
            tickAmount: 6,
        },
        yaxis: {
            decimalsInFloat: 2,
            max: 100,
            min: 0,
            tickAmount: 5,
        },
        tooltip: {
              x: {
                    format: 'dd MMM yyyy'
              }
        },
        fill: {
              type: 'gradient',
              gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.7,
                    opacityTo: 0.9,
                    stops: [0, 100]
              }
        },
    };
    var pytrend_chart = new ApexCharts(document.querySelector("#pytrend-chart"), options);
    pytrend_chart.render();
};
function show_financial(data, table_id){
   for (var i = 0; i < data.length; i++) {
        for (var key in data[i]){
            var tr_head =  $('#'+table_id).find('thead').find('tr')
            tr_head.append("<th>"+ key + "</th>").fadeIn(2000);
            for (var value in data[i][key]){
                var tr = $('#'+table_id).find('#'+value)
                if (tr.length > 0) {
                    var cust_class = '';

                    if (data[i][key][value] < 0){ cust_class = 'text-c-red' }
                    tr.append("<td class=" + cust_class + ">" + formatNumber(data[i][key][value]/1000) + "</td>")
                    .fadeIn(2000);
                }
            }
            var last_key = key
        }
   }
};
function formatNumber(num) {
  return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
}
