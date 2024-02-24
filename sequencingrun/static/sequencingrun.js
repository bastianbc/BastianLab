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
                                    <a href="javascript:;" class="menu-link sequencing-files-link" data-kt-docs-table-filter="detail_row">
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
            initToggleToolbar();
            toggleToolbars();
            handleDeleteRows();
            handleResetForm();
            initRowActions();
            handleSelectedRows.init();
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

      function uncheckedFirstCheckBox() {

        dt.on( 'draw', function () {

          // Remove header checked box
          const headerCheckbox = container.querySelectorAll('[type="checkbox"]')[0];
          headerCheckbox.checked = false;

        });

      }

       function handleGenerateSheet() {
          const generateSelected = document.querySelector('[data-kt-docs-table-select="generate_sample_sheet"]');
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
                url: '/sheet/sheet_multiple',
                type: 'POST',
                headers: {'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value },
                data: {
                    "selected_ids": getSelectedRows()
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
                              "selected_ids": getSelectedRows(),
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
          handleBatchDelete(), handleGenerateSheet(), uncheckedFirstCheckBox();
        }
      }

    })();


    // loadingEl
    function loadingEl() {
        const loadingEl = document.createElement("div");
        document.body.prepend(loadingEl);
        loadingEl.classList.add("page-loader");
        loadingEl.classList.add("flex-column");
        loadingEl.classList.add("bg-dark");
        loadingEl.classList.add("bg-opacity-25");
        loadingEl.innerHTML = `
                <span class="spinner-border text-primary" role="status"></span>
                <span class="text-gray-800 fs-6 fw-semibold mt-5">Loading...</span>
            `;
        KTApp.showPageLoading();
        return loadingEl;
    }


    function initSequencingFilesModal() {
      const elSequencingFiles = document.getElementById("modal_sequencing_files");
      const modalSequencingFiles = new bootstrap.Modal(elSequencingFiles);

      document.querySelectorAll(".sequencing-files-link").forEach((item, i) => {
        item.addEventListener("click", function () {
          var loadingElement = loadingEl();
          const parent = this.closest('tr');
          // Get customer name
          const id = parent.querySelector('input[type=checkbox]').value;
          $.ajax({
              url: "/sequencingrun/" + id + "/get_sequencing_files",
              type: "GET",
              success: function (data) {

                fillElements(data);
                document.querySelector('button[name=btnSave]').addEventListener("click", function () {
                  saveChanges(id);
                });
                document.querySelectorAll('.fl_sl').forEach(function(element) {
                    element.addEventListener("change", function() {
                        console.log($(this));
                        var row = this.closest('.row');
                        var file_set_input_name = row.querySelector('.fset');
                        if (file_set_input_name && !file_set_input_name.value.includes("_FLAG_")) {
                            file_set_input_name.value = file_set_input_name.value + "_FLAG_";
                        }
                    });
                });
                loadingElement.remove();
                modalSequencingFiles.show();
              },
              error: function (data) {
                loadingElement.remove();
                Swal.fire({
                  text: data.responseJSON.message,
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

      });

    }


    function fillElements(data) {

      var list = document.querySelector(".list-body2");

      list.innerHTML = ""; // Clean the list

      for (var i = 0; i < data.files.length; i++) {

        var sel = document.createElement("select");
        sel.classList.add("select","form-control","form-control-sm", "fl_sl")
        var defaultOption = document.createElement("option");
        defaultOption.text = "Not Matched";
        defaultOption.value = "not_matched";
        defaultOption.setAttribute("selected", "selected");

        sel.add(defaultOption);

        var emptyOption = document.createElement("option");
        emptyOption.text = "";
        emptyOption.value = "";
        sel.add(emptyOption, 0);

        for (var sl of data.sample_libs) {
          var opt = document.createElement("option");
          opt.value = sl.id;
          opt.text = sl.name;

          if (sl.id == data.files[i][1]) { // mactched sample_lib
            opt.setAttribute("selected", "selected");
          }

          sel.add(opt);
        }

        var row = `<div class="row">
                      <div class="col-2">${sel.outerHTML}</div>
                      <div class="col-4"><input type="text" class="form-control fset form-control-sm" value="${data.files[i][2]}"></div>
                      <div class="col-4"><span class="fname">${data.files[i][0]}</span></div>
                      <div class="col-2 text-center"><span class="num">${data.files[i][3]}</span></div>
                   </div>
                   `;
        list.innerHTML += row;
      }


    }

    function saveChanges(id) {
        var loadingElement = loadingEl();
      var list = document.querySelectorAll(".list-body2 .row");
      const elSequencingFiles = document.getElementById("modal_sequencing_files");
      const modalSequencingFiles = new bootstrap.Modal(elSequencingFiles);

      var data = [];

      list.forEach((row, i) => {
        var sample_lib_id = row.querySelector("select").value;
        var file_set_name = row.querySelector("input[type=text]").value;
        var file_name = row.querySelector(".fname").textContent;
        var file_numbers = row.querySelector(".num").textContent;

        data.push({
            sample_lib_id: sample_lib_id,
            file_set_name: file_set_name,
            file_name: file_name,
            file_numbers: file_numbers
          });
      });

      $.ajax({
          url: "/sequencingrun/save_sequencing_files",
          data: {
            "id":id,
            "data":JSON.stringify(data),
          },
          headers: {'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value },
          type: "POST",
          }).done(function(result) {
            if (result.success) {
                loadingElement.remove();
              Swal.fire({
              text: "Sequencing Files Saved Succesfully.",
              icon: "info",
              buttonsStyling: false,
              confirmButtonText: "Ok, got it!",
              customClass: {
                  confirmButton: "btn fw-bold btn-success",
              }
          }).then(function(){
                console.log(modalSequencingFiles);
                document.getElementById("modal_sequencing_files").style.display = "none";
              });
            }
            else {
              loadingElement.remove();
              Swal.fire({
              text: "Sequencing File(s)  could not be saved!",
              icon: "error",
              buttonsStyling: false,
              confirmButtonText: "Ok, got it!",
              customClass: {
                  confirmButton: "btn fw-bold btn-success",
              }
            }).then(function(){
                document.getElementById("modal_sequencing_files").style.display = "none";
              });
            }

          });
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
              <div class="col-2 align-self-center text-center" data-id="${ data[i].id }"><a href="/sequencingrun/edit/${id}"><i class="far fa-trash fs-4 text-danger"></i></a></div>
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
