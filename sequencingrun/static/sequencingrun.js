"use strict";

// Class definition
var KTDatatablesServerSide = function () {
    // Shared variables
    var table;
    var dt;
    var filterPayment;
    var editor;
    var selectedRows = [];

    // Private functions
    var initDatatable = function ( initialValue ) {

        $.fn.dataTable.moment( 'MM/DD/YYYY' );

        dt = $(".table").DataTable({
            // searchDelay: 500,
            processing: true,
            serverSide: true,
            order: [[2, 'desc']],
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
            ajax: {
              url: '/sequencingrun/filter_sequencingruns',
              type: 'GET',
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
                { data: 'id' },
                { data: 'name' },
                { data: 'date',
                  render: function (data) {
                    return moment(data).format('MM/DD/YYYY');
                  }
                },
                { data: 'facility',
                  render: function (val, type, row) {
                    return row["facility_label"];
                  }
                },
                { data: 'sequencer',
                  render: function (val, type, row) {
                    return row["sequencer_label"];
                  }
                },
                { data: 'pe',
                  render: function (val, type, row) {
                    return row["pe_label"];
                  }
                },
                { data: 'amp_cycles' },
                { data: 'date_run',
                  render: function (data) {
                    return moment(data).format('MM/DD/YYYY');
                  }
                },
                { data: 'num_sequencinglibs' },
                { data: 'num_file_sets' },
                { data: null },
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
                {
                    targets: 8,
                    className: 'text-center',
                    orderable: true,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let id = row["id"];
                          return `
                              <a href="/sequencinglib?model=sequencing_run&id=${id}&initial=true">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 9,
                    orderable: true,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let sl_id = row["id"];
                          return `
                              <a href="/sequencingfile/sequencingfilesets?id=${sl_id}&initial=true&model=sequencing_run">${data}</a>`;
                        }
                        return data;
                    }
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
                                <div class="menu-item">
                                    <a href="/sequencingrun/edit/`+ row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        Edit
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item">
                                    <a href="javascript:;" class="menu-link detail-link" data-kt-docs-table-filter="detail_row">
                                        Used Library(s)
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item">
                                    <a href="javascript:;" class="menu-link sequencing-files-link text-start" data-kt-docs-table-filter="detail_row">
                                        Get Sequencing Files
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item">
                                    <a href="/sequencingrun/delete/` + row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="delete_row">
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
            initRowSelection();
            handleRestoreRowSelection();
            initToggleToolbar();
            toggleToolbars();
            handleDeleteRows();
            handleResetForm();
            initRowActions();
            handleSelectedRows.init();
            KTMenu.createInstances();
        });
    }

    var initRowSelection = function () {
        // Select all checkboxes
        const allCheckboxes = document.querySelectorAll('.table tbody [type="checkbox"]');
        allCheckboxes.forEach(c => {
            // Checkbox on Change event
            c.addEventListener("change", function () {
                toggleRowSelection(c.value);
            });

            // Checkbox on click event
            c.addEventListener('click', function () {
                setTimeout(function () {
                    toggleToolbars();
                }, 50);
            });
        });

        function toggleRowSelection(id) {
            var index = selectedRows.indexOf(id);
            if (index === -1) {
                // If the row is not selected, add it to selected rows
                selectedRows.push(id);
            } else {
                // If the row is already selected, remove it in selected rows
                selectedRows.splice(index, 1);
            }
        }

    }

    var handleRestoreRowSelection = function () {
        const allCheckboxes = document.querySelectorAll('.table tbody [type="checkbox"]');
        allCheckboxes.forEach(c => {
            if ( selectedRows.indexOf(c.value) > -1 ) {
                c.checked = true;
            }
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

                const name = parent.querySelectorAll('td')[1].innerText;
                const id = parent.querySelectorAll('td')[0].querySelector(".form-check-input").value;

                $.ajax({
                    url: "/sequencingrun/check_can_deleted_async",
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
                                      text: name + " could not be deleted.",
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
                                    text: "Sequencing Run deleted succesfully.",
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

        // Toggle toolbars
        if (selectedRows.length > 0) {
            selectedCount.innerHTML = selectedRows.length;
            toolbarBase.classList.add('d-none');
            toolbarSelected.classList.remove('d-none');
        } else {
            toolbarBase.classList.remove('d-none');
            toolbarSelected.classList.add('d-none');
        }
    }

    var initEditor = function () {

      var facilityOptions = [];
      var sequencerOptions = [];
      var peOptions = [];

      Promise.all([

        getFacilityOptions(),
        getSequencerOptions(),
        getPeOptions()

      ]).then(function () {

        editor = new $.fn.dataTable.Editor({
          ajax: {
            url: "/sequencingrun/edit_sequencingrun_async",
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
                 label: "Date:",
                 name: "date",
                 type: "datetime",
                 displayFormat: "M/D/YYYY",
                 wireFormat: 'YYYY-MM-DD'
             }, {
                 label: "Facility:",
                 name: "facility",
                 type: "select",
                 options: facilityOptions
             }, {
                 label: "Sequencer:",
                 name: "sequencer",
                 type: "select",
                 options: sequencerOptions
             }, {
                 label: "PE:",
                 name: "pe",
                 type: "select",
                 options: peOptions
             }, {
                 label: "AMP Cycles:",
                 name: "amp_cycles"
             }, {
                 label: "Date Run:",
                 name: "date_run",
                 type: "datetime",
                 displayFormat: "M/D/YYYY",
                 wireFormat: 'YYYY-MM-DD'
             },
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

     function getFacilityOptions() {

       $.ajax({
           url: "/sequencingrun/get_facilities",
           type: "GET",
           async: false,
           success: function (data) {

            // var options = [];
            data.forEach((item, i) => {

              facilityOptions.push({
                "label":item["label"],
                "value":item["value"]
              })

            });
           }
       });

     }

     function getSequencerOptions() {

       $.ajax({
           url: "/sequencingrun/get_sequencers",
           type: "GET",
           async: false,
           success: function (data) {

            // var options = [];
            data.forEach((item, i) => {

              sequencerOptions.push({
                "label":item["label"],
                "value":item["value"]
              })

            });
           }
       });

     }

     function getPeOptions() {

       $.ajax({
           url: "/sequencingrun/get_pes",
           type: "GET",
           async: false,
           success: function (data) {

            // var options = [];
            data.forEach((item, i) => {

              peOptions.push({
                "label":item["label"],
                "value":item["value"]
              })

            });
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
      const model = params.get('model');
      const id = params.get('id');
      const initial = params.get('initial');
      cleanUrl();

      if (initial =="true" && model != null && id !=null) {

        return JSON.stringify({
          "model": model,
          "id": id
        });

      }

      return null;

    }

    var handleSelectedRows = ((e) => {

      const container = document.querySelector('.table');

      function uncheckedFirstCheckBox() {

        dt.on( 'draw', function () {

          // Remove header checked box
          const headerCheckbox = container.querySelectorAll('[type="checkbox"]')[0];
          headerCheckbox.checked = false;

        });

      }

       function handleGenerateSheet() {
          const generateSelected = document.querySelector('[data-kt-docs-table-select="generate_broad_institute"]');
            generateSelected.addEventListener('click', function () {
                const loadingEl = document.createElement("div");
                document.body.prepend(loadingEl);
                loadingEl.classList.add("page-loader");
                loadingEl.classList.add("flex-column");
                loadingEl.classList.add("bg-dark");
                loadingEl.classList.add("bg-opacity-25");
                loadingEl.innerHTML = `
                    <span class="spinner-border text-primary" role="status"></span>
                    <span class="text-gray-800 fs-6 fw-semibold mt-5">"CSV File is Generating..."</span>
                `;
                KTApp.showPageLoading();

                $.ajax({
                url: '/sheet/generate_broad_institute',
                type: 'POST',
                headers: {'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value },
                data: {
                    "selected_ids": JSON.stringify(selectedRows)
                },
                xhrFields: {
                    responseType: 'blob'
                },
                success: function(data, status, xhr) {
                    var filename = "";
                    var disposition = xhr.getResponseHeader('Content-Disposition');
                    if (disposition && disposition.indexOf('attachment') !== -1) {
                        var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                        var matches = filenameRegex.exec(disposition);
                        if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
                    }

                    var blob = new Blob([data], { type: 'text/csv' });

                    var link = document.createElement('a');
                    link.href = window.URL.createObjectURL(blob);
                    link.download = filename || "seq_run_sheet.csv"; // Provide a default filename if none is found
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    loadingEl.remove();
                    Swal.fire({
                        text: "Your file is downloaded!.",
                        icon: "success",
                        buttonsStyling: false,
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                            confirmButton: "btn fw-bold btn-primary",
                        }
                    }).then(function(){
                  wait(1500);
                  location.reload();
              });
                },
                error: function(response) {
                    loadingEl.remove();
                     Swal.fire({
                        text: "Your file can not created",
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


       function handleUCSFcat() {
          const generateSelected = document.querySelector('[data-kt-docs-table-select="generate_ucsf_cat"]');
            generateSelected.addEventListener('click', function () {
                const loadingEl = document.createElement("div");
                document.body.prepend(loadingEl);
                loadingEl.classList.add("page-loader");
                loadingEl.classList.add("flex-column");
                loadingEl.classList.add("bg-dark");
                loadingEl.classList.add("bg-opacity-25");
                loadingEl.innerHTML = `
                    <span class="spinner-border text-primary" role="status"></span>
                    <span class="text-gray-800 fs-6 fw-semibold mt-5">"CSV File is Generating..."</span>
                `;
                KTApp.showPageLoading();

                $.ajax({
                url: '/sheet/generate_ucsf_cat',
                type: 'POST',
                headers: {'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value },
                data: {
                    "selected_ids": JSON.stringify(selectedRows)
                },
                xhrFields: {
                    responseType: 'blob'
                },
                success: function(data, status, xhr) {
                    var filename = "";
                    var disposition = xhr.getResponseHeader('Content-Disposition');
                    if (disposition && disposition.indexOf('attachment') !== -1) {
                        var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                        var matches = filenameRegex.exec(disposition);
                        if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
                    }

                    var blob = new Blob([data], { type: 'text/csv' });

                    var link = document.createElement('a');
                    link.href = window.URL.createObjectURL(blob);
                    link.download = filename || "seq_run_sheet.csv"; // Provide a default filename if none is found
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    loadingEl.remove();
                    Swal.fire({
                        text: "Your file is downloaded!.",
                        icon: "success",
                        buttonsStyling: false,
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                            confirmButton: "btn fw-bold btn-primary",
                        }
                    }).then(function(){
                  wait(1500);
                  location.reload();
              });
                },
                error: function(response) {
                    loadingEl.remove();
                     Swal.fire({
                        text: "Your file can not created",
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

      function handleBatchDelete() {

        // Select elements
        const deleteSelected = document.querySelector('[data-kt-docs-table-select="delete_selected"]');

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
                            url: "/sequencingrun/batch_delete",
                            data: {
                              "selected_ids": JSON.stringify(selectedRows),
                            },
                            error: function (xhr, ajaxOptions, thrownError) {
                                swal("Error deleting!", "Please try again", "error");
                            }
                        }).done(function (result) {
                            if (result.deleted) {
                              Swal.fire({
                                  text: "Sequencing Run(s) deleted succesfully.",
                                  icon: "info",
                                  buttonsStyling: false,
                                  confirmButtonText: "Ok, got it!",
                                  customClass: {
                                      confirmButton: "btn fw-bold btn-success",
                                  }
                              }).then(function(){
                                  // clean selected rows
                                  selectedRows = [];
                                  // refresh dataTable
                                  dt.draw();
                              });
                            }
                            else {
                              Swal.fire({
                                  text: "Sequencing Run(s) could not be deleted!",
                                  icon: "error",
                                  buttonsStyling: false,
                                  confirmButtonText: "Ok, got it!",
                                  customClass: {
                                      confirmButton: "btn fw-bold btn-success",
                                  }
                              });
                            }
                        });

                        // Remove header checked box
                        const headerCheckbox = container.querySelectorAll('[type="checkbox"]')[0];
                        headerCheckbox.checked = false;
                    });
                }
            });
        });

      }

      // Closure to keep track of initialization state
      let isModalInitialized = false;
      let modal, stepper, form, listBody, menuItem;

      stepper = new KTStepper(document.getElementById("modal_stepper"));

      function handleGenerateAnalysisSheet() {

          // Initialize modal and related elements only once
          if (!isModalInitialized) {
              initializeModalElements();
          }

          initGenerateAnalysisSheetButton();

          function initializeModalElements() {
              modal = new bootstrap.Modal(document.getElementById("modal_analysis_sheet"));
              menuItem = document.querySelector('[data-kt-docs-table-select="generate_analysis_sheet"]');
              const stepperElement = document.getElementById("modal_stepper");
              form = document.getElementById("form-analysis-run");
              listBody = document.querySelector("#analysis-sheet-list tbody");

              // Initialize modal events only once
              initModalEvents();

              isModalInitialized = true;
          }

          function initGenerateAnalysisSheetButton() {
              // Remove existing event listener if any
              menuItem.removeEventListener("click", fetchData);
              // Add new event listener
              menuItem.addEventListener("click", fetchData);
          }

          function initModalEvents() {
              const modalElement = document.getElementById("modal_analysis_sheet");

              modalElement.addEventListener('hide.bs.modal', function(){
                  resetModal();
              });

              modalElement.addEventListener('shown.bs.modal', function(){
                  initStepper();
              });

              document.querySelector('[data-kt-stepper-action="submit"]').addEventListener("click", submitForm);
          }

          function resetModal() {
              console.log("reset modeal");
                listBody.innerHTML = "";

                if (stepper) {
                    stepper.destroy();  // <--- important! destroy stepper cleanly
                    stepper = null;
                }

                form.reset();
                selectedRows = [];
                dt.draw();
            }

            function initStepper() {
                const stepperElement = document.getElementById("modal_stepper");

                if (stepperElement) {
                    if (stepper) {
                        stepper.destroy();
                    }

                    stepper = new KTStepper(stepperElement);

                    const stepperContents = stepperElement.querySelectorAll('[data-kt-stepper-element="content"]');
                    if (stepperContents.length > 0) {
                        stepperContents.forEach((content, index) => {
                            if (index === 0) {
                                content.classList.add('current');  // first step active
                            } else {
                                content.classList.remove('current'); // others hidden by default
                            }
                        });
                    }

                    // Stepper event listeners
                    stepper.on("kt.stepper.next", function (stepperObj) {
                        stepperObj.goNext();
                    });

                    stepper.on("kt.stepper.previous", function (stepperObj) {
                        stepperObj.goPrevious();
                    });
                }
            }




          function fetchData() {
                const loadingEl = document.createElement("div");
                document.body.prepend(loadingEl);
                loadingEl.classList.add("page-loader");
                loadingEl.classList.add("flex-column");
                loadingEl.classList.add("bg-dark");
                loadingEl.classList.add("bg-opacity-25");
                loadingEl.innerHTML = `
                    <span class="spinner-border text-primary" role="status"></span>
                    <span class="text-gray-800 fs-6 fw-semibold mt-5">"Sequencing Files are loading..."</span>
                `;
                KTApp.showPageLoading();
              $.ajax({
                  type: "GET",
                  url: "/sequencingrun/get_sample_libs_async",
                  data: {
                      "selected_ids": JSON.stringify(selectedRows),
                  },
                  error: function (xhr, ajaxOptions, thrownError) {
                      loadingEl.remove();
                      swal("Error getting records!", "Please try again", "error");
                  }
              }).done(function (result) {
                  loadingEl.remove();
                  populateTable(result);
                  modal.show();
              });
          }

          function populateTable(data) {
            const listBody = document.querySelector("#analysis-sheet-list tbody"); // Find the existing tbody
              console.log("data coming");
              console.log(data);
            listBody.innerHTML = ''; // Clear previous rows


            data.forEach(item => {
                var path = "";
                if (item.path_fastq) {
                    path = `${item.path_fastq}`;
                } else if (item.path_bam) {
                    path = `${item.path_bam}`;
                } else if (item.path_bai) {
                    path = `${item.path_bai}`;
                }
                let file = "";
                if (item.fastq) {
                    file = item.fastq;
                } else if (item.bam) {
                    file = item.bam;
                } else if (item.bai) {
                    file = item.bai;
                }

                const row = document.createElement("tr");

                row.appendChild(createCheckboxCell());
                row.appendChild(createTableCell("#")); // Or you can use row index if needed
                row.appendChild(createTableCell(item.patient || ""));
                row.appendChild(createTableCell(item.barcode_name || ""));
                row.appendChild(createTableCell(item.na_type || ""));
                row.appendChild(createTableCell(item.area_type || ""));
                row.appendChild(createTableCell(item.seq_run || ""));
                row.appendChild(createTableCell(item.name || ""));
                row.appendChild(createTableCell(item.bait || ""));
                row.appendChild(createTableCell(file));
                row.appendChild(createTableCell(path));
                row.appendChild(createTableCell(item.matching_normal_sl || ""));

                listBody.appendChild(row);
            });
        }


        function createCheckboxCell() {
            const td = document.createElement("td");
            const checkDiv = document.createElement("div");
            checkDiv.classList.add("form-check", "form-check-sm", "form-check-custom", "form-check-solid", "me-3");
            const input = document.createElement("input");
            input.type = "checkbox";
            input.classList.add("form-check-input");
            input.checked = true;
            checkDiv.appendChild(input);
            td.appendChild(checkDiv);
            return td;
        }

        function createTableCell(content) {
            const td = document.createElement("td");
            const span = document.createElement("span");
            span.textContent = content;
            td.appendChild(span);
            return td;
        }




            function downloadCSV(csvContent) {
                // Create a blob with the CSV content
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

                // Create download link
                const link = document.createElement('a');
                const url = URL.createObjectURL(blob);

                // Set up download properties
                link.setAttribute('href', url);
                link.setAttribute('download', 'table-data.csv');
                link.style.visibility = 'hidden';

                // Add to document, trigger download, and clean up
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }

          function submitForm() {
              if (!form.checkValidity()) {
                    form.reportValidity();
                    return;
                }
                const formData = new FormData(form);
                const pipelineDropdown = form.querySelector('select[name="pipeline"]');
                const genomeDropdown = form.querySelector('select[name="genome"]');

                const pipeline = pipelineDropdown.value;
                const genome = genomeDropdown.value;
                console.log(pipeline, genome);
              $.ajax({
                  url: "/analysisrun/save_analysis_run",
                  type: "POST",
                  headers: {
                      'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
                  },
                  data: {
                         "selected_ids":selectedRows,
                         "pipeline":pipeline,
                         "genome":genome
                      },
                  success: function (data, status, xhr) {
                    const blob = new Blob([data], { type: 'text/csv' });
                    const url = window.URL.createObjectURL(blob);
                    const link = document.createElement("a");

                    // Try to get filename from response headers
                    const disposition = xhr.getResponseHeader("Content-Disposition");
                    let filename = "download.csv";
                    if (disposition && disposition.indexOf("filename=") !== -1) {
                        filename = disposition.split("filename=")[1].replace(/['"]/g, '');
                    }

                    link.href = url;
                    link.download = filename;

                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                    window.URL.revokeObjectURL(url);

                    Swal.fire({
                        text: "CSV file has been downloaded successfully.",
                        icon: "success",
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                            confirmButton: "btn fw-bold btn-primary",
                        }
                    }).then((result) => {
                        if (result.isConfirmed) {
                          // this will reload the page
                          window.location.reload();
                        }
                      });

                    modal.hide();

                },
                  error: function (xhr, ajaxOptions, thrownError) {
                      Swal.fire({
                          text: "An error occurred. The operation could not be performed.",
                          icon: "error",
                          buttonsStyling: false,
                          confirmButtonText: "Ok, got it!",
                          customClass: {
                              confirmButton: "btn fw-bold btn-primary",
                          }
                      });
                  }
              });
          }
      }


      return {
        init: function () {
          handleBatchDelete(), handleGenerateSheet(),  handleUCSFcat(), uncheckedFirstCheckBox(), handleGenerateAnalysisSheet();
        }
      }

    })();

    function loadingEl() {
        const loadingEl = document.createElement("div");
        document.body.prepend(loadingEl);
        loadingEl.classList.add("page-loader");
        loadingEl.classList.add("flex-column");
        loadingEl.innerHTML = `
                <span class="spinner-border text-primary" role="status"></span>
                <span class="text-gray-800 fs-6 fw-semibold mt-5">Loading...</span>
            `;
        KTApp.showPageLoading();
        return loadingEl;
    }

    var initSequencingFilesModal = function () {

        const elSequencingFiles = document.getElementById("modal_sequencing_files");
        const modalSequencingFiles = new bootstrap.Modal(elSequencingFiles);
        var matchingTable = [];
        var sequencingRunId = null;

        document.querySelectorAll(".sequencing-files-link").forEach((item, i) => {
          item.addEventListener("click", function () {
            const parent = this.closest('tr');

            sequencingRunId = parent.querySelector('input[type=checkbox]').value;

            Swal.fire({
                title: 'Loading...',
                text: 'Fetching sequencing files, please wait...',
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
            $.ajax({
                url: "/sequencingrun/" + sequencingRunId + "/get_sequencing_files",
                type: "GET",
                success: function (data) {
                  if (data.success) {
                        Swal.close();
                        initialMachingTable(data);
                        fillElements(data);
                        checkMatching();
                        modalSequencingFiles.show();
                  }
                  else {
                      Swal.fire({
                        title: "Error",
                        text: `${data.message}`,
                        icon: "error",
                        buttonsStyling: false,
                        confirmButtonText: "Ok, got it!",
                        width: "700px", // 📏 Increase popup width
                        padding: "2em", // 🧱 Add padding around content
                        customClass: {
                            popup: "swal2-large-popup",
                            title: "swal2-large-title",
                            htmlContainer: "swal2-large-text",
                            confirmButton: "btn fw-bold btn-primary btn-lg", // 💡 Larger button
                        }
                    });
                  }
              },
              error: function (data) {}
            });

          });

        });

        document.querySelector("#modal_sequencing_files button[name='btnSave']").addEventListener("click", function() {
            saveChanges();
        });

        // Creating file set dropdown
        function generateFileSetSelect(file_sets, sl=null) {
            var sel = document.createElement("select");
            sel.classList.add("select","form-control","form-control-sm");

            var emptyOption = document.createElement("option");
            emptyOption.text = "Not Matched";
            emptyOption.value = "";
            sel.add(emptyOption, 0);

            for (const item of file_sets) {
                var option = document.createElement("option");
                option.value = item.file_set;
                option.text = item.file_set;
                option.setAttribute("data-files_number",item.files.length);

                if (item.file_set.startsWith(sl.name)) {
                    option.selected = true;
                }

                sel.add(option);
             }

             // Add a change event listener to the created select element
            sel.addEventListener("change", function (event) {
                var select = event.target; // the select element that on the process
                setFilesNumber(select);
                swap(select);
                checkMatching();
            });

             return sel;

        }

        function initialMachingTable(data) {
            matchingTable = [];
            for (var sl of data.sample_libs) {
                var tmp = {
                    "sample_lib":sl.name,
                    "initial":"",
                    "swap":"",
                };
                for (var fs of data.file_sets) {
                    if (fs.file_set.startsWith(sl.name)) {
                        tmp["swap"] = tmp["initial"] = fs.file_set;
                    }
                }
                matchingTable.push(tmp);
            }
        }

        function swap(select) {
            var selectedValue = select.value;
            //  All select elements for file_sets
            var selects = document.querySelectorAll(".list-body2 select");

            // The position of the selected item in the matchingTable
            var matchedIndex = matchingTable.findIndex(item => item["swap"] === selectedValue);

            if (matchedIndex !== -1) {
                // reset
                matchingTable[matchedIndex]["swap"] = "";
                selects[matchedIndex].value = "";
                // Find the corresponding select element index in .list-body2
                var swappingIndex = Array.from(selects).findIndex((sel) => sel.value === selectedValue);
                // swapping the datas
                matchingTable[matchedIndex]["swap"] = matchingTable[swappingIndex]["swap"];
                matchingTable[swappingIndex]["swap"] = selectedValue;
                // set new value
                selects[matchedIndex].value = matchingTable[matchedIndex]["swap"];

            }
            else {
                var swappingIndex = Array.from(selects).findIndex((sel) => sel.value === selectedValue);
                matchingTable[swappingIndex]["swap"] = selectedValue;
            }

        }

        function checkMatching() {

            document.querySelectorAll(".list-body2 .row").forEach((item, i) => {

                if ( item.querySelector("select").value.startsWith(item.querySelector("input[type=text]").value) ) {

                    item.querySelectorAll("input[type=text], select").forEach((element, i) => {
                        element.style.border = "";
                    });
                }
                else {

                    item.querySelectorAll("input[type=text], select").forEach((element, i) => {
                        element.style.border = "1px solid red";
                    });

                }
            });

        }

        function setFilesNumber(select) {
            var selectedItem = select.options[select.selectedIndex]
            var row = selectedItem.closest(".row");
            row.querySelector(".col-2 input[type='text']").value = selectedItem.getAttribute("data-files_number") | 0;
        }

        function fillElements(data) {
            var list = document.querySelector(".list-body2");

            list.innerHTML = ""; // Clean the list

            for (var sl of data.sample_libs) {
                var sel = generateFileSetSelect(data.file_sets, sl);

                // Create elements for the row and its columns
                var row = document.createElement("div");
                row.classList.add("row","mb-1");

                var col1 = document.createElement("div");
                col1.classList.add("col-4");
                var input = document.createElement("input");
                input.type = "text";
                input.classList.add("form-control", "form-control-sm");
                input.value = sl.name;
                col1.appendChild(input);

                var col2 = document.createElement("div");
                col2.classList.add("col-6");
                col2.appendChild(sel);

                var col3 = document.createElement("div");
                col3.classList.add("col-2");
                var inputFilesNumber = document.createElement("input");
                inputFilesNumber.type = "text";
                inputFilesNumber.classList.add("form-control", "form-control-sm", "text-center");
                inputFilesNumber.disabled = true;
                inputFilesNumber.value = sel.options[sel.selectedIndex].getAttribute("data-files_number") || 0;
                col3.appendChild(inputFilesNumber);

                // Append columns to the row
                row.appendChild(col1);
                row.appendChild(col2);
                row.appendChild(col3);

                // Append the row to the list
                list.appendChild(row);
           }

        }

        function saveChanges() {
            Swal.fire({
                title: 'Saving...',
                text: 'Saving files and file sets...',
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
            $.ajax({
                url: "/sequencingrun/" + sequencingRunId + "/save_sequencing_files",
                type: "POST",
                headers: {'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value },
                data: {
                    data: JSON.stringify(matchingTable),
                },
                success: function (data) {

                    if (data.success) {
                        Swal.close();
                        Swal.fire({
                            text: "The sequencing files created successfully and the file locations replaced.",
                            icon: "success",
                            buttonsStyling: false,
                            confirmButtonText: "Ok, got it!",
                            customClass: {
                                confirmButton: "btn fw-bold btn-primary",
                            }
                        });
                    }
                    else {
                        Swal.close();
                        Swal.fire({
                            text: `${data.message}`,
                            icon: "error",
                            buttonsStyling: false,
                            confirmButtonText: "Ok, got it!",
                            customClass: {
                                confirmButton: "btn fw-bold btn-primary",
                            }
                        });
                    }

                    modalSequencingFiles.hide();
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    Swal.close();
                        Swal.fire({
                            text: `${data.message}`,
                            icon: "error",
                            buttonsStyling: false,
                            confirmButtonText: "Ok, got it!",
                            customClass: {
                                confirmButton: "btn fw-bold btn-primary",
                            }
                        });
                }
            });
        }

    }

    var initRowActions = () => {

      const el = document.getElementById("modal_used_sequencinglibs");
      const modal = new bootstrap.Modal(el);

      var data = {};

      initModal();

      initSequencingFilesModal();

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
                url: "/sequencingrun/" + id + "/used_sequencinglibs",
                type: "GET",
                success: function (retval) {

                  data = retval;
                  fillElements(id);
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

        for (var i = 0; i < data.length; i++) {

          var row = `<div class="row mb-1 detail-row">
              <div class="col-4 align-self-center" data-id="${ data[i].id }"><a href="/sequencinglib/edit/${ data[i].id }">${ data[i].name }</a></div>
              <div class="col-3 align-self-center">${ data[i].buffer }</div>
              <div class="col-3 align-self-center text-center">${ data[i].nmol }</div>
              <div class="col-2 align-self-center text-center" data-id="${ data[i].id }"><a href="/sequencingrun/edit/${id}"><i class="fa-trash fs-4 text-danger"></i></a></div>
            </div>`;
          listEl.innerHTML += row;

        }
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
