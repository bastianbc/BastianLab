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
    var initDatatable = function (initialValue) {

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
              keys: [ 6 ],
              editor: editor,
              editOnFocus: true
            },
            ajax: {
              url: '/sequencingfile/filter_sequencingfilesets',
              type: "GET",
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
              { data: 'set_id'},
              { data: 'prefix' },
              { data: 'sample_lib' },
              { data: 'sequencing_run' },
              { data: 'num_sequencing_files'},
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
                    orderable: false,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let set_id = row["set_id"];
                          return `
                              <a href="/sequencingfile?initial=${set_id}">${data}</a>`;
                        }
                        return data;
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
                                    <a href="/sequencingfile/sequencingfileset/edit/` + row["set_id"] + `" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        Edit
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/sequencingfile/sequencingfileset/delete/` + row["set_id"] +`" class="menu-link px-3" data-kt-docs-table-filter="delete_row">
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

        const filterButton = document.querySelector('[data-kt-docs-table-filter="filter"]');

        // Filter datatable on submit
        filterButton.addEventListener('click', function () {



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
                    url: "/sequencingfile/check_can_deleted_async_set",
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
                                    text: "Sequencing file set deleted succesfully.",
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

      const container = document.querySelector('.table');

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
                            url: "/sequencingfile/sequencingfileset/batch_delete",
                            data: {
                              "selected_ids": getSelectedRows(),
                            },
                            error: function (xhr, ajaxOptions, thrownError) {
                                swal("Error deleting!", "Please try again", "error");
                            }
                        }).done(function (result) {
                            if (result.deleted) {
                              Swal.fire({
                                  text: "Sequencing File Set(s) deleted succesfully.",
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
                                  text: "Sequencing File Set(s) could not be deleted!",
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
                        text: "Selected sequencing file set could not be deleted.",
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
          handleBatchDelete(), uncheckedFirstCheckBox();
        }
      }

    })();

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
            initDatatable( handleInitialValue() );
            handleSearchDatatable();
            // initToggleToolbar();
            // handleFilterDatatable();
            // handleDeleteRows();
            // handleResetForm();
            handleSelectedRows.init();
            // initEditor();
        }
    }
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesServerSide.init();
});
