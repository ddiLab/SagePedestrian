//Thanks to stack overflow for providing a reference on how to create a selectable calendar
//The skeleton for this page was found at this post on stack overflow
//https://stackoverflow.com/questions/57582127/highlighting-specific-days-in-jquery-datepicker


$(function() {    
    //this does not work
    var enableDays = updateDates();

    function enableAllTheseDays(date) {
      var fDate = $.datepicker.formatDate('yy-mm-dd', date);
      var result = [false, ""];
      $.each(enableDays, function(k, d) {
        if (fDate === d) {
          result = [true, "highlight-green"];
        }
      });
      
      return result;
    }
  
    //this section creates the datepicker and gives it the formatting we need, and makes only a select amount of days available
    $("#dateinput").datepicker({
      dateFormat: "yy-mm-dd",
      beforeShowDay: enableAllTheseDays,
    });
  
  });

function updateDates() {
  return JSON.parse(dates); //parse 
}
