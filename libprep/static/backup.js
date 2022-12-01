var handleSelectedRows = function (e) {

      var stepper = new KTStepper(document.getElementById("modal_stepper"));

      var modal = new bootstrap.Modal(document.getElementById("modal_samplelib_options"));

      function getSelectedRows() {

        const container = document.querySelector('.table');

        const selectedRows = container.querySelectorAll('[type="checkbox"]:checked');

        const selectedIds = [];

        selectedRows.forEach((p) => {
          // Select parent row
          const parent = p.closest('tr');
          // Get nucacid name
          const id = parent.querySelector('input[type=checkbox]').value;

          selectedIds.push(id)

        });

        return JSON.stringify(selectedIds);
      }

      function getCreationOptions() {

        var data = new FormData(document.getElementById('frm_creation_options'));
        var options = Object.fromEntries(data.entries());

        return JSON.stringify(options);
      }

      function checkSelectedRows() {
        // selected row's na type can not be together rna and dna
        const container = document.querySelector('.table');

        const selectedRows = container.querySelectorAll('[type="checkbox"]:checked');

        var arr = [];

        for (var i = 0; i < selectedRows.length; i++) {

          try {

            var naType = selectedRows[i].closest('tr').querySelectorAll('td')[3].innerText;

            arr.push(naType)

          } catch (e) {

            continue;

          }
        }

        var naTypeSet = new Set(arr);

        if (naTypeSet.size > 1) {

          return false;

        }

        return true;

      }

      function openModal() {

        if (checkSelectedRows()) {

          modal.show();

        }
        else {

          Swal.fire({
              text: "DNA and RNA type nucleic acids cannot be together in the selected rows.",
              icon: "error",
              buttonsStyling: false,
              confirmButtonText: "Ok, got it!",
              customClass: {
                  confirmButton: "btn fw-bold btn-primary",
              }
          });

        }

      }

      function closeModal() {

        modal.hide();

      }

      const txtPrefix = document.getElementById("id_prefix");

      txtPrefix.addEventListener("keyup", function () {

        this.value = this.value.toLocaleUpperCase();

      });

      const btnContinue = document.getElementById("btn_continue");

      // create nucacids
      btnContinue.addEventListener('click', function () {

        $.ajax({
          type: "GET",
          url: "/samplelib/new_async",
          data: {
            "selected_ids": getSelectedRows(),
            "options": getCreationOptions()
          },
        }).done(function(result) {
          if (result.success) {
            Swal.fire({
                text: "Sample Library(s) was created succesfully.",
                icon: "info",
                buttonsStyling: false,
                confirmButtonText: "Ok, got it!",
                customClass: {
                    confirmButton: "btn fw-bold btn-success",
                }
            }).then(function(){
              dt.draw();
            });
          }
          else {
            Swal.fire({
                text: "Sample Library(s) was not created.",
                icon: "error",
                buttonsStyling: false,
                confirmButtonText: "Ok, got it!",
                customClass: {
                    confirmButton: "btn fw-bold btn-danger",
                }
            });
          }

          closeModal();

        });

      });
    }
