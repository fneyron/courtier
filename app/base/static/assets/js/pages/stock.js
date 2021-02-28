'use strict';
$(document).ready(function() {
    // [ stock-scroll ] start
    var px = new PerfectScrollbar('.income-scroll', {
        wheelSpeed: .5,
        swipeEasing: 0,
        wheelPropagation: 1,
        minScrollbarLength: 40,
    });
    var px = new PerfectScrollbar('.balance-scroll', {
        wheelSpeed: .5,
        swipeEasing: 0,
        wheelPropagation: 1,
        minScrollbarLength: 40,
    });
    var px = new PerfectScrollbar('.cashflow-scroll', {
        wheelSpeed: .5,
        swipeEasing: 0,
        wheelPropagation: 1,
        minScrollbarLength: 40,
    });
    // [ stock-scroll ] end

});
function show_financial(data, table_id){
   for (var i = 0; i < data.length; i++) {
        for (var key in data[i]){
            var tr_head =  $('#'+table_id).find('thead').find('tr')
            tr_head.append("<th>"+ key + "</th>")
            for (var value in data[i][key]){
                var tr = $('#'+table_id).find('#'+value)
                console.log(value, tr.length)
                if (tr.length > 0) {
                    tr.append("<td>" + data[i][key][value] + "</td>")
                }
            }
        }
   }
};
