$( document ).ready(function() {

  // The datetime field is initialized as flatpickr and formatted.
  $("#id_completion_date").flatpickr({
    altInput: true,
    altFormat: "m/d/Y",
    dateFormat: "Y-m-d H:i:s",
  });

});
