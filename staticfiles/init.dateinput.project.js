$( document ).ready(function() {
  console.log("dattime init");
  $("#id_date_start").flatpickr({
    altInput: true,
    altFormat: "m/d/Y",
    dateFormat: "Y-m-d H:i:s",
  });
  $("#id_date_range").flatpickr({
    altInput: true,
    altFormat: "m/d/Y",
    dateFormat: "Y-m-d",
    mode: "range"
  });

});
