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
            order: [[7, 'desc']],
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
            ajax: '/blocks/filter_blocks',
            columns: [
              { data: null },
              { data: 'name' },
              { data: 'project' },
              { data: 'patient' },
              { data: 'diagnosis' },
              { data: 'body_site' },
              { data: 'thickness' },
              { data: 'date_added',
                render: function (data) {
                  return moment(data).format('MM/DD/YYYY');
                }
              },
              { data: 'num_areas' },
            ],
            columnDefs: [
                {
                    targets: 0,
                    orderable: false,
                    render: function (data) {
                        return `
                            <div class="form-check form-check-sm form-check-custom form-check-solid">
                                <input class="form-check-input" type="checkbox" value="${data['bl_id']}" />
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
                    targets: 8,
                    orderable: false,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let bl_id = row["bl_id"];
                          return `
                              <a href="/areas?initial=${bl_id}">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 9,
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
                            <div class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-600 menu-state-bg-light-primary fw-bold fs-7 w-150px py-4" data-kt-menu="true">
                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/blocks/edit/`+ row["bl_id"] +`" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        Edit
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                  <a href="javascript:;" class="menu-link px-3" data-block_id=` + row["bl_id"] + ` data-block_name=` + row["name"] + ` data-bs-toggle="modal" data-bs-target="#modal_area_options">
                                      Create Area(s)
                                  </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/blocks/delete/` + row["bl_id"] +`" class="menu-link px-3" data-kt-docs-table-filter="delete_row">
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
                const blockName = parent.querySelectorAll('td')[1].innerText;

                // SweetAlert2 pop up --- official docs reference: https://sweetalert2.github.io/
                Swal.fire({
                    text: "Are you sure you want to delete " + blockName + "?",
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
                            text: "Deleting " + blockName,
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
                                    swal("Done!", "It was succesfully deleted!", "success");
                                    dt.draw();
                                },
                                error: function (xhr, ajaxOptions, thrownError) {
                                    swal("Error deleting!", "Please try again", "error");
                                }
                            });
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
                            url: "/blocks/batch_delete",
                            data: {
                              "selected_ids": getSelectedRows(),
                            },
                            error: function (xhr, ajaxOptions, thrownError) {
                                swal("Error deleting!", "Please try again", "error");
                            }
                        }).done(function (result) {
                            if (result.deleted) {
                              Swal.fire({
                                  text: "Block(s) was deleted succesfully.",
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
                                  text: "Block(s) wasn't deleted!",
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

    var handleSelectedRows = (function (e) {

      var modal = new bootstrap.Modal(document.getElementById("modal_area_options"));

      var selectedItem = {};

      function initModal() {
        var isInit = false;

        function resetForm() {

          document.getElementById("frm_creation_options").reset();

        }

        document.getElementById("modal_area_options").addEventListener('show.bs.modal', function(e){

          selectedItem = {
              "id": e.relatedTarget.getAttribute("data-block_id"),
              "name": e.relatedTarget.getAttribute("data-block_name")
          };

          if (!isInit) {

            isInit = true;

            initEvents();
          }

        });

        document.getElementById("modal_area_options").addEventListener('hide.bs.modal', function(e){

          resetForm();

        });

      }

      function initEvents() {

        document.getElementById('btn_continue').addEventListener('click', function () {

          $.ajax({
            type: "GET",
            url: "/areas/add_area_to_block_async",
            data: {
              "block_id": selectedItem["id"],
              "options": getCreationOptions()
            },
          }).done(function(result) {
            if (result.success) {
              Swal.fire({
                  text: "The areas for "+ selectedItem["name"] +" were created",
                  icon: "info",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                      confirmButton: "btn fw-bold btn-success",
                  }
              });
            }
            else {
              Swal.fire({
                  text: "Areas(s) was not created.",
                  icon: "error",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                      confirmButton: "btn fw-bold btn-danger",
                  }
              });
            }

            modal.hide();

            dt.draw();

          });

        });

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

      const btnAddBlockToProject = document.querySelector('[data-kt-docs-table-select="event_add_block_to_project"]');

      const btnRemoveBlockFromProject = document.querySelector('[data-kt-docs-table-select="event_remove_block_from_project"]');

      function getCreationOptions() {

        var data = new FormData(document.getElementById('frm_creation_options'));
        var options = Object.fromEntries(data.entries());

        return JSON.stringify(options);
      }

      if (btnAddBlockToProject) {

        btnAddBlockToProject.addEventListener('click', function () {

          $.ajax({
            type: "GET",
            url: "/blocks/add_block_to_project_async",
            data: {
              "selected_ids": getSelectedRows(),
              "project_id": this.getAttribute('data-project_id')
            },
          }).done(function(result) {
            if (result.success) {
              Swal.fire({
                  text: "Block(s) was added succesfully.",
                  icon: "info",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                      confirmButton: "btn fw-bold btn-success",
                  }
              }).then(function(){
                window.location.href = "/projects";
              });
            }
            else {
              Swal.fire({
                  text: "Block(s) was not added.",
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

      if (btnRemoveBlockFromProject) {

        btnRemoveBlockFromProject.addEventListener('click', function () {

          $.ajax({
            type: "GET",
            url: "/blocks/remove_block_from_project_async",
            data: {
              "selected_ids": getSelectedRows(),
              "project_id": this.getAttribute('data-project_id')
            },
          }).done(function(result) {
            if (result.success) {
              Swal.fire({
                  text: "Block(s) was removed succesfully.",
                  icon: "info",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                      confirmButton: "btn fw-bold btn-success",
                  }
              }).then(function(){
                window.location.href = "/projects";
              });
            }
            else {
              Swal.fire({
                  text: "Block(s) was not removed.",
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

      return {
        init: function () {
          initModal();
        }
      }

    })();

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
          url: "/blocks/edit_block_async",
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
           },{
               label: "Diagnosis:",
               name: "diagnosis"
           },{
               label: "Body Site:",
               name: "body_site"
           },{
               label: "Thickness:",
               name: "thickness"
           }
       ],
       formOptions: {
          inline: {
            onBlur: 'submit'
          }
       }
     });


     $('.table').on( 'click', 'tbody td:not(:first-child)', function (e) {
       editor.inline( dt.cell( this ).index(), {
           onBlur: 'submit'
       });
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

    // Public methods
    return {
        init: function () {
            initDatatable( handleInitialValue() );
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
