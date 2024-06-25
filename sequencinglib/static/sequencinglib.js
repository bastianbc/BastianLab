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
              url: '/sequencinglib/filter_sequencinglibs',
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
                { data: 'nmol' },
                { data: 'buffer',
                  render: function (val, type, row) {
                    return row["buffer_label"];
                  }
                },
                { data: 'pdf' },
                { data: 'num_capturedlibs' },
                { data: 'num_sequencingruns' },
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
                    targets: 5,
                    orderable: false,
                    render: function (data, type, row) {
                        if (data) {
                          let link = row["pdf"];
                          return `
                            <a href="${ link }" target="blank">
                              <span class="svg-icon svg-icon-muted svg-icon-2hx"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                              <path opacity="0.3" d="M4.425 20.525C2.525 18.625 2.525 15.525 4.425 13.525L14.825 3.125C16.325 1.625 18.825 1.625 20.425 3.125C20.825 3.525 20.825 4.12502 20.425 4.52502C20.025 4.92502 19.425 4.92502 19.025 4.52502C18.225 3.72502 17.025 3.72502 16.225 4.52502L5.82499 14.925C4.62499 16.125 4.62499 17.925 5.82499 19.125C7.02499 20.325 8.82501 20.325 10.025 19.125L18.425 10.725C18.825 10.325 19.425 10.325 19.825 10.725C20.225 11.125 20.225 11.725 19.825 12.125L11.425 20.525C9.525 22.425 6.425 22.425 4.425 20.525Z" fill="currentColor"/>
                              <path d="M9.32499 15.625C8.12499 14.425 8.12499 12.625 9.32499 11.425L14.225 6.52498C14.625 6.12498 15.225 6.12498 15.625 6.52498C16.025 6.92498 16.025 7.525 15.625 7.925L10.725 12.8249C10.325 13.2249 10.325 13.8249 10.725 14.2249C11.125 14.6249 11.725 14.6249 12.125 14.2249L19.125 7.22493C19.525 6.82493 19.725 6.425 19.725 5.925C19.725 5.325 19.525 4.825 19.125 4.425C18.725 4.025 18.725 3.42498 19.125 3.02498C19.525 2.62498 20.125 2.62498 20.525 3.02498C21.325 3.82498 21.725 4.825 21.725 5.925C21.725 6.925 21.325 7.82498 20.525 8.52498L13.525 15.525C12.325 16.725 10.525 16.725 9.32499 15.625Z" fill="currentColor"/></svg>
                              </span>
                            </a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 6,
                    className: 'text-center',
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
                    targets: 7,
                    className: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let id = row["id"];
                          return `
                              <a href="/sequencingrun?model=seqlib&id=${id}&initial=true">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 8,
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
                                    <a href="/sequencinglib/edit/`+ row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        Edit
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item">
                                    <a href="javascript:;" class="menu-link px-3 detail-link" data-kt-docs-table-filter="detail_row">
                                        Used Library(s)
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item">
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
                    url: "/sequencinglib/check_can_deleted_async",
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
                                      text: name + " could not deleted.",
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
                                    text: "Sequencing Library deleted succesfully.",
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

      var bufferOptions = [];

      Promise.all([

        getBufferOptions()

      ]).then(function () {

        editor = new $.fn.dataTable.Editor({
          ajax: {
            url: "/sequencinglib/edit_sequencinglib_async",
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
                 label: "NMol:",
                 name: "nmol",
             }, {
                 label: "BUffer:",
                 name: "buffer",
                 type: "select",
                 options: bufferOptions
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

     function getBufferOptions() {

       $.ajax({
           url: "/sequencinglib/get_buffers",
           type: "GET",
           async: false,
           success: function (data) {
            // var options = [];
            data.forEach((item, i) => {

              bufferOptions.push({
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

    var handleSelectedRows = ((e) => {

      const container = document.querySelector('.table');

      var modal = new bootstrap.Modal(document.getElementById("modal_sequencingrun_options"));
      // var modal_2 = new bootstrap.Modal(document.getElementById("add_to_seq_run"));

      function initModal() {

        var isInit = false;

        function resetForm() {

          document.getElementById("frm_creation_options").reset();

        }

        document.getElementById("modal_sequencingrun_options").addEventListener('show.bs.modal', function(e){

          initEvents();

        });

        document.getElementById("modal_sequencingrun_options").addEventListener('hide.bs.modal', function(e){

          resetForm();

        });

      }

      function initEvents() {

        document.getElementById("id_prefix").addEventListener("keyup", function () {

          this.value = this.value.toLocaleUpperCase();

        });

        document.getElementById("btn_continue").addEventListener('click', function () {

          $.ajax({
            type: "GET",
            url: "/sequencingrun/new_async",
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
                generate_sheet(result.id);
              });
            }
            else {
              Swal.fire({
                  text: "Sequencing Library(s) could not created.",
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
                            url: "/sequencinglib/batch_delete",
                            data: {
                              "selected_ids": JSON.stringify(selectedRows),
                            },
                            error: function (xhr, ajaxOptions, thrownError) {
                                swal("Error deleting!", "Please try again", "error");
                            }
                        }).done(function (result) {
                            if (result.deleted) {
                              Swal.fire({
                                  text: "Sequencing Library(s) deleted succesfully.",
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
                                  text: "Sequencing Library(s) could not deleted!",
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

      function wait(ms){
           var start = new Date().getTime();
           var end = start;
           while(end < start + ms) {
             end = new Date().getTime();
          }
        }

      function generate_sheet(id){
          $.ajax({
                url: '/sheet/sheet_seq_run/' + id,
                type: 'GET',
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

                    // Create a new Blob object using the response data of the xhr request
                    var blob = new Blob([data], { type: 'text/csv' });

                    // Create a link element, use it to download the blob, and remove it
                    var link = document.createElement('a');
                    link.href = window.URL.createObjectURL(blob);
                    link.download = filename || "seq_run_sheet.csv"; // Provide a default filename if none is found
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
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
      }

      //create_sequencing_run
      function initCreateSequencingRun(){

        document.getElementById("btn_add_continue").addEventListener('click', function () {
            var selectElement = document.getElementById("id_seq_run").value;
            const modalElement = document.getElementById("add_to_seq_run"); // Replace "currentlyOpenModalID" with the ID of the modal that might be open
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
          $.ajax({
            url: "/sequencingrun/add_async",
            type: "GET",
            data: {
              "id": selectElement,
              "selected_ids": JSON.stringify(selectedRows),
              "options": getCreationOptions()
            },
          }).done(function(result) {

            if (result.success) {
              Swal.fire({
                  text: "Sequencing Library(s) added succesfully.",
                  icon: "info",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                      confirmButton: "btn fw-bold btn-success",
                  }
              }).then(function(){
                  generate_sheet(selectElement);
              });
            }
            else {
              Swal.fire({
                  text: `Sequencing Library(s) could not added ${result.message}`,
                  icon: "error",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                      confirmButton: "btn fw-bold btn-danger",
                  }
              }).then(function(){
                  modal.show();
                  modal.hide();
                  dt.draw();
              });
            }
          });

        });


        document.getElementById("create_sequencing_run").addEventListener('click', function (e) {
        const container = document.querySelector('.table');
        const selectedRows = container.querySelectorAll('[type="checkbox"]:checked');
        const selectedIds = [];
        selectedRows.forEach((p) => {
          const parent = p.closest('tr');
          const id = parent.querySelector('input[type=checkbox]').value;
          selectedIds.push(id)
        });
        Swal.fire({
              title: "<h3 style='color:dodgerblue'>" + "Add to an existing Sequencing Run?" + "</h3>",
              showDenyButton: true,
              confirmButtonText: "Yes Add!",
              denyButtonText: "No, Create New One",
              icon: "question",
              buttonsStyling: true,
              customClass: {
                  confirmButton: "btn fw-bold btn-success",
                  denyButton: "btn fw-bold btn-primary",
                  title: "text-light"
              }
          }).then((result) => {
              /* Read more about isConfirmed, isDenied below */
              if (result.isConfirmed) {

                var modal = new bootstrap.Modal(document.getElementById("add_to_seq_run"));
                modal.show();
                // location.reload()
              } else if (result.isDenied){
                  var modal = new bootstrap.Modal(document.getElementById("modal_sequencingrun_options"));
                  modal.show();
                  modal.hide();
              }
            });
        });

    }

      function initSequencingSheetModal() {
          const stepper = new KTStepper(document.getElementById("modal_stepper"));
          const exportButton = document.querySelector('button[name="btn_export_sheet"]');

          if (Object.keys(stepper).length !== 0) { //isEmpty

            stepper.on("kt.stepper.next", function (stepper) {
                stepper.goNext(); // go next step

                if (stepper.currentStepIndex === 2) {
                    exportButton.classList.remove("d-none");
                }
            });

            stepper.on("kt.stepper.previous", function (stepper) {
                stepper.goPrevious(); // go previous step
                if (stepper.currentStepIndex === 1) {
                    exportButton.classList.add("d-none");
                }
            });

          }
      }

      return {
        init: function () {
          initModal(), handleBatchDelete(), uncheckedFirstCheckBox(), initCreateSequencingRun(), initSequencingSheetModal();
        },
      }

    })();

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
        listEl.setAttribute('data-target_vol', data[0].target_vol);

        var total_persentage = 100;
        var totalVolume = 0;

        for (var i = 0; i < data.length; i++) {

          totalVolume += data[i].volume;

        }
        for (var i = 0; i < data.length; i++) {
          var p = 0.00;
          var v = 0.00;

          v = data[i].volume;
          p = ((v / totalVolume) * 100) || 0;

          var row = `<div class="row mb-1 detail-row">
              <div class="col-2 align-self-center" data-id="${ data[i].captured_lib }"><a href="/capturedlib/edit/${ data[i].captured_lib }">${ data[i].name }</a></div>
              <div class="col-1 align-self-center">${ data[i].frag_size }</div>
              <div class="col-2 align-self-center text-center">${ data[i].vol_remain }</div>
              <div class="col-1 align-self-center text-center">${ data[i].conc }</div>
              <div class="col-2 align-self-center text-center">${ data[i].nm }</div>
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

        var totalVolume = parseFloat(document.querySelector("#total_volume").value);

        var targetVol = parseFloat(document.querySelector(".list-body").getAttribute("data-target_vol"));

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

          return parseFloat(document.getElementById("total_percentage").value) == 100;

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
                  text: "Captured Library(s) updated succesfully.",
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
                  text: "Captured Library(s) could not updated.",
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
