document.addEventListener('DOMContentLoaded', (event) => {

  document.getElementById("id_conc").addEventListener("change", function () {

    document.getElementById("id_amount").value = parseFloat(this.value) * parseFloat(document.getElementById("id_vol_init").value);

  });

  document.getElementById("id_vol_init").addEventListener("change", function () {

    document.getElementById("id_amount").value = parseFloat(this.value) * parseFloat(document.getElementById("id_conc").value);

    document.getElementById("id_vol_remain").value = this.value;

  });

  document.getElementById("id_vol_remain").addEventListener("change", function () {

    

  });

});
