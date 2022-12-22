$( document ).ready(function() {

  $("#id_date").flatpickr({
    altInput: true,
    altFormat: "m/d/Y",
    dateFormat: "Y-m-d",
  });

  $("#id_date_range").flatpickr({
    altInput: true,
    altFormat: "m/d/Y",
    dateFormat: "Y-m-d",
    mode: "range"
  });

});
