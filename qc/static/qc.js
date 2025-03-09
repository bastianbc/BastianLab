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
    var initDatatable = function (initialValue,sample_lib,analysis_run,sequencing_run,variant_file,type) {

        $.fn.dataTable.moment( 'MM/DD/YYYY' );

        dt = $(".table").DataTable({
            // searchDelay: 500,
            processing: true,
            serverSide: true,
            order: [[0, 'desc']],
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
                url: '/qc/filter_sampleqcs',
                type: 'GET',
                data: {
                  "sample_lib": sample_lib,
                  "analysis_run": analysis_run,
                  "sequencing_run": sequencing_run,
                  "variant_file": variant_file,
                  "type": type,
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
                { data: 'id' },
                { data: 'sample_lib' },
                { data: 'sequencing_run' },
                { data: 'analysis_run' },
                { data: 'insert_size_histogram' },
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
                    targets: 4,
                    data: 'insert_size_histogram',
                    render: function (data, type, row) {
                        if (!data) {
                            return '<span class="text-muted">No PDF</span>';
                        }
                        return `<a href="pdf/${row['id']}" target="_blank" class="btn btn-sm btn-light-primary">
                                    <i class="bi bi-file-pdf me-1"></i>View PDF
                                </a>`;
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
                                  <a href="/qc/detail/`+ row["id"] +`" class="menu-link px-3">
                                      Edit
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
            initRowActions();
            handleSelectedRows.init();
            KTMenu.createInstances();
        });
    };

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
    };

    // Filter Datatable
    var handleFilterDatatable = () => {
        const filterButton = document.querySelector('[data-kt-docs-table-filter="filter"]');
        // Filter datatable on submit
        filterButton.addEventListener('click', function () {

            var sample_lib = document.getElementById("id_sample_lib").value;
            var analysis_run = document.getElementById("id_analysis_run").value;
            var sequencing_run = document.getElementById("id_sequencing_run").value;
            var variant_file = document.getElementById("id_variant_file").value;
            var type = document.getElementById("id_type").value;
            initDatatable(null,sample_lib,analysis_run,sequencing_run,variant_file,type);

        });
    };

    // Reset Filter
    var handleResetFilter = () => {
        // Select reset button
        const resetButton = document.querySelector('[data-kt-docs-table-filter="reset"]');

        // Reset datatable
        resetButton.addEventListener('click', function () {

                document.getElementById("sample_lib").value='';
                document.getElementById("analysis_run").value='';
                document.getElementById("sequencing_run").value='';
                document.getElementById("variant_file").value='';
                document.getElementById("type").value='';

          initDatatable(null, null, null, null, null, null, null, null);

        });
    };
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
                    url: "/capturedlib/check_can_deleted_async",
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
                                    text: "Captured Library deleted succesfully.",
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

        resetButton.addEventListener('click', function () {

          document.getElementById("normal_area_checkbox").checked = false;


          initDatatable(null, null);
      });
    };

    // Redirects from other pages
    var handleInitialValue = () => {

      // Remove parameters in URL
      function cleanUrl() {
        window.history.replaceState(null, null, window.location.pathname);
      }
      const params = new URLSearchParams(window.location.search);
      const id = params.get('id');
      const initial = params.get('initial');


      cleanUrl();

      if (initial =="true" && id !=null) {

        return JSON.stringify({
          "id": id
        });

      }

      return null;

    };

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

    var handleSelectedRows = ((e) => {

      var isInit = false;

      var container = document.querySelector('.table');





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
                  text: "Sequencing Library(s) could not be created.",
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
              "selected_ids": JSON.stringify(selectedRows),
              "options": getCreationOptions()
            },
          }).done(function(result) {
            if (result.success) {
              Swal.fire({
                  text: "Sequencing Library(s) created succesfully.",
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
                  text: "Sequencing Library(s) could not be created.",
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

      function getCreationOptions() {

        var data = new FormData(document.getElementById('frm_creation_options'));
        var options = Object.fromEntries(data.entries());

        return JSON.stringify(options);
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
                            url: "/capturedlib/batch_delete",
                            data: {
                              "selected_ids": JSON.stringify(selectedRows),
                            },
                            error: function (xhr, ajaxOptions, thrownError) {
                                swal("Error deleting!", "Please try again", "error");
                            }
                        }).done(function (result) {
                            if (result.deleted) {
                              Swal.fire({
                                  text: "Captured Library(s) deleted succesfully.",
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
                                  text: "Captured Library(s) could not be deleted!",
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
                        text: "Selected customers could not be deleted.",
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

      function uncheckedFirstCheckBox() {

        dt.on( 'draw', function () {

          // Remove header checked box
          const headerCheckbox = container.querySelectorAll('[type="checkbox"]')[0];
          headerCheckbox.checked = false;

        });

      }

      return {
        init: function () {
          handleBatchDelete(), uncheckedFirstCheckBox();
        }
      }

    })();

    var handleFilter = () => {

      $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
        var min = parseInt($('#min').val(), 10);
        var max = parseInt($('#max').val(), 10);
        var age = parseFloat(data[3]) || 0; // use data for the age column

        if (
            (isNaN(min) && isNaN(max)) ||
            (isNaN(min) && age <= max) ||
            (min <= age && isNaN(max)) ||
            (min <= age && age <= max)
        ) {
            return true;
        }
        return false;
      });

      $('#min, #max').keyup(function () {
          table.draw();
      });

    }

    var initRowActions = () => {

        document.querySelectorAll(".qc-link").forEach(function (element) {
            element.addEventListener("click", function () {
                const arName = this.getAttribute('data-ar-name');

                // Show loading message
                Swal.fire({
                    title: 'Processing...',
                    text: 'Processing QC metrics for analysis run',
                    icon: 'info',
                    allowOutsideClick: false,
                    showConfirmButton: false,
                });

                // Send AJAX request to server with the updated endpoint
                fetch(`/qc/process/${arName}/`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // Check the status from our new API response format
                    if (data.status === 'success') {
                        // Create a table to display summary report
                        let tableHtml = `
                            <div class="mt-3">
                                <p><strong>QC metrics processed successfully for ${data.analysis_run_name}</strong></p>
                                <p>${data.message}</p>
                                <table class="table table-bordered table-striped">
                                    <thead>
                                        <tr>
                                            <th>Sample Library</th>
                                            <th>Dup Metrics</th>
                                            <th>HS Metrics</th>
                                            <th>Insert Metrics</th>
                                            <th>Histogram PDF</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                        `;

                        // Add rows for each sample library
                        for (const [sampleLib, status] of Object.entries(data.summary_report)) {
                            tableHtml += `
                                <tr>
                                    <td>${sampleLib}</td>
                                    <td>${status.dup_metrics_processed ? '✅' : '❌'}</td>
                                    <td>${status.hs_metrics_processed ? '✅' : '❌'}</td>
                                    <td>${status.insert_metrics_processed ? '✅' : '❌'}</td>
                                    <td>${status.histogram_pdf_processed ? '✅' : '❌'}</td>
                                </tr>
                            `;

                            // If there's an error, add it as a row
                            if (status.error) {
                                tableHtml += `
                                    <tr class="table-danger">
                                        <td colspan="5"><strong>Error:</strong> ${status.error}</td>
                                    </tr>
                                `;
                            }
                        }

                        tableHtml += `
                                    </tbody>
                                </table>
                            </div>
                        `;

                        Swal.fire({
                            title: 'QC Processing Complete',
                            html: tableHtml,
                            icon: "success",
                            buttonsStyling: false,
                            confirmButtonText: "Ok, got it!",
                            customClass: {
                                confirmButton: "btn fw-bold btn-success",
                            }
                        });
                    } else {
                        // Handle error response from our API
                        Swal.fire({
                            title: 'Processing Error',
                            text: data.message || data.error || 'Failed to process QC metrics',
                            icon: 'error',
                            confirmButtonText: 'Ok, got it!',
                            customClass: {
                                confirmButton: 'btn fw-bold btn-primary',
                            }
                        });
                    }
                })
                .catch(error => {
                    Swal.fire({
                        title: 'Error!',
                        text: 'An error occurred during processing: ' + error.message,
                        icon: 'error',
                        confirmButtonText: 'Ok, got it!',
                        customClass: {
                            confirmButton: 'btn fw-bold btn-primary',
                        }
                    });
                    console.error('Error:', error);
                });
            });
        });

    }

    // Public methods
    return {
        init: function () {
            initDatatable(handleInitialValue(),null,null,null,null,null);
            handleSearchDatatable();
            initToggleToolbar();
            handleFilterDatatable();
            handleDeleteRows();
            handleResetForm();
            handleFilter();
            handleResetFilter();
        }
    }
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesServerSide.init();
});
