"use strict";

// Class definition
var KTDatatablesServerSide = function () {
    // Shared variables
    var table;
    var dt;
    var filterPayment;

    // Private functions
    var initDatatable = function (filterSequencingRun,filterPatient,filterBarcode,filterBait,filterAreaType,filterNaType) {

        dt = $("#kt_datatable_example_1").DataTable({
            // searchDelay: 500,
            processing: true,
            serverSide: true,
            destroy: true,
            order: [[2, 'asc']],
            stateSave: false,
            select: {
                style: 'multi',
                selector: 'td:first-child input[type="checkbox"]',
                className: 'row-selected'
            },
            ajax: {
              url: "/sheet/filter_sheet",
              type: 'GET',
              data : {
                  "sequencing_run": filterSequencingRun,
                  "patient": filterPatient,
                  "barcode": filterBarcode,
                  "bait": filterBait,
                  "area_type": filterAreaType,
                  "na_type": filterNaType
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
                { data: 'patient' },
                { data: 'name' },
                { data: 'barcode_name' },
                { data: 'bait' },
                { data: 'na_type' },
                { data: 'area_type' },
                { data: 'matching_normal_sl' },
                { data: 'seq_run' },
                { data: 'fastq' },
                { data: 'path_fastq' },
                { data: 'bam' },
                { data: 'path_bam' },
                { data: 'bai' },
                { data: 'path_bai' },
            ],
            columnDefs: [
                {
                    targets: 0,
                    orderable: false,
                    render: function (data) {
                        return `
                            <div class="form-check form-check-sm form-check-custom form-check-solid">
                                <input class="form-check-input m-1" type="checkbox" value="${row['seq_run']}" />
                            </div>`;
                    }
                },

                {
                    targets: 1,
                    render: function (data, type, row) {
                        let namesList = [];
                        if (Array.isArray(row["patient"])) {
                            row["patient"].forEach(sqr => {
                                namesList.push(sqr.pat_id);
                            });
                        }
                        return namesList.join(", ");
                    }
                },
                {
                    targets: [9,10],
                    render: function (data, type, row) {

                        if (row["fastq"] !== "[]") {
                            return data;
                        } else {
                            return '';
                        }
                    }
                },
                {
                    targets: [11, 12, 13, 14],
                    render: function (data, type, row) {
                        if (row["fastq"] !== "[]") {
                            return '';
                        } else {
                            return data;
                        }
                    }
                },
            ],
            // Add data-filter attribute
            createdRow: function (row, data, dataIndex) {
                $(row).find('td:eq(4)').attr('data-filter', data.CreditCardType);
            }
        });

        table = dt.$;

        // Re-init functions on every table re-draw -- more info: https://datatables.net/reference/event/draw
        dt.on('draw', function () {

            handleResetFilter();
            handleDeleteRows();
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
        const filterButton = document.querySelector('[data-kt-docs-table-filter="filter"]');
        // Filter datatable on submit
        filterButton.addEventListener('click', function () {
          var sequencingRun = $('#id_sequencing_run').select2('data'); // Fetches the data objects for selected options
          var selectedSequencingRuns = sequencingRun.map(option => option.id); // Maps over the data objects to extract the ids

          var patient = document.getElementById("id_patient").value;
          var barcode = document.getElementById("id_barcode").value;
          var bait = document.getElementById("id_bait").value;
          var area_type = document.getElementById("id_area_type").value;
          var na_type = document.getElementById("id_na_type").value;

          initDatatable(selectedSequencingRuns,patient,barcode,bait,area_type,na_type);

        });
    }

    function getSelectedRows() {
        const container = document.querySelector('.table');
        const selectedRows = container.querySelectorAll('tbody [type="checkbox"]:checked');
        const selectedIds = [];

        selectedRows.forEach((p) => {
            // Select parent row
            const parent = p.closest('tr');
            // Get customer ID
            const id = parent.querySelector('input[type="checkbox"]').value;

            selectedIds.push(id);
        });

        return JSON.stringify(selectedIds);
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
                const customerName = parent.querySelectorAll('td')[2].innerText;

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
                            Swal.fire({
                                text: "You have deleted " + customerName + "!.",
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
    var handleResetFilter = () => {
        // Select reset button
        const resetButton = document.querySelector('[data-kt-docs-table-filter="reset"]');

        // Reset datatable
        resetButton.addEventListener('click', function () {
            // clean the selected sequencing runs
            document.getElementById("select2-id_sequencing_run-container").innerHTML = "";
            // clean the selected patient
            document.getElementById("select2-id_patient-container").innerHTML = "";
            document.getElementById("id_patient").value="";
            document.getElementById("id_barcode").value="";
            document.getElementById("id_bait").value="";
            document.getElementById("id_area_type").value="";
            document.getElementById("id_na_type").value="";

            initDatatable(null,null,null,null,null,null);
        });
    }


    var init_csv_button = function (){
        document.getElementById('export_to_csv').onclick = function(){
            console.log("")
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
            // Show page loading
            KTApp.showPageLoading();

            $.ajax({
                url: '/sheet/create_csv_sheet', // Replace with your actual URL
                type: 'GET',
                xhrFields: {
                    responseType: 'blob' // Important for handling binary data
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
                    link.download = filename || "seq_run_sheet.csv";
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
        };

    };

    var init_csv_button_2 = function (){
        document.getElementById('export_to_csv_individual').onclick = function(){
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

            // Show page loading
            KTApp.showPageLoading();
            var seq_run = document.getElementById('id_sequencing_run_report').value;

            $.ajax({
                url: '/sheet/sheet_seq_run', // Replace with your actual URL
                type: 'GET',
                data: {
                    "seq_run": seq_run
                },
                xhrFields: {
                    responseType: 'blob' // Important for handling binary data
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
                    link.download = filename || "seq_run_sheet.csv";
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
        };

    };

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

    // var handleAlternativeExport = () => {
    //     // event listener
    //     document.querySelector("button[name='alternative_export']").addEventListener("click", function () {
    //         exportTableToCSV("alternative_export.csv")
    //     });
    //
    //     function exportTableToCSV(filename) {
    //         var data = [];
    //
    //         // Add header
    //         var headers = [], headerCols = document.querySelectorAll("table thead tr th");
    //         for (var i = 1; i < headerCols.length; i++) {
    //             headers.push(headerCols[i].innerText.toLowerCase());
    //         }
    //         headers.unshift("no");
    //         data.push(headers.join("\t"));
    //         console.log(data);
    //         var rowNumber = 1;
    //         var rows = document.querySelectorAll("table tbody tr");
    //         for (var i = 0; i < rows.length; i++) {
    //             var row = [], cols = rows[i].querySelectorAll("td");
    //
    //             // exclude checked rows
    //             if (cols.length > 0 && !cols[0].querySelector('input[type="checkbox"]').checked) {
    //                 row.push(rowNumber);
    //                 rowNumber++;
    //                 for (var j = 1; j < cols.length; j++) {
    //                     row.push(cols[j].innerText);
    //                 }
    //                 data.push(row.join("\t"));
    //             }
    //         }
    //
    //         downloadCSV(data.join("\n"), filename);
    //     }
    //
    //     function downloadCSV(data, filename) {
    //         // Create a temporary link element
    //         var url = new Blob([data], {type: "text/csv"});
    //         var link = document.createElement("a");
    //         link.download = filename;
    //         link.href = window.URL.createObjectURL(url);
    //         link.style.display = "none";
    //
    //         // Append the link to the document body
    //         document.body.appendChild(link);
    //
    //         // Click the link programmatically to trigger the download
    //         link.click();
    //
    //         // Remove the link from the document body
    //         document.body.removeChild(link);
    //     }
    // }

    var handleAlternativeExport = function () {
        // Grab the table container
        const container = document.querySelector('.table');
        // All checkboxes inside the table
        const checkboxes = container.querySelectorAll('[type="checkbox"]');
        // Button that triggers the export
        const exportButton = document.querySelector("button[name='alternative_export']");

        // Example function to toggle toolbars
        function toggleToolbars() {
            // Your logic here for showing/hiding toolbars...
        }

        // Listen for checkbox clicks, then toggle toolbars
        checkboxes.forEach(c => {
            c.addEventListener('click', function () {
                setTimeout(function () {
                    toggleToolbars();
                }, 50);
            });
        });

        // ----------------------------------------------------------------
        // Define a function that performs the AJAX call for exporting rows
        // ----------------------------------------------------------------
        function exportSelectedRows() {
            // selectedRows should be an array of IDs you want to include
            // for your backend to process. Make sure this array is maintained
            // elsewhere based on which checkboxes are selected.
            $.ajax({
                type: "GET",
                url: "/sheet/sheet_multiple",
                data: {
                    "selected_ids": getSelectedRows(),
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    swal("Error deleting!", "Please try again", "error");
                }
            }).done(function (result) {
                if (result.deleted) {
                    Swal.fire({
                        text: "Sheet created successfully.",
                        icon: "info",
                        buttonsStyling: false,
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                            confirmButton: "btn fw-bold btn-success",
                        }
                    }).then(function () {
                        // Clear selected rows
                        selectedRows = [];
                        // Refresh DataTable if needed
                        dt.draw();
                    });
                } else {
                    Swal.fire({
                        text: `Sheet cannot be created!\n${result.message}`,
                        icon: "error",
                        buttonsStyling: false,
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                            confirmButton: "btn fw-bold btn-success",
                        }
                    });
                }
            });

            // Uncheck the header checkbox after export
            const headerCheckbox = container.querySelector('[type="checkbox"]');
            if (headerCheckbox) {
                headerCheckbox.checked = false;
            }
        }

        // ---------------------------------------------------------
        // Wire up the export button to call exportSelectedRows()
        // ---------------------------------------------------------
        if (exportButton) {
            exportButton.addEventListener("click", function () {
                exportSelectedRows();
            });
        }
    };

    // Public methods
    return {
        init: function () {
            initDatatable(null, null, null, null, null, null);
            handleSearchDatatable();
            handleFilterDatatable();
            handleResetFilter();
            handleDeleteRows();
            handleAlternativeExport();
            init_csv_button();
        }
    }
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesServerSide.init();
});
