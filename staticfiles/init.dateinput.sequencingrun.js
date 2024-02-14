$( document ).ready(function() {

  $("#id_date").flatpickr({
    altInput: true,
    altFormat: "m/d/Y",
    dateFormat: "Y-m-d H:s:i",
  });

  $("#id_date_run").flatpickr({
    altInput: true,
    altFormat: "m/d/Y",
    dateFormat: "Y-m-d H:s:i",
  });

});
