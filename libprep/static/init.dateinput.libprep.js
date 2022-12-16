$( document ).ready(function() {

  $("#id_date").flatpickr({
    dateFormat: "m/d/Y",
  });

  $("#id_date_range").flatpickr({
    dateFormat: "m/d/Y",
    mode: "range"
  });

});
