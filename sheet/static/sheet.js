"use strict";

// Class definition
var KTDatatablesServerSide = function () {
    // Shared variables
    var table;
    var dt;
    var filterPayment;

    // Private functions
    var initDatatable = function () {
        dt = $("#kt_datatable_example_1").DataTable({
            // searchDelay: 500,
            processing: true,
            serverSide: true,
            pageLength: 100,
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
                { data: 'barcode' },
                { data: 'bait' },
                { data: 'na_type' },
                { data: 'area_type' },
                { data: 'matching_normal_sl' },
                { data: 'seq_run' },
                { data: 'files' },
                { data: 'path' },
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
                    targets: 1,
                    render: function (data, type, row) {
                        let namesList = [];
                        if (Array.isArray(row["patient"])) {
                            row["patient"].forEach(sqr => {
                                namesList.push(sqr.pat_id);
                            });
                        }
                        // This will return the names list. Adjust based on your requirements
                        return namesList.join(", ");
                    }
                },
                {
                    targets: 4,
                    render: function (data, type, row) {
                        let namesList = [];
                        if (Array.isArray(row["bait"])) {
                            row["bait"].forEach(sqr => {
                                namesList.push(sqr.pat_id);
                            });
                        }
                        // This will return the names list. Adjust based on your requirements
                        return namesList.join(", ");
                    }
                },
                {
                    targets: -2,
                    render: function (data, type, row) {
                        let namesList = [];
                        if (Array.isArray(row["files"])) {
                            row["files"].forEach(sqr => {
                                namesList.push(sqr.name);
                            });
                        }
                        // This will return the names list. Adjust based on your requirements
                        return namesList.join(", ");
                    }
                },
                {
                    targets: -3,
                    render: function (data, type, row) {
                        let namesList = [];
                        if (Array.isArray(row["seq_run"])) {
                            row["seq_run"].forEach(sqr => {
                                namesList.push(sqr.name);
                            });
                        }
                        // This will return the names list. Adjust based on your requirements
                        return namesList.join(", ");
                    }
                },
                {
                    targets: -4,
                    render: function (data, type, row) {
                        let namesList = [];
                        if (Array.isArray(row["matching_normal_sl"])) {
                            row["matching_normal_sl"].forEach(sl => {
                                namesList.push(sl.name);
                            });
                        }
                        // This will return the names list. Adjust based on your requirements
                        return namesList.join(", ");
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
            // initToggleToolbar();
            // toggleToolbars();
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
    // var handleFilterDatatable = () => {
    //     // Select filter options
    //     filterPayment = document.querySelectorAll('[data-kt-docs-table-filter="payment_type"] [name="payment_type"]');
    //     const filterButton = document.querySelector('[data-kt-docs-table-filter="filter"]');
    //
    //     // Filter datatable on submit
    //     filterButton.addEventListener('click', function () {
    //         // Get filter values
    //         let paymentValue = '';
    //
    //         // Get payment value
    //         filterPayment.forEach(r => {
    //             if (r.checked) {
    //                 paymentValue = r.value;
    //             }
    //
    //             // Reset payment value if "All" is selected
    //             if (paymentValue === 'all') {
    //                 paymentValue = '';
    //             }
    //         });
    //
    //         // Filter datatable --- official docs reference: https://datatables.net/reference/api/search()
    //         dt.search(paymentValue).draw();
    //     });
    // }

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
    // var handleResetForm = () => {
    //     // Select reset button
    //     const resetButton = document.querySelector('[data-kt-docs-table-filter="reset"]');
    //
    //     // Reset datatable
    //     resetButton.addEventListener('click', function () {
    //         // Reset payment type
    //         filterPayment[0].checked = true;
    //
    //         // Reset datatable --- official docs reference: https://datatables.net/reference/api/search()
    //         dt.search('').draw();
    //     });
    // }

    // // Init toggle toolbar
    // var initToggleToolbar = function () {
    //     // Toggle selected action toolbar
    //     // Select all checkboxes
    //     const container = document.querySelector('#kt_datatable_example_1');
    //     const checkboxes = container.querySelectorAll('[type="checkbox"]');
    //
    //     // Select elements
    //     const deleteSelected = document.querySelector('[data-kt-docs-table-select="delete_selected"]');
    //     // Toggle delete selected toolbar
    //     checkboxes.forEach(c => {
    //         // Checkbox on click event
    //         c.addEventListener('click', function () {
    //             setTimeout(function () {
    //                 toggleToolbars();
    //             }, 50);
    //         });
    //     });
    //
    //     // Deleted selected rows
    //     deleteSelected.addEventListener('click', function () {
    //         // SweetAlert2 pop up --- official docs reference: https://sweetalert2.github.io/
    //         Swal.fire({
    //             text: "Are you sure you want to delete selected customers?",
    //             icon: "warning",
    //             showCancelButton: true,
    //             buttonsStyling: false,
    //             showLoaderOnConfirm: true,
    //             confirmButtonText: "Yes, delete!",
    //             cancelButtonText: "No, cancel",
    //             customClass: {
    //                 confirmButton: "btn fw-bold btn-danger",
    //                 cancelButton: "btn fw-bold btn-active-light-primary"
    //             },
    //         }).then(function (result) {
    //             if (result.value) {
    //                 // Simulate delete request -- for demo purpose only
    //                 Swal.fire({
    //                     text: "Deleting selected customers",
    //                     icon: "info",
    //                     buttonsStyling: false,
    //                     showConfirmButton: false,
    //                     timer: 2000
    //                 }).then(function () {
    //                     Swal.fire({
    //                         text: "You have deleted all selected customers!.",
    //                         icon: "success",
    //                         buttonsStyling: false,
    //                         confirmButtonText: "Ok, got it!",
    //                         customClass: {
    //                             confirmButton: "btn fw-bold btn-primary",
    //                         }
    //                     }).then(function () {
    //                         // delete row data from server and re-draw datatable
    //                         dt.draw();
    //                     });
    //
    //                     // Remove header checked box
    //                     const headerCheckbox = container.querySelectorAll('[type="checkbox"]')[0];
    //                     headerCheckbox.checked = false;
    //                 });
    //             } else if (result.dismiss === 'cancel') {
    //                 Swal.fire({
    //                     text: "Selected customers was not deleted.",
    //                     icon: "error",
    //                     buttonsStyling: false,
    //                     confirmButtonText: "Ok, got it!",
    //                     customClass: {
    //                         confirmButton: "btn fw-bold btn-primary",
    //                     }
    //                 });
    //             }
    //         });
    //     });
    // }

    // // Toggle toolbars
    // var toggleToolbars = function () {
    //     // Define variables
    //     const container = document.querySelector('#kt_datatable_example_1');
    //     const toolbarBase = document.querySelector('[data-kt-docs-table-toolbar="base"]');
    //     const toolbarSelected = document.querySelector('[data-kt-docs-table-toolbar="selected"]');
    //     const selectedCount = document.querySelector('[data-kt-docs-table-select="selected_count"]');
    //
    //     // Select refreshed checkbox DOM elements
    //     const allCheckboxes = container.querySelectorAll('tbody [type="checkbox"]');
    //
    //     // Detect checkboxes state & count
    //     let checkedState = false;
    //     let count = 0;
    //
    //     // Count checked boxes
    //     allCheckboxes.forEach(c => {
    //         if (c.checked) {
    //             checkedState = true;
    //             count++;
    //         }
    //     });
    //
    //     // Toggle toolbars
    //     if (checkedState) {
    //         selectedCount.innerHTML = count;
    //         toolbarBase.classList.add('d-none');
    //         toolbarSelected.classList.remove('d-none');
    //     } else {
    //         toolbarBase.classList.remove('d-none');
    //         toolbarSelected.classList.add('d-none');
    //     }
    // }
    var init_csv_button = function (){
        document.getElementById('export_to_csv').onclick = function(){
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
    // Public methods
    return {
        init: function () {
            initDatatable();
            handleSearchDatatable();
            // initToggleToolbar();
            // handleFilterDatatable();
            handleDeleteRows();
            // handleResetForm();
            init_csv_button();
        }
    }
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesServerSide.init();
});
