"use strict";

// Class definition
var KTDatatablesServerSide = function () {
    // Shared variables
    var table;
    var dt;
    var filterPayment;
    var editor;

    // Private functions
    var initDatatable = function ( initialValue ) {

        dt = $(".table").DataTable({
            // searchDelay: 500,
            processing: true,
            serverSide: true,
            order: [[1, 'desc']],
            stateSave: false,
            destroy: true,
            select: {
                style: 'multi',
                selector: 'td:first-child input[type="checkbox"]',
                className: 'row-selected'
            },
            keys: {
              columns: ':not(:first-child)',
              keys: [ 9 ],
              editor: editor,
              editOnFocus: true
            },
            ajax: '/sequencinglib/filter_sequencinglibs',
            columns: [
                { data: null },
                { data: 'name' },
                { data: 'date' },
                { data: 'nmol' },
                { data: 'buffer' },
            ],
            columnDefs: [
                {
                    targets: 0,
                    orderable: false,
                    render: function (data) {
                        return `
                            <div class="form-check form-check-sm form-check-custom form-check-solid">
                                <input class="form-check-input" type="checkbox" value="${data['id']}" />
                            </div>`;
                    }
                },
                {
                    targets: 5,
                    data: null,
                    orderable: false,
                    className: 'text-end',
                    render: function (data, type, row) {
                        return `
                            <a href="#" class="btn btn-light btn-active-light-primary btn-sm" data-kt-menu-trigger="click" data-kt-menu-placement="bottom-end" data-kt-menu-flip="top-end">
                                Actions
                                <span class="svg-icon svg-icon-5 m-0">
                                    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="24px" height="24px" viewBox="0 0 24 24" version="1.1">
                                        <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
                                            <polygon points="0 0 24 0 24 24 0 24"></polygon>
                                            <path d="M6.70710678,15.7071068 C6.31658249,16.0976311 5.68341751,16.0976311 5.29289322,15.7071068 C4.90236893,15.3165825 4.90236893,14.6834175 5.29289322,14.2928932 L11.2928932,8.29289322 C11.6714722,7.91431428 12.2810586,7.90106866 12.6757246,8.26284586 L18.6757246,13.7628459 C19.0828436,14.1360383 19.1103465,14.7686056 18.7371541,15.1757246 C18.3639617,15.5828436 17.7313944,15.6103465 17.3242754,15.2371541 L12.0300757,10.3841378 L6.70710678,15.7071068 Z" fill="currentColor" fill-rule="nonzero" transform="translate(12.000003, 11.999999) rotate(-180.000000) translate(-12.000003, -11.999999)"></path>
                                        </g>
                                    </svg>
                                </span>
                            </a>
                            <!--begin::Menu-->
                            <div class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-600 menu-state-bg-light-primary fw-bold fs-7 w-125px py-4" data-kt-menu="true">
                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/sequencinglib/edit/`+ row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        Edit
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-2">
                                    <a href="javascript:;" class="menu-link px-3 detail-link" data-kt-docs-table-filter="detail_row">
                                        Used Library(s)
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/sequencinglib/delete/` + row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="delete_row">
                                        Delete
                                    </a>
                                </div>
                                <!--end::Menu item-->
                            </div>
                            <!--end::Menu-->
                        `;
                    },
                },
            ],
            // Add data-filter attribute
            createdRow: function (row, data, dataIndex) {
                $(row).find('td:eq(4)').attr('data-filter', data.CreditCardType);
            },
            oSearch: {sSearch: "_initial:" + initialValue}
        });

        table = dt.$;

        // Re-init functions on every table re-draw -- more info: https://datatables.net/reference/event/draw
        dt.on('draw', function () {
            initToggleToolbar();
            toggleToolbars();
            handleDeleteRows();
            handleResetForm();
            initRowActions();
            handleSelectedRows();
            KTMenu.createInstances();
        });
    }

    // Search Datatable --- official docs reference: https://datatables.net/reference/api/search()
    var handleSearchDatatable = function () {
        const filterSearch = document.querySelector('[data-kt-docs-table-filter="search"]');
        filterSearch.addEventListener('keyup', function (e) {
            dt.search(e.target.value).draw();
        });
    }

    // Filter Datatable
    var handleFilterDatatable = () => {
        // Select filter options
        filterPayment = document.querySelectorAll('[data-kt-docs-table-filter="payment_type"] [name="payment_type"]');
        const filterButton = document.querySelector('[data-kt-docs-table-filter="filter"]');

        // Filter datatable on submit
        filterButton.addEventListener('click', function () {
            // Get filter values
            let paymentValue = '';

            // Get payment value
            filterPayment.forEach(r => {
                if (r.checked) {
                    paymentValue = r.value;
                }

                // Reset payment value if "All" is selected
                if (paymentValue === 'all') {
                    paymentValue = '';
                }
            });

            // Filter datatable --- official docs reference: https://datatables.net/reference/api/search()
            dt.search(paymentValue).draw();
        });
    }

    // Delete customer
    var handleDeleteRows = () => {
        // Select all delete buttons
        const deleteButtons = document.querySelectorAll('[data-kt-docs-table-filter="delete_row"]');

        deleteButtons.forEach(d => {
            // Delete button on click
            d.addEventListener('click', function (e) {
                e.preventDefault();

                // Select parent row
                const parent = e.target.closest('tr');

                // Get customer name
                const customerName = parent.querySelectorAll('td')[1].innerText;

                // SweetAlert2 pop up --- official docs reference: https://sweetalert2.github.io/
                Swal.fire({
                    text: "Are you sure you want to delete " + customerName + "?",
                    icon: "warning",
                    showCancelButton: true,
                    buttonsStyling: false,
                    confirmButtonText: "Yes, delete!",
                    cancelButtonText: "No, cancel",
                    customClass: {
                        confirmButton: "btn fw-bold btn-danger",
                        cancelButton: "btn fw-bold btn-active-light-primary"
                    }
                }).then(function (result) {
                    if (result.value) {
                        // Simulate delete request -- for demo purpose only
                        Swal.fire({
                            text: "Deleting " + customerName,
                            icon: "info",
                            buttonsStyling: false,
                            showConfirmButton: false,
                            timer: 2000
                        }).then(function () {
                            // Calling delete request with ajax
                            $.ajax({
                                url: parent.querySelector('[data-kt-docs-table-filter="delete_row"]').href,
                                type: "DELETE",
                                headers: {'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value },
                                success: function () {
                                  Swal.fire({
                                        text: "Sample Library(s) was deleted succesfully.",
                                        icon: "info",
                                        buttonsStyling: false,
                                        confirmButtonText: "Ok, got it!",
                                        customClass: {
                                            confirmButton: "btn fw-bold btn-success",
                                        }
                                    }).then(function(){
                                      dt.draw();
                                    });
                                },
                                error: function (xhr, ajaxOptions, thrownError) {
                                  Swal.fire({
                                      text: customerName + " was not deleted.",
                                      icon: "error",
                                      buttonsStyling: false,
                                      confirmButtonText: "Ok, got it!",
                                      customClass: {
                                          confirmButton: "btn fw-bold btn-primary",
                                      }
                                  });
                                }
                            });
                        });
                    } else if (result.dismiss === 'cancel') {
                        Swal.fire({
                            text: customerName + " was not deleted.",
                            icon: "error",
                            buttonsStyling: false,
                            confirmButtonText: "Ok, got it!",
                            customClass: {
                                confirmButton: "btn fw-bold btn-primary",
                            }
                        });
                    }
                });
            })
        });
    }

    // Reset Filter
    var handleResetForm = () => {
        // Select reset button
        const resetButton = document.querySelector('[data-kt-docs-table-filter="reset"]');

        // Reset datatable
        resetButton.addEventListener('click', function () {
            // Reset payment type
            filterPayment[0].checked = true;

            // Reset datatable --- official docs reference: https://datatables.net/reference/api/search()
            dt.search('').draw();
        });
    }

    // Init toggle toolbar
    var initToggleToolbar = function () {
        // Toggle selected action toolbar
        // Select all checkboxes
        const container = document.querySelector('.table');
        const checkboxes = container.querySelectorAll('[type="checkbox"]');

        // Select elements
        const deleteSelected = document.querySelector('[data-kt-docs-table-select="delete_selected"]');

        // Toggle delete selected toolbar
        checkboxes.forEach(c => {
            // Checkbox on click event
            c.addEventListener('click', function () {
                setTimeout(function () {
                    toggleToolbars();
                }, 50);
            });
        });

        // Deleted selected rows
        deleteSelected.addEventListener('click', function () {
            // SweetAlert2 pop up --- official docs reference: https://sweetalert2.github.io/
            Swal.fire({
                text: "Are you sure you want to delete selected records?",
                icon: "warning",
                showCancelButton: true,
                buttonsStyling: false,
                showLoaderOnConfirm: true,
                confirmButtonText: "Yes, delete!",
                cancelButtonText: "No, cancel",
                customClass: {
                    confirmButton: "btn fw-bold btn-danger",
                    cancelButton: "btn fw-bold btn-active-light-primary"
                },
            }).then(function (result) {
                if (result.value) {
                    // Simulate delete request -- for demo purpose only
                    Swal.fire({
                        text: "Deleting selected customers",
                        icon: "info",
                        buttonsStyling: false,
                        showConfirmButton: false,
                        timer: 2000
                    }).then(function () {

                      function getSelectedRows() {

                        const container = document.querySelector('.table');

                        const selectedRows = container.querySelectorAll('[type="checkbox"]:checked');

                        const selectedIds = [];

                        selectedRows.forEach((p) => {
                          // Select parent row
                          const parent = p.closest('tr');
                          // Get customer name
                          const id = parent.querySelector('input[type=checkbox]').value;

                          selectedIds.push(id)

                        });

                        return JSON.stringify(selectedIds);
                      }

                        // Calling delete request with ajax
                        $.ajax({
                            type: "GET",
                            url: "/sequencinglib/batch_delete",
                            data: {
                              "selected_ids": getSelectedRows(),
                            },
                            done: function (result) {
                                if (result.success) {
                                  Swal.fire({
                                      text: "Nucleic Acid(s) was deleted succesfully.",
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
                                      text: "Nucleic Acid(s) wasn't deleted!",
                                      icon: "error",
                                      buttonsStyling: false,
                                      confirmButtonText: "Ok, got it!",
                                      customClass: {
                                          confirmButton: "btn fw-bold btn-success",
                                      }
                                  });
                                }
                            },
                            error: function (xhr, ajaxOptions, thrownError) {
                                swal("Error deleting!", "Please try again", "error");
                            }
                        });

                        Swal.fire({
                            text: "You have deleted all selected customers!.",
                            icon: "success",
                            buttonsStyling: false,
                            confirmButtonText: "Ok, got it!",
                            customClass: {
                                confirmButton: "btn fw-bold btn-primary",
                            }
                        }).then(function () {
                            // delete row data from server and re-draw datatable
                            dt.draw();
                        });

                        // Remove header checked box
                        const headerCheckbox = container.querySelectorAll('[type="checkbox"]')[0];
                        headerCheckbox.checked = false;
                    });
                } else if (result.dismiss === 'cancel') {
                    Swal.fire({
                        text: "Selected customers was not deleted.",
                        icon: "error",
                        buttonsStyling: false,
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                            confirmButton: "btn fw-bold btn-primary",
                        }
                    });
                }
            });
        });
    }

    // Toggle toolbars
    var toggleToolbars = function () {
        // Define variables
        const container = document.querySelector('.table');
        const toolbarBase = document.querySelector('[data-kt-docs-table-toolbar="base"]');
        const toolbarSelected = document.querySelector('[data-kt-docs-table-toolbar="selected"]');
        const selectedCount = document.querySelector('[data-kt-docs-table-select="selected_count"]');

        // Select refreshed checkbox DOM elements
        const allCheckboxes = container.querySelectorAll('tbody [type="checkbox"]');

        // Detect checkboxes state & count
        let checkedState = false;
        let count = 0;

        // Count checked boxes
        allCheckboxes.forEach(c => {
            if (c.checked) {
                checkedState = true;
                count++;
            }
        });

        // Toggle toolbars
        if (checkedState) {
            selectedCount.innerHTML = count;
            toolbarBase.classList.add('d-none');
            toolbarSelected.classList.remove('d-none');
        } else {
            toolbarBase.classList.remove('d-none');
            toolbarSelected.classList.add('d-none');
        }
    }

    var initEditor = function () {

      editor = new $.fn.dataTable.Editor({
        ajax: {
          url: "/samplelib/edit_samplelib_async",
          type: "POST",
          headers: {'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value },
          success: function () {
              dt.draw();
          },
          error: function (xhr, ajaxOptions, thrownError) {
              swal("Error updating!", "Please try again!", "error");
          }
        },
        table: ".table",
        fields: [ {
               label: "Name:",
               name: "name"
           }, {
               label: "Barcode:",
               name: "barcode"
           }, {
               label: "Date:",
               name: "date",
               type: "datetime"
           }, {
               label: "Method:",
               name: "method",
           }, {
               label: "Concentration:",
               name: "conc"
           }, {
               label: "Input Amount:",
               name: "input_amount",
               type: "readonly"
           }, {
               label: "Volume Init:",
               name: "vol_init"
           }, {
               label: "Volume Remain:",
               name: "vol_remain"
           },
       ],
       formOptions: {
          inline: {
            onBlur: 'submit'
          }
       }
     });


     $('.table').on( 'click', 'tbody td:not(:first-child)', function (e) {
          editor.inline( this );
     });

     $('.table').on( 'key-focus', function ( e, datatable, cell ) {
          editor.inline( cell.index() );
     });

    }

    // Redirects from other pages
    var handleInitialValue = () => {

      // Remove parameters in URL
      function cleanUrl() {
        window.history.replaceState(null, null, window.location.pathname);
      }

      const params = new URLSearchParams(window.location.search);
      const x = params.get('initial');

      cleanUrl();

      return x;

    }

    var handleSelectedRows = (e) => {

      document.getElementById("modal_capturedlib_options").addEventListener('show.bs.modal', function(e){

        if (!checkSelectedRows()) {

          Swal.fire({
              text: "Identical barcodes are used in selected rows.",
              icon: "error",
              buttonsStyling: false,
              confirmButtonText: "Ok, got it!",
              customClass: {
                  confirmButton: "btn fw-bold btn-primary",
              }
          });

          return e.preventDefault();
        }

      });

      function getSelectedRows() {

        const container = document.querySelector('.table');

        const selectedRows = container.querySelectorAll('[type="checkbox"]:checked');

        const selectedIds = [];

        selectedRows.forEach((p) => {
          // Select parent row
          const parent = p.closest('tr');
          // Get customer name
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
        // selected row's na type must be DNA
        var container = document.querySelector('.table');

        var selectedRows = container.querySelectorAll('[type="checkbox"]:checked');

        var barcodeList = [];

        for (var i = 0; i < selectedRows.length; i++) {

          const parent = selectedRows[i].closest('tr');
          // Get barcode
          const barcode = parent.querySelectorAll('td')[2].innerText;

          if (barcodeList.indexOf(barcode) > -1 ) {

            return false;

          }

          barcodeList.push(barcode);
        }

        return true;

      }

    }

    var initRowActions = () => {

      const el = document.getElementById("modal_used_capturedlibs");
      const modal = new bootstrap.Modal(el);

      var data = {};

      initModal();

      function initModal() {

        el.addEventListener('hide.bs.modal', function(){

          var listEl = document.querySelector(".list-body");

          listEl.innerHTML = "";

          data = {};

        });

        var detailLinks = document.querySelectorAll(".detail-link");

        for (var detail of detailLinks) {

          detail.addEventListener("click", function (e) {
            e.preventDefault();
            // Select parent row
            const parent = this.closest('tr');
            // Get customer name
            const id = parent.querySelector('input[type=checkbox]').value;

            $.ajax({
                url: "/sequencinglib/" + id + "/used_capturedlibs",
                type: "GET",
                success: function (retval) {

                  data = retval;

                  fillElements(id);

                  updateTotalPercentage();
                  updateTotalVolume();
                  updateBufferAmount();
                  updateVolumeRemain();

                  initEvents();

                  modal.show();

                },
                error: function (xhr, ajaxOptions, thrownError) {

                }
            });

          });

        }

      }

      function fillElements(id) {

        var listEl = document.querySelector(".list-body");

        listEl.setAttribute('data-sequencing_lib_id', id);
        listEl.setAttribute('data-nmol', data[0].nmol);

        var total_persentage = 1;
        var totalVolume = 0;

        for (var i = 0; i < data.length; i++) {

          totalVolume += data[i].volume;

        }

        for (var i = 0; i < data.length; i++) {
          var p = 0.00;
          var v = 0.00;
          //
          // if (totalVolume > 0) {
          //
          //   p = data[i].volume / totalVolume;
          //
          // }
          // else {
          //
          //   p = 1/data.length;
          //
          // }
          //
          // v = p * data[i].nmol  / data[i].nm;
          v = data[i].volume;
          p = data[i].volume / totalVolume;

          var row = `<div class="row mb-1 detail-row">
              <div class="col-2 align-self-center" data-id="${ data[i].captured_lib }">${ data[i].name }</div>
              <div class="col-2 align-self-center">${ data[i].frag_size }</div>
              <div class="col-2 align-self-center text-center">${ data[i].vol_remain }</div>
              <div class="col-1 align-self-center text-center">${ data[i].conc }</div>
              <div class="col-1 align-self-center text-center">${ data[i].nm }</div>
              <div class="col-2 text-center"><input type="text" class="textinput textInput form-control form-control-sm text-end detail-percentage" value="${ p.toFixed(2) }"></div>
              <div class="col-2 text-center"><input type="text" class="textinput textInput form-control form-control-sm text-end detail-volume" value="${ v.toFixed(2) }"></div>
            </div>`;
          listEl.innerHTML += row;

        }

        // var note = '<div><textarea name="notes" cols="40" rows="2" class="textarea form-control" id="id_notes"></textarea></div>';
        //
        // listEl.innerHTML += note;

        var footer = `<div class="mt-5">
              <button type="button" class="btn btn-lg btn-success" id="btn_save">Make Sequencing Library</button>
            </div>`;

        listEl.innerHTML += footer;

      }

      function getValues() {

        var rows = document.querySelector(".list-body").querySelectorAll(".row");

        var values = [];

        for (var row of rows) {

          var id = row.querySelectorAll('div')[0].getAttribute("data-id");
          var volume = row.querySelector(".detail-volume").value;

          values.push({
            "id":id,
            "volume":volume
          });
        }

        return JSON.stringify(values);

      }

      function updateTotalPercentage() {

        var total = 0;

        for (var detail of document.querySelectorAll(".detail-percentage")) {

          total += parseFloat(detail.value);

        }

        document.querySelector("#total_percentage").value = total.toFixed(2);

      }

      function updateTotalVolume() {

        var total = 0;

        for (var detail of document.querySelectorAll(".detail-volume")) {

          total += parseFloat(detail.value);

        }

        document.querySelector("#total_volume").value = total.toFixed(2);

      }

      function updateBufferAmount() {

        var totalVolume = document.querySelector("#total_volume").value;

        var targetMol = document.querySelector(".list-body").getAttribute("data-nmol");

        var targetVol = 0;

        var bufferAmount = (targetVol - totalVolume).toFixed(2);

        document.querySelector("#buffer_amount").value = bufferAmount;

      }

      function updateVolumeRemain(){

        document.querySelectorAll(".detail-row").forEach((row, i) => {

          var volume = parseFloat(row.querySelector(".detail-volume").value);

          row.querySelectorAll('div')[2].innerText = (data[i].vol_remain - volume).toFixed(2);

        });

      }

      function initEvents() {

        for (var persentage of document.querySelectorAll(".detail-percentage")) {

          persentage.addEventListener("change", function () {

            var row = this.closest('.row');

            var nm = row.querySelectorAll('div')[4].innerText;

            var nmol = document.querySelector(".list-body").getAttribute("data-nmol");

            var volume = this.value * nmol  / nm;

            row.querySelector(".detail-volume").value = volume.toFixed(2);

            updateTotalPercentage();
            updateTotalVolume();
            updateBufferAmount();
            updateVolumeRemain();

          });

        }

        function checkTotalPercentage() {

          return parseFloat(document.getElementById("total_percentage").value) == 1;

        }

        document.getElementById("btn_save").addEventListener('click', function () {

          if ( !checkTotalPercentage() ) {
            Swal.fire({
                text: "The total percent should be 100.",
                icon: "error",
                buttonsStyling: false,
                confirmButtonText: "Ok, got it!",
                customClass: {
                    confirmButton: "btn fw-bold btn-danger",
                }
            });

            return e.preventDefault();

          }

          var id = document.querySelector(".list-body").getAttribute("data-sequencing_lib_id");

          $.ajax({
            type: "GET",
            url: "/sequencinglib/"+ id +"/make_sequencinglib_async",
            data: {
              "values": getValues(),
            },
          }).done(function(result) {
            if (result.success) {
              Swal.fire({
                  text: "Captured Library(s) was updated succesfully.",
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
                  text: "Captured Library(s) was not updated.",
                  icon: "error",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                      confirmButton: "btn fw-bold btn-danger",
                  }
              });
            }

            modal.hide();

          });

        });

      }

    }

    // Public methods
    return {
        init: function () {
            initDatatable( handleInitialValue() );
            handleSearchDatatable();
            initToggleToolbar();
            handleFilterDatatable();
            handleDeleteRows();
            handleResetForm();
            initEditor();
        }
    }
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesServerSide.init();
});
