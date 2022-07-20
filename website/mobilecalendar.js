//Thanks to stack overflow for providing a reference on how to create a selectable calendar
//The skeleton for this page was found at this post on stack overflow
//https://stackoverflow.com/questions/57582127/highlighting-specific-days-in-jquery-datepicker


$(function() {
    //hard coded works
    /*
    var enableDays = ['2022-07-01', '2022-07-02', '2022-07-03', '2022-07-04', '2022-07-05', '2022-06-13', '2022-06-15', '2022-06-17', '2022-06-18',
    '2022-06-19', '2022-06-20', '2022-06-21', '2022-06-30'];
    */
    
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
    $("#dateinput2").datepicker({
      dateFormat: "yy-mm-dd",
      beforeShowDay: enableAllTheseDays,
    });
  });

function updateDates() {
  return JSON.parse(dates); //parse 
}
