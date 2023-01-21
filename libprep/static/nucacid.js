"use strict";

// Class definition
var KTDatatablesServerSide = function () {
    // Shared variables
    var table;
    var dt;
    var filterPayment;
    var editor;

    /*
   * Initializes the datatable.
   * @param  {String} initialValue  If it comes from another page, it is initialized with this value.
   * @param  {String} filterDateRange   A parameter of custom filter.
   * @param  {String} filterNAType A parameter of custom filter.
   */
    var initDatatable = function ( initialValue, filterDateRange, filterNAType ) {

        $.fn.dataTable.moment( 'MM/DD/YYYY' );

        dt = $(".table").DataTable({
            // searchDelay: 500,
            processing: true,
            serverSide: true,
            order: [[0, 'desc']],
            stateSave: false,
            destroy: true,
            pageLength: 100,
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
            ajax: {
              url: '/libprep/filter_nucacids',
              type: "GET",
              data:{
                "date_range": filterDateRange,
                "na_type": filterNAType,
              },
              error: function (xhr, ajaxOptions, thrownError) {
                  if (xhr.status == 403) {

                    Swal.fire({
                        text: "You do not have permission to view.",
                        icon: "error",
                        buttonsStyling: false,
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                            confirmButton: "btn fw-bold btn-primary",
                        }
                    });

                  }
              }
            },
            columns: [
                { data: 'nu_id' },
                { data: 'name' },
                { data: 'area' },
                { data: 'na_type',
                  render: function (val, type, row) {
                    return row["na_type_label"];
                  }
                },
                { data: 'date',
                  render: function (data) {
                    return moment(data).format('MM/DD/YYYY');
                  }
                },
                { data: 'method',
                  render: function (val, type, row) {
                    return row["method_label"];
                  }
                },
                { data: 'conc' },
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
                                <input class="form-check-input" type="checkbox" value="${data}" />
                            </div>`;
                    }
                },
                // {
                //     targets: 4,
                //     render: function (data, type, row) {
                //         return `<img src="${hostUrl}media/svg/card-logos/${row.CreditCardType}.svg" class="w-35px me-3" alt="${row.CreditCardType}">` + data;
                //     }
                // },
                {
                    targets: 9,
                    orderable: false
                },
                {
                    targets: 10,
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
                                    <a href="/libprep/edit/`+ row["nu_id"] +`" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        Edit
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/libprep/delete/` + row["nu_id"] +`" class="menu-link px-3" data-kt-docs-table-filter="delete_row">
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

          var dateRange = document.getElementById("id_date_range").value;
          var naType = document.getElementById("id_na_type").value;

          initDatatable(null,dateRange,naType)

        });
    }

    // Delete nucacid
    var handleDeleteRows = () => {
        // Select all delete buttons
        const deleteButtons = document.querySelectorAll('[data-kt-docs-table-filter="delete_row"]');

        deleteButtons.forEach(d => {
            // Delete button on click
            d.addEventListener('click', function (e) {
                e.preventDefault();

                // Select parent row
                const parent = e.target.closest('tr');

                const name = parent.querySelectorAll('td')[1].innerText;
                const id = parent.querySelectorAll('td')[0].querySelector(".form-check-input").value;

                $.ajax({
                    url: "/libprep/check_can_deleted_async",
                    type: "GET",
                    data: {
                      "id": id,
                    },
                    async:false,
                    error: function (xhr, ajaxOptions, thrownError) {
                        if (xhr.status == 403) {

                          Swal.fire({
                              text: "You do not have permission to delete.",
                              icon: "error",
                              buttonsStyling: false,
                              confirmButtonText: "Ok, got it!",
                              customClass: {
                                  confirmButton: "btn fw-bold btn-primary",
                              }
                          });

                        }
                    }
                }).done(function (data) {

                  var message = "Are you sure you want to delete " + name + "?";

                  if (data.related_objects.length > 0) {

                    message += " It has downstream records:";

                    for (var item of data.related_objects) {

                      message += item.model + "(" + item.count + ")"

                    }

                  }

                  Swal.fire({
                      text: message,
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
                              text: "Deleting " + name,
                              icon: "info",
                              buttonsStyling: false,
                              showConfirmButton: false,
                              timer: 1000
                          }).then(function () {

                            $.ajax({
                                url: parent.querySelector('[data-kt-docs-table-filter="delete_row"]').href,
                                type: "DELETE",
                                headers: {'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value },
                                error: function (xhr, ajaxOptions, thrownError) {
                                  Swal.fire({
                                      text: name + " was not deleted.",
                                      icon: "error",
                                      buttonsStyling: false,
                                      confirmButtonText: "Ok, got it!",
                                      customClass: {
                                          confirmButton: "btn fw-bold btn-primary",
                                      }
                                  });
                                }
                            }).done(function () {

                              Swal.fire({
                                    text: "Nucleic acid was deleted succesfully.",
                                    icon: "info",
                                    buttonsStyling: false,
                                    confirmButtonText: "Ok, got it!",
                                    customClass: {
                                        confirmButton: "btn fw-bold btn-success",
                                    }
                                }).then(function(){

                                  dt.draw();

                                });

                            });

                          });
                      }
                  });

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

          document.getElementById("id_date_range").value = "";

          document.getElementById("id_na_type").value = "";

          initDatatable(null, null, null);

        });
    }

    // Init toggle toolbar
    var initToggleToolbar = function () {
        // Toggle selected action toolbar
        // Select all checkboxes
        const container = document.querySelector('.table');
        const checkboxes = container.querySelectorAll('[type="checkbox"]');

        // Toggle delete selected toolbar
        checkboxes.forEach(c => {
            // Checkbox on click event
            c.addEventListener('click', function () {
                setTimeout(function () {
                    toggleToolbars();
                }, 50);
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

    // Functions in selected rows
    var handleSelectedRows = ((e) => {

      var isInit = false;

      const container = document.querySelector('.table');

      var stepper = new KTStepper(document.getElementById("modal_stepper"));

      var modal = new bootstrap.Modal(document.getElementById("modal_samplelib_options"));

      // Toggles the enable the print and submit buttons.
      function toggleButtons(state) {

        document.querySelector('[data-kt-stepper-action="print"]').disabled = !state;
        document.querySelector('[data-kt-stepper-action="submit"]').disabled = state;

      }

      // Initializes sample library options modal
      function initModal() {

        function resetStepper() {

          stepper.goFirst();

        }

        function resetForm() {

          document.getElementById("frm_creation_options").reset();

        }

        function resetTable() {

          document.querySelector(".list-body").innerHTML = "";

        }

        function hidePrintAsCSV() {

          document.querySelector('[data-kt-stepper-action="print"]').classList.add("d-none");

        }

        document.getElementById("modal_samplelib_options").addEventListener('show.bs.modal', function(e){

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

            if (!isInit) {

              isInit = true;

              initModalEvents().init();
            }

          }

        });

        document.getElementById("modal_samplelib_options").addEventListener('hide.bs.modal', function(e){

          resetForm();

          resetStepper();

          resetTable();

          hidePrintAsCSV();

          dt.draw();

        });

      }

      // Initializes modal events
      function initModalEvents() {

        // Capitalizes the character entered in the prefix field
        function initPrefixKeyUp() {

          document.getElementById("id_prefix").addEventListener("keyup", function () {

            this.value = this.value.toLocaleUpperCase();

          });

        }

        // Initializes Continue button. Creates new sample library using ajax method as asynchronous.
        function initContinueClick() {

          document.querySelector('[data-kt-stepper-action="next"]').addEventListener('click', function () {

            $.ajax({
              type: "GET",
              url: "/samplelib/new_async",
              data: {
                "selected_ids": getSelectedRows(),
                "options": getCreationOptions()
              },
              beforeSend: function () {

                handleSpinner(true);

              }
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
                });

                handleSize();

                fillElements(result.data);

                initEventsDynamically().init();

                handlePrintAsCSV();

                stepper.goNext();

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

              handleSpinner(false);

            });

          });

        }

        // Initializes Submit button. Updates sample library using ajax method as asynchronous.
        function initSubmit() {

          document.querySelector('[data-kt-stepper-action="submit"]').addEventListener('click', function () {

            $.ajax({
              type: "GET",
              url: "/samplelib/update_async",
              data: {
                "values": getValues(),
              },
            }).done(function(result) {
              if (result.success) {
                Swal.fire({
                    text: "Sample Library(s) was updated succesfully.",
                    icon: "info",
                    buttonsStyling: false,
                    confirmButtonText: "Ok, got it!",
                    customClass: {
                        confirmButton: "btn fw-bold btn-success",
                    }
                });

                toggleButtons(true);

              }
              else {
                Swal.fire({
                    text: "Sample Library(s) was not updated.",
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

        /*
        * Handles the spinner. Spinner is a load indicator which is occur whenever the application processing/waiting for an operation.
        While the Spinner is loading, you can't interact with target, until the process is completed.
        * @param  {Boolean} state A value that specifies whether to appear.
        */
        function handleSpinner(state) {

          if (state) {

            document.querySelector('[data-kt-stepper-action="next"]').setAttribute("data-kt-indicator", "on");

          }
          else {

            document.querySelector('[data-kt-stepper-action="next"]').removeAttribute("data-kt-indicator");

          }

        }

        // If passed to the second step in the stepper, enlarges the modal.
        function handleSize() {

          var element = document.getElementById("modal_samplelib_options").getElementsByClassName("modal-dialog")[0];

          element.classList.remove("mw-600px");

          element.classList.add("mw-900px");

        }

        // Renders the page based on data coming from the server asynchronously.
        function fillElements(data) {

          var listEl = document.querySelector(".list-body");

          var total_amount = 0;
          var total_volume = 0;

          var shearVolume = parseFloat(document.getElementById("id_shear_volume").value);

          for (var i = 0; i < data.length; i++) {

            var row = `<div class="row m-1" data-id="${ data[i].id }">
                <div class="col-3 align-self-center">${ data[i].sample_lib }</div>
                <div class="col-3 align-self-center">${ data[i].nucacid }</div>
                <div class="col-2 align-self-center">${ data[i].area }</div>
                <div class="col-1 align-self-center">${ data[i].conc }</div>
                <div class="col-1 text-center"><input type="text" class="textinput textInput form-control form-control-sm text-end detail-volume" value="${ data[i].input_vol }"></div>
                <div class="col-1 text-center"><input type="text" class="textinput textInput form-control form-control-sm text-end detail-amount" value="${ data[i].input_amount }"></div>
                <div class="col-1 text-center"><input type="text" class="textinput textInput form-control form-control-sm text-end detail-te" value="${ shearVolume - data[i].input_vol }"></div>
              </div>`;
            listEl.innerHTML += row;

          }

        }

        /*
        * Collects the entered values and creates an array of dictionary.
        * @return {Array} A list of object created from each rows.
        */
        function getValues() {

          var rows = document.querySelector(".list-body").querySelectorAll(".row");

          var values = [];

          for (var row of rows) {

            var id = row.getAttribute("data-id");
            var volume = row.querySelector(".detail-volume").value;
            var amount = row.querySelector(".detail-amount").value;
            var te = row.querySelector(".detail-te").value;

            values.push({
              "id":id,
              "volume":volume,
              "amount": amount,
              "te": te
            });
          }

          return JSON.stringify(values);

        }

        /*
        * Object Ids for export to CSV.
        * @return {String} A list of number as a string.
        */
        function getLinkIds() {

          var result = [];

          document.querySelectorAll(".list-body .row").forEach((item, i) => {

            result.push(item.getAttribute("data-id"));

          });

          return JSON.stringify(result);
        }

        // Exports to CSV file
        function handlePrintAsCSV() {

          var element = document.querySelector('[data-kt-stepper-action="print"]');
          element.classList.remove("d-none");
          element.setAttribute("onclick", "window.location.href='/samplelib/print_as_csv?selected_ids=" + getLinkIds() +"'");

        }

        return {
          init: function () {
            initPrefixKeyUp(),initContinueClick(), initSubmit();
          }
        }

      }

      // Events after modal rendered
      function initEventsDynamically() {

        var shearVolume = parseFloat(document.getElementById("id_shear_volume").value);

        // Calculates the values depend on the volume changing for each rows.
        function initVolumeChange() {

          for (var amount of document.querySelectorAll(".detail-volume")) {

            amount.addEventListener("change", function () {

              var parent = this.closest('.row');

              var conc = parseFloat(parent.querySelectorAll('div')[3].innerText);

              var amount = this.value * conc;

              parent.querySelector(".detail-amount").value = amount;

              parent.querySelector(".detail-te").value = shearVolume - this.value;

              toggleButtons(false);

            });

          }

        }

        // Calculates the values depend on the amount changing for each rows.
        function initAmountChange() {

          for (var amount of document.querySelectorAll(".detail-amount")) {

            amount.addEventListener("change", function () {

              var parent = this.closest('.row');

              var conc = parent.querySelectorAll('div')[3].innerText;

              var volume = parseFloat(this.value / conc).toFixed(2);

              parent.querySelector(".detail-volume").value = volume;

              parent.querySelector(".detail-te").value = parseFloat(shearVolume - volume).toFixed(2);


              toggleButtons(false);

            });

          }

        }

        return {
          init: function () {
            initVolumeChange(),initAmountChange();
          }
        }

      }

      /*
      * Object Ids for some processes like deletion, creation.
      * @return {String} A list of number as a string.
      */
      function getSelectedRows() {

        const selectedRows = container.querySelectorAll('tbody [type="checkbox"]:checked');

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

      /*
      * Serializes the form.
      * @return {String} A list of object as a string.
      */
      function getCreationOptions() {

        var data = new FormData(document.getElementById('frm_creation_options'));
        var options = Object.fromEntries(data.entries());

        return JSON.stringify(options);
      }

      /*
      * Checks that the selected objects must be of the same type.
      * @return {Boolean} If type of all selected items is same, returns True.
      */
      function checkSelectedRows() {

        const selectedRows = container.querySelectorAll('tbody [type="checkbox"]:checked');

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

      // Deletes all selected rows.
      function handleBatchDelete() {

        // Select elements
        var deleteSelected = document.querySelector('[data-kt-docs-table-select="delete_selected"]');

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

                        $.ajax({
                            type: "GET",
                            url: "/libprep/batch_delete",
                            data: {
                              "selected_ids": getSelectedRows(),
                            },
                            error: function (xhr, ajaxOptions, thrownError) {
                                swal("Error deleting!", "Please try again", "error");
                            }
                        }).done(function (result) {
                            if (result.deleted) {
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
                        });

                    });
                } else if (result.dismiss === 'cancel') {
                    Swal.fire({
                        text: "Selected nucacids was not deleted.",
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

      // Unchecks the checkbox in header of datatable.
      function uncheckedFirstCheckBox() {

        dt.on( 'draw', function () {

          const headerCheckbox = container.querySelectorAll('[type="checkbox"]')[0];
          headerCheckbox.checked = false;

        });

      }

      return {
        init: function () {
          initModal(),handleBatchDelete(), uncheckedFirstCheckBox(), toggleButtons(true);
        }
      }

    })();

    // Provides the datatable to be fully editable. official docs for more info  --> https://editor.datatables.net
    var initEditor = function () {

      var methodOptions = [];
      var naTypeOptions = [];

      Promise.all([

        getMethodOptions(),
        getNaTypeOptions()

      ]).then(function() {

        editor = new $.fn.dataTable.Editor({
          ajax: {
            url: "/libprep/edit_nucacid_async",
            type: "POST",
            headers: {'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value },
            success: function (data) {
              if ( !data.success ) {

                Swal.fire({
                    text: data.message,
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
                 label: "Area:",
                 name: "area"
             }, {
                 label: "Nucleic Acid Type:",
                 name: "na_type",
                 type: "select",
                 options: naTypeOptions
             }, {
                 label: "Date:",
                 name: "date",
                 type: "datetime",
                 // def: function () { return new Date(); },
                 displayFormat: "M/D/YYYY",
                 wireFormat: 'YYYY-MM-DD'
             }, {
                 label: "Method:",
                 name: "method",
                 type: "select",
                 options: methodOptions
             }, {
                 label: "Concentration:",
                 name: "conc",
             }, {
                 label: "Volume Init:",
                 name: "vol_init"
             }, {
                 label: "Volume Remain:",
                 name: "vol_remain"
             }
         ],
         formOptions: {
            inline: {
              onBlur: 'submit'
            }
         }
        });

      });

      $('.table').on( 'click', 'tbody td:not(:first-child)', function (e) {
        editor.inline( dt.cell( this ).index(), {
            onBlur: 'submit'
        });
      });

      $('.table').on( 'key-focus', function ( e, datatable, cell ) {
          editor.inline( cell.index() );
      });

      // Gets the method options and fills the dropdown. It is executed synchronous.
      function getMethodOptions() {

        $.ajax({
            url: "/method/get_methods",
            type: "GET",
            async: false,
            success: function (data) {

             // var options = [];
             data.forEach((item, i) => {

               methodOptions.push({
                 "label":item["name"],
                 "value":item["id"]
               })

             });

             // editor.field( 'method' ).update( options );

            }
        });

      }

      // Gets the nucleic acid type options and fills the dropdown. It is executed synchronous.
      function getNaTypeOptions() {

        $.ajax({
            url: "/libprep/get_na_types",
            type: "GET",
            async: false,
            success: function (data) {

             // var options = [];
             data.forEach((item, i) => {

               naTypeOptions.push({
                 "label":item["label"],
                 "value":item["value"]
               })

             });

             // editor.field( 'method' ).update( options );

            }
        });

      }

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

    // Public methods
    return {
        init: function () {
            initDatatable( handleInitialValue(),null,null );
            handleSearchDatatable();
            initToggleToolbar();
            handleFilterDatatable();
            handleDeleteRows();
            handleResetForm();
            handleSelectedRows.init();
            initEditor();
        }
    }
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesServerSide.init();
});
