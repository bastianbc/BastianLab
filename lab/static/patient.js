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
    var initDatatable = function (initialValue, race, sex, dob) {

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
              url: '/lab/filter_patients',
              type: 'GET',
              data:{
                "race": race,
                "sex": sex,
                "dob": dob,
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
                { data: 'pat_id' },
                { data: 'source' },
                { data: 'sex' ,
                  render: function (val, type, row) {
                    return row["sex_label"];
                  }
                },
                { data: 'race' ,
                  render: function (val, type, row) {
                    return row["race_label"];
                  }
                },
                { data: 'date_added',
                  render: function (data) {
                    return moment(data).format('MM/DD/YYYY');
                  }
                },
                { data: 'num_blocks' },
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
                    targets: 6,
                    orderable: false,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let id = row["id"];
                          return `
                              <a href="/blocks?model=patient&id=${id}&initial=true">${data}</a>`;
                        }
                        return data;
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
                            <div class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-600 menu-state-bg-light-primary fw-bold fs-7 w-150px py-4" data-kt-menu="true">
                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/lab/edit/`+ row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        Edit
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/blocks?model=patient&id=`+ row["id"] +`&initial=false" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        Add Block(s)
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/blocks?model=patient&id=`+ row["id"] +`&initial=true" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        Remove Block(s)
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/lab/delete/` + row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="delete_row">
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
            toggleToolbars();
            handleDeleteRows();
            handleResetForm();
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
        const filterButton = document.querySelector('[data-kt-docs-table-filter="filter"]');

        // Filter datatable on submit
        filterButton.addEventListener('click', function () {

          var race = document.getElementById("id_race").value;
          var sex = document.getElementById("id_sex").value;
          var dob = document.getElementById("id_dob").value;

          initDatatable(race, sex, dob);

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
                                    swal("Done!", "It deleted succesfully!", "success");
                                    dt.draw();
                                },
                                error: function (xhr, ajaxOptions, thrownError) {
                                    swal("Error deleting!", "Please try again", "error");
                                }
                            });

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
                            text: customerName + " could not be deleted.",
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

          document.getElementById("id_race").value = "";
          document.getElementById("id_sex").value = "";
          document.getElementById("id_dob").value = "";

          initDatatable(null, null, null);

        });
    }

    var handleSelectedRows = function (e) {
      // Select element
      const btnCreateBlock = document.querySelector('[data-kt-docs-table-select="event_selected"]');

      // Created blocks for selected rows
      btnCreateBlock.addEventListener('click', function () {

        $.ajax({
          type: "GET",
          url: "/blocks/add_block_to_patient_async",
          data: {
            "selected_ids":JSON.stringify(selectedRows),
          },
        }).done(function(result) {
          if (result.success) {
            Swal.fire({
                text: "Block(s) created succesfully.",
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
                text: "Block(s) could not be created.",
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

      var raceOptions = [];
      var sexOptions = [];

      Promise.all([

        getRaceOptions(),
        getSexOptions()

      ]).then(function () {

        editor = new $.fn.dataTable.Editor({
          ajax: {
            url: "/lab/edit_patient_async",
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
          fields: [
            {
              label: "PAT ID:",
              name: "pat_id"
            }, {
              label: "Source:",
              name: "source"
            }, {
              label: "Sex:",
              name: "sex",
              type: "select",
              options: sexOptions,
            }, {
              label: "Race:",
              name: "race",
              type: "select",
              options: raceOptions,
            }
         ],
         formOptions: {
            inline: {
              onBlur: 'submit'
            }
         }
       });

      });

      $('.table').on( 'click', 'tbody td:not(:first-child):not(:last-child)', function (e) {
        editor.inline( dt.cell( this ).index(), {
            onBlur: 'submit'
        });
      });

      function getRaceOptions() {

        $.ajax({
            url: "/lab/get_race_options",
            type: "GET",
            async: false,
            success: function (data) {

             // var options = [];
             data.forEach((item, i) => {

               raceOptions.push({
                 "label":item["label"],
                 "value":item["value"]
               })

             });
            }
        });

      }

      function getSexOptions() {

        $.ajax({
            url: "/lab/get_sex_options",
            type: "GET",
            async: false,
            success: function (data) {

             // var options = [];
             data.forEach((item, i) => {

               sexOptions.push({
                 "label":item["label"],
                 "value":item["value"]
               })

             });
            }
        });

      }


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
            initDatatable(handleInitialValue(), null,null,null);
            handleSearchDatatable();
            handleFilterDatatable();
            handleDeleteRows();
            handleResetForm();
            handleSelectedRows();
            initEditor();
        }
    }
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesServerSide.init();
});
