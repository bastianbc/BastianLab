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
            ajax: '/capturedlib/filter_capturedlibs',
            columns: [
                { data: null },
                { data: 'name' },
                { data: 'barcode' },
                { data: 'date' },
                { data: 'bait' },
                { data: 'frag_size' },
                { data: 'conc' },
                { data: 'amp_cycle' },
                { data: 'buffer' },
                { data: 'nm' },
                { data: 'vol_init' },
                { data: 'vol_remain' },
                { data: 'amount' },
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
                    targets: 12,
                    orderable: false,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let id = row["id"];
                          return `
                              <a href="javascript:;" class="detail-link">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 13,
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
                                    <a href="/capturedlib/edit/`+ row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
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
                                    <a href="/capturedlib/delete/` + row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="delete_row">
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
            handleSelectedRows.init();
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
                        text: "Deleting selected records",
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
                            url: "/capturedlib/batch_delete",
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
          url: "/capturedlib/edit_capturedlib_async",
          type: "POST",
          headers: {'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value },
          success: function (result) {
              if (!result.success) {
                Swal.fire({
                    text: "Error occurred during data update.",
                    icon: "error",
                    buttonsStyling: false,
                    confirmButtonText: "Ok, got it!",
                    customClass: {
                        confirmButton: "btn fw-bold btn-primary",
                    }
                });
              }

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
               label: "Date:",
               name: "date",
               type: "datetime"
           }, {
               label: "Bait:",
               name: "bait",
               type: "select",
               options : [
                 {"label": "Type 1", "value": "type1"},
                 {"label": "Type 2", "value": "type2"},
                 {"label": "Type 3", "value": "type3"}
               ]
           },{
               label: "Fragment Size:",
               name: "frag_size"
           },{
               label: "Concentration:",
               name: "conc"
           }, {
               label: "AMP Cycle:",
               name: "amp_cycle"
           },{
               label: "Buffer:",
               name: "buffer"
           },{
               label: "Volume Init:",
               name: "vol_init"
           }, {
               label: "Volume Remain:",
               name: "vol_remain"
           },
           {
               label: "Amount:",
               name: "amount",
               type: "readonly"
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

    var initRowActions = () => {

      const el = document.getElementById("modal_used_samplelibs");
      const modal = new bootstrap.Modal(el);

      initModal();

      function initModal() {

        el.addEventListener('hide.bs.modal', function(){

          var listEl = document.querySelector(".list-body");

          listEl.innerHTML = "";

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
                url: "/capturedlib/" + id + "/used_samplelibs",
                type: "GET",
                success: function (data) {

                  fillElements(id,data);

                  updateTotalAmount();
                  updateTotalVolume();

                  initEvents();

                  modal.show();

                },
                error: function (xhr, ajaxOptions, thrownError) {

                }
            });

          });

        }

      }

      function fillElements(id,data) {

        var listEl = document.querySelector(".list-body");

        listEl.setAttribute('data-captured_lib_id', id);

        var total_amount = 0;
        var total_volume = 0;

        for (var i = 0; i < data.length; i++) {

          var row = `<div class="row mb-1">
              <div class="col-2 align-self-center" data-id="${ data[i].id }">${ data[i].name }</div>
              <div class="col-2 align-self-center">${ data[i].conc }</div>
              <div class="col-2 align-self-center text-center">${ data[i].vol_remain }</div>
              <div class="col-2 align-self-center text-center">${ data[i].barcode }</div>
              <div class="col-2 text-center"><input type="text" class="textinput textInput form-control form-control-sm text-end detail-amount" value="${ data[i].amount }"></div>
              <div class="col-2 text-center"><input type="text" class="textinput textInput form-control form-control-sm text-end detail-volume" value="${ data[i].volume }"></div>
            </div>`;
          listEl.innerHTML += row;

        }

        var footer = `<div class="mt-5">
              <button type="button" class="btn btn-lg btn-success" id="btn_save">Save</button>
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

      function updateTotalAmount() {

        var total = 0;

        for (var detail of document.querySelectorAll(".detail-amount")) {

          total += parseFloat(detail.value);

        }

        document.querySelector("#total_amount").value = total;

      }

      function updateTotalVolume() {

        var total = 0;

        for (var detail of document.querySelectorAll(".detail-volume")) {

          total += parseFloat(detail.value);

        }

        document.querySelector("#total_volume").value = total;

      }

      function initEvents() {

        for (var amount of document.querySelectorAll(".detail-amount")) {

          amount.addEventListener("change", function () {

            var parent = this.closest('.row');

            var conc = parent.querySelectorAll('div')[1].innerText;

            var volume = this.value / conc;

            parent.querySelector(".detail-volume").value = volume;

            updateTotalAmount();
            updateTotalVolume();

          });

        }

        var id = document.querySelector(".list-body").getAttribute("data-captured_lib_id");

        document.getElementById("btn_save").addEventListener('click', function () {

          $.ajax({
            type: "GET",
            url: "/capturedlib/"+ id +"/update_async",
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

    var handleSelectedRows = ((e) => {

      var stepper = new KTStepper(document.getElementById("modal_stepper"));

      var modal = new bootstrap.Modal(document.getElementById("modal_sequencinglib_options"));

      function initModal() {
        var isInit = false;

        function resetStepper() {

          stepper.goFirst();

        }

        function resetForm() {

          document.getElementById("frm_creation_options").reset();

        }

        document.getElementById("modal_sequencinglib_options").addEventListener('show.bs.modal', function(e){

          if (!checkSelectedRows()) {

            Swal.fire({
                text: "Identical barcodes are used in selected rows.",
                icon: "error",
                buttonsStyling: false,
                confirmButtonText: "Ok, got it!",
                customClass: {
                    confirmButton: "btn fw-bold btn-primary",
                }
            }).then(function () {

              modal.hide();

            });

          }
          else {

            initStepper();

            if (!isInit) {

              isInit = true;

              initEvents();
            }

          }

        });

        document.getElementById("modal_sequencinglib_options").addEventListener('hide.bs.modal', function(e){

          resetForm();

          resetStepper();

        });

      }

      function initEvents() {

        function handleSpinner(state) {

          if (state) {

            document.querySelector('[data-kt-stepper-action="next"]').setAttribute("data-kt-indicator", "on");

          }
          else {

            document.querySelector('[data-kt-stepper-action="next"]').removeAttribute("data-kt-indicator");

          }

        }

        function handleData(data) {

          document.getElementById("id_prefix").value = data.name;
          document.getElementById("id_date").value = data.date;
          document.getElementById("id_buffer").value = data.buffer;

        }

        function handleFormAction(state) {

          var frm = document.getElementById('frm_creation_options');
          var url = "";

          if (state) {

            url = "/sequencinglib/recreate_sequencinglib_async";

          }
          else {

            url = "/sequencinglib/new_async";

          }

          frm.setAttribute("action",url);

        }

        function getFormAction() {

          return document.getElementById('frm_creation_options').getAttribute("action")

        }

        document.getElementById("id_prefix").addEventListener("keyup", function () {

          this.value = this.value.toLocaleUpperCase();

        });

        document.getElementById("id_sequencing_lib").addEventListener("change", function () {

          $.ajax({
            type: "GET",
            url: "/sequencinglib/get_sequencinglib_async/" + this.value,
            beforeSend: function () {

              handleSpinner(true);

            }
          }).done(function(data) {
            if (data) {

              handleSpinner(false);

              handleData(data);

              handleFormAction(true);

            }
            else {
              Swal.fire({
                  text: "Sequencing Library(s) was not created.",
                  icon: "error",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                      confirmButton: "btn fw-bold btn-danger",
                  }
              });
            }

          });

        });

        document.querySelector('[data-kt-stepper-action="submit"]').addEventListener('click', function () {

          $.ajax({
            type: "GET",
            url: getFormAction(),
            data: {
              "selected_ids": getSelectedRows(),
              "options": getCreationOptions()
            },
          }).done(function(result) {
            if (result.success) {
              Swal.fire({
                  text: "Sequencing Library(s) was created succesfully.",
                  icon: "info",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                      confirmButton: "btn fw-bold btn-success",
                  }
              }).then(function(){

                modal.hide();

                dt.draw();
              });
            }
            else {
              Swal.fire({
                  text: "Sequencing Library(s) was not created.",
                  icon: "error",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                      confirmButton: "btn fw-bold btn-danger",
                  }
              });
            }

          });

        });

      }

      function initStepper() {

        if (Object.keys(stepper).length !== 0) { //isEmpty

          stepper.on("kt.stepper.next", function (stepper) {
              stepper.goNext(); // go next step
          });

          stepper.on("kt.stepper.previous", function (stepper) {
              stepper.goPrevious(); // go previous step
          });

        }

      }

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

      return {
        init: function () {
          initModal();
        }
      }

    })();

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