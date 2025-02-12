"use strict";

// Class definition
var KTDatatablesServerSide = function () {
    // Shared variables
    var table;
    var dt;
    var filterPayment;
    var selectedRows = [];

    // Private functions
    var initDatatable = function () {

        $.fn.dataTable.moment('MM/DD/YYYY');

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
                keys: [9],
                editOnFocus: true
            },
            ajax: {
                url: '/analysisrun/filter_analysisruns',
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
                { data: 'pipeline' },
                { data: 'genome' },
                { data: 'sheet' },
                {
                    data: 'date',
                    render: function (data) {
                        return moment(data).format('MM/DD/YYYY');
                    }
                },
                { data: 'status' },
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
                    targets: 7,
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
                            <div class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-600 menu-state-bg-light-primary fw-bold fs-7 w-200px py-4" data-kt-menu="true">
                                <!--begin::Menu item-->
                                <div class="menu-item">
                                    <a href="javascript:;" class="menu-link variants-link text-start" data-kt-docs-table-filter="detail_row">
                                        Get Variants
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                            <div class="menu-item">
                                <a href="javascript:;" class="menu-link check-file-link text-start"  data-ar-name="${row.name}">
                                    Import CNS
                                </a>
                            </div>
                            <!--end::Menu item-->


                                <!--begin::Menu item-->
                                <div class="menu-item">
                                    <a href="#` + row["id"] + `" class="menu-link px-3" data-kt-docs-table-filter="delete_row">
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
            if (selectedRows.indexOf(c.value) > -1) {
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
                    url: "/analysisrun/check_can_deleted_async",
                    type: "GET",
                    data: {
                        "id": id,
                    },
                    async: false,
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
                                    headers: { 'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value },
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
                                    }).then(function () {

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

    var handleSelectedRows = ((e) => {

        const container = document.querySelector('.table');

        function uncheckedFirstCheckBox() {

            dt.on('draw', function () {

                // Remove header checked box
                const headerCheckbox = container.querySelectorAll('[type="checkbox"]')[0];
                headerCheckbox.checked = false;

            });

        }

        function handleBatchDelete() {

            // Select elements
            const deleteSelected = document.querySelector('[data-kt-docs-table-select="delete_selected"]');

            // Deleted selected rows
            deleteSelected.addEventListener('click', function () {
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
                                url: "/analysisrun/batch_delete",
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
                                    }).then(function () {
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



        return {
            init: function () {
                handleBatchDelete(), uncheckedFirstCheckBox();
            }
        }

    })();

    var initRowActions = () => {

        document.querySelectorAll(".variants-link").forEach((item, i) => {
            item.addEventListener("click", function (e) {
                const parent = e.target.closest('tr');
                var analysisRunName = parent.querySelectorAll('td')[1].innerText;

                // Show loading message
                Swal.fire({
                    title: 'Processing...',
                    text: 'Importing variant files',
                    icon: 'info',
                    allowOutsideClick: false,
                    showConfirmButton: false,
                });

                $.ajax({
                    url: `/variant/import_variants/${analysisRunName}`,
                    type: "GET",
                }).done(function (data) {
                    // Close loading dialog
                    Swal.close();

                    if (data.success) {
                        let html = `
                            <div class="mt-3">
                                <p><strong>Process Summary:</strong></p>
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Folder</th>
                                            <th>Success</th>
                                            <th>Failed</th>
                                            <th>Objects Created</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${data.summary.map(stat => `
                                            <tr>
                                                <td>${stat.folder_name}</td>
                                                <td>${stat.success_count}</td>
                                                <td>${stat.failed_count}</td>
                                                <td>${stat.objects_created}</td>
                                            </tr>
                                        `).join('')}
                                        <tr class="table-active fw-bold">
                                            <td>${data.total.folder_name}</td>
                                            <td>${data.total.success_count}</td>
                                            <td>${data.total.failed_count}</td>
                                            <td>${data.total.objects_created}</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        `;

                        Swal.fire({
                            html: html,
                            icon: "success",
                            buttonsStyling: false,
                            confirmButtonText: "Ok, got it!",
                            customClass: {
                                confirmButton: "btn fw-bold btn-success",
                                htmlContainer: 'text-start'
                            }
                        });
                    } else {
                        let html = `<p class="text-center">${data.error}</p>`;

                        Swal.fire({
                            html: html,
                            icon: "error",
                            buttonsStyling: false,
                            confirmButtonText: "Ok, anladım!",
                            customClass: {
                                confirmButton: "btn fw-bold btn-primary",
                                htmlContainer: 'text-start'
                            }
                        });
                    }

                }).fail(function (jqXHR, textStatus, errorThrown) {
                    Swal.close();
                    Swal.fire({
                        text: "An error occurred during import",
                        icon: "error",
                        buttonsStyling: false,
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                            confirmButton: "btn fw-bold btn-primary",
                        }
                    });
                });
            });
        });

        document.querySelectorAll(".check-file-link").forEach(function (element) {
            element.addEventListener("click", function () {
                const variantType = this.getAttribute('data-variant-type');
                const arName = this.getAttribute('data-ar-name');

                // Show loading message
                Swal.fire({
                    title: 'Processing...',
                    text: 'Checking for folder and file existence',
                    icon: 'info',
                    allowOutsideClick: false,
                    showConfirmButton: false,
                });

                // Send AJAX request to server
                fetch(`import_cns/${arName}`,
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            let tableHtml = `
                            <div class="mt-3">
                            <p><strong>Variant files imported successfully.</strong></p>
                            <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th class="text-start" style="border: 1px solid #4a4a4a; white-space: nowrap;">Folder Name</th>
                                    <th class="text-start" style="border: 1px solid #4a4a4a; white-space: nowrap;">Success Count</th>
                                    <th class="text-start" style="border: 1px solid #4a4a4a; white-space: nowrap;">Failed Count</th>
                                    <th class="text-start" style="border: 1px solid #4a4a4a; white-space: nowrap;">Objects Created</th> 
                                </tr>
                            </thead>
                            <tbody>
                        `;

                            data.summary.forEach(item => {
                                console.log(item);
                                if (item.folder_name !== 'Total') {
                                    tableHtml += `
                                    <tr>
                                        <td class="text-start" style="border: 1px solid #4a4a4a;">${item.folder_name}</td>
                                        <td class="text-center" style="border: 1px solid #4a4a4a;">${item.success_count}</td>
                                        <td class="text-center" style="border: 1px solid #4a4a4a;">${item.failed_count}</td>
                                        <td class="text-center" style="border: 1px solid #4a4a4a;">${item.objects_created}</td>
                                    </tr>
                                `;
                                }
                            });

                            // Total row
                            const total = data.summary.find(item => item.folder_name === 'Total');
                            tableHtml += `
                                    <tr class="table-active">  
                                        <td class="text-start" style="border: 1px solid #4a4a4a;"><strong>${total.folder_name}</strong></td>
                                        <td class="text-center" style="border: 1px solid #4a4a4a;"><strong>${total.success_count}</strong></td>
                                        <td class="text-center" style="border: 1px solid #4a4a4a;"><strong>${total.failed_count}</strong></td>
                                        <td class="text-center" style="border: 1px solid #4a4a4a;"><strong>${total.objects_created}</strong></td>
                                        <td></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        `;

                            Swal.fire({
                                html: tableHtml,
                                text: "Variant files imported successfully.",
                                icon: "info",
                                buttonsStyling: false,
                                confirmButtonText: "Ok, got it!",
                                customClass: {
                                    confirmButton: "btn fw-bold btn-success",
                                }
                            });

                        } else {
                            Swal.fire({
                                title: 'Error!',
                                text: data.error,
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
                            text: 'An error occurred during processing.',
                            icon: 'error',
                            confirmButtonText: 'Ok, got it!',
                            customClass: {
                                confirmButton: 'btn fw-bold btn-primary',
                            }
                        });
                        console.error('Error:', error);
                    });
            })
        });

    }


    // Public methods
    return {
        init: function () {
            initDatatable();
            handleSearchDatatable();
            initToggleToolbar();
            handleFilterDatatable();
            handleDeleteRows();
            handleResetForm();

        }
    }
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesServerSide.init();
});
