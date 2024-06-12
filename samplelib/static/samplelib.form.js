document.addEventListener('DOMContentLoaded', (event) => {
  // Calculates the amount when the qpcr_conc is changed.
  document.getElementById("id_qpcr_conc").addEventListener("change", function () {

    document.getElementById("id_amount_in").value = parseFloat(this.value) * parseFloat(document.getElementById("id_vol_init").value);

  });

  // Calculates the amount and the remian volume when the initial volume is changed.
  document.getElementById("id_vol_init").addEventListener("change", function () {

    document.getElementById("id_amount_in").value = parseFloat(this.value) * parseFloat(document.getElementById("id_qpcr_conc").value);

  });

});
