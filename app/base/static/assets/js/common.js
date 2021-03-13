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

function apex_chart_options(id){
    var options = {
        series: [],
        annotations: {
            yaxis: [],
            xaxis: [],
        },
        chart: {
            id: id,
            type: 'area',
            animations: {
                enabled: false
            },
            zoom: {
                autoScaleYaxis: true
            }
        },
        markers: {
            size: 0,
            showNullDataPoints: false,
        },
        dataLabels: {
            enabled: false
        },
        xaxis: {
            type: 'datetime',
        },
        yaxis: {
            decimalsInFloat: 2,
            labels: {
                minWidth: "100%",
            },
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
    return options
}

function apex_chart_annotate(axis, value, label){
    var annotation = {
        borderColor: '#999',
        opacity: 0.3,
        forceNiceScale: true,
        label: {
            offsetX: -100,
            show: true,
            position: 'right',
            text: label,
            align: 'right',
            borderWidth: 0,
            borderRadius: 0,
            style: {
                color: "#fff",
                background: '#00E396'
            }
        }
    }
    annotation[axis] = value
    return annotation

}

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
        var change_html = '<span class="text-c-red">' + parseFloat(change).toFixed(2)
        + '% <i class="feather icon-trending-down ml-1"></i></span>'
    }
    $('#gtrend').find('#last').append(last)
    $('#gtrend').find('#change').append(change_html);


    var options = apex_chart_options('pytrend_chart');
    options.series.push({
        name: 'Value %',
        type: 'line',
        data: data['point']});
    options.yaxis.max=100;
    options.chart.group = 'stock';
    options.yaxis.min=0;
    options.annotations.yaxis.push(apex_chart_annotate('y', mean, 'Average'));

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
                    tr.append("<td class='f-12 " + cust_class + "'>" + formatNumber(data[i][key][value]/1000) + "</td>")
                    .fadeIn(2000);
                }
            }
            var last_key = key
        }
   }
};


function greater_than(num, to){
    var a = parseFloat(num);
    var b = parseFloat(to);
    return (a>b);
}

function compare_data(){
    $('[data-compare-id]').each(function() {
        var to = $(this).attr('data-compare-id');
        var compare = $(this).attr('data-compare-value');
        if(to && $('#'+to).length){
            console.log($(this).text(), $('#'+to).text());
            if(compare == 'greater'){
                if (greater_than($(this).text(), $('#'+to).text())){
                    var str = '<span class="text-c-green">' + $(this).text() + '</span>';
                }
                else {
                     var str = '<span class="text-c-red">' + $(this).text() + '</span>';
                }
            }
            else if (compare == 'lower'){
                 if (greater_than($(this).text(), $('#'+to).text())){
                    var str = '<span class="text-c-red">' + $(this).text() + '</span>';
                }
                else {
                     var str = '<span class="text-c-green">' + $(this).text() + '</span>';
                }
            }
           $(this).html(str);
        }
    });
}

function compare_to_format(num, to){
    /*console.log(to.replace(/\D+/g, ''))*/
    var a = parseFloat(num);
    var b = parseFloat(to);

    if (a > b){
        var str = '<span class="text-c-green">' + num + '</span>';
    }
    else {
        var str = '<span class="text-c-red">' + num + '</span>';
    }

    return str
}

function display_data(data, tag){
    for (var val in data){
        if($('#'+tag+'-'+val).length){
            var comp = $('#'+tag+'-'+val).attr('data-compare');
            if(comp && $('#'+comp.length)){
               var str = compare_to_format($('#'+comp).text(), data[val])
                $('#'+comp).html(str);
            }
            $('#'+tag+'-'+val).append(data[val]);
        }
    }
};

function formatNumber(num) {
  return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
}
