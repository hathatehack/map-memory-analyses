$(document).ready(function() {
    var $trs = $('tr');

    // add title bar class
    var $tds = $trs.first().children('td')
    $tds.addClass('summaryTitleBar');
    $tds.last().removeClass().addClass('summaryTotal');

    // add data class and column title/total class
    $trs.slice(1, $trs.length - 1).each(function(index, tr) {
        $tds = $(tr).children('td');
        $tds.addClass('summaryData');
        $tds.first().removeClass().addClass('summaryTitleColumn');
        $tds.last().removeClass().addClass('summaryTotal');
    });

    // add row total class
    $tds = $trs.last().children('td');
    $tds.addClass('summaryTotal');
});