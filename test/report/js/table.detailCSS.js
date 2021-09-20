$(document).ready(function() {
    var $tables = $('#tables>*');

    $tables.each(function(i, table) {
        var $trs = $(table).children('tbody').children();

        // add title bar class
        $trs.first().children().addClass('detailTitleBar');

        // add data class
        $trs.slice(1, $trs.length - 1).each(function(i, tr) {
            var $tds = $(tr).children();
            $tds.slice(0, $tds.length - 2).addClass('detailData');
            $tds.slice(-2, -1).addClass('detailTotal');
            $tds.slice(-1).addClass('detailMisc');
        });

        // add total class
        var $tds = $trs.last().children();
        $tds.addClass('detailTotal');
        $tds.last().removeClass().addClass('detailMisc');
    })

    // add button to display more detail
    if($tables.length > 1) {
        $overview = $tables.first()
        $overview.after('<button style="margin-top: 30px">Show more details</button>');
        $overview.siblings('button').click(function(e) {
                e.srcElement.style.display = 'none';
                $tables.css('display', 'block');
            });
    }
});