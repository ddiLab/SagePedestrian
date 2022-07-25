var slider = 

$(document).ready(function() {
    $("#slider").slider({
        min: 13,
        max: 22,
        step: 1,
        values: [13, 22],//the widgets
        slide: function(event, ui) {
            if ( ui.values[0] > ui.values[1] ) {
                return false;
            } else {
                for (var i = 0; i < ui.values.length; ++i) {
                    $("input.sliderValue[data-index=" + i + "]").val(ui.values[i]);          
                }
            }
        }
    });
    
    $("input.sliderValue").change(function() {
        var $this = $(this);
        $("#slider").slider("values", $this.data("index"), $this.val());
    });
});