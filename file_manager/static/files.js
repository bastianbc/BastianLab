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
    var initDatatable = function (initialValue,sub_dir) {
        console.log("init data table");
        setTimeout(function() {
        $.fn.dataTable.moment('MM/DD/YYYY');

        dt = $(".table").DataTable({
            // searchDelay: 500,
            processing: true,
            serverSide: true,
            order: [[0, 'desc']],
            stateSave: false,
            destroy: true,
            paging: true,
            pagingType: 'full_numbers',
            pageLength: "All",
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
            responsive: true,
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
              url: '/file_manager/filter_files',
              type: 'GET',
                data:{
                  sub_dir:sub_dir,
                },
                dataSrc: 'data',
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
                { data: 'status' },
                { data: 'variant_file'},
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
                    orderable: false,
                    render: function (data, type, row) {
                        if (row['type'] === 'directory') {
                            return `
                                <div class="d-flex align-items-center">
                                    <i class="ki-duotone ki-folder fs-2x text-primary me-4">
                                        <span class="path1"></span>
                                        <span class="path2"></span>
                                    </i>
                                    <a href="javascript:void(0);" class="reload-subdir-link text-gray-800 text-hover-primary" data-subdir="${encodeURIComponent(row['dir'])}">
                                        ${row['name']}
                                    </a>
                                </div>`;
                        } else if (row['type'] === 'file') {
                            return `
                                <div class="d-flex align-items-center">
                                    <span class="icon-wrapper">
                                        <i class="ki-duotone ki-files fs-2x text-primary me-4"></i>
                                    </span>
                                    <a href="" class="text-gray-800 text-hover-primary">
                                        ${row['name']}
                                    </a>
                                </div>`;
                        } else {
                            // Fallback if type is unknown
                            return `<span>${row['name']}</span>`;
                        }
                    }
                },

                {
                    targets: 2,
                    orderable: false,
                    render: function (data, type, row) {
                        const status = row['status'];
                        let badgeClass = 'badge-light-warning'; // default class
                        let label = status || 'Unknown';

                        if (status === 'Completed') {
                            badgeClass = 'badge-light-success';
                        } else if (status === 'Does not Apply') {
                            badgeClass = 'badge-light-secondary';
                        } else if (status === 'Not Processed') {
                            badgeClass = 'badge-light-danger';
                        }

                        return `<div class="badge ${badgeClass}">${label}</div>`;
                    }
                },


                {
                    targets: 4,
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
                                
                                <!--end::Menu item-->
                                <!--begin::Menu item-->
                               
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
            KTMenu.createInstances();
            addBackButtonListener();
        });

        addReloadSubDirListeners();

    }, 5000);

    }
    var isBackButtonInitialized = false;

    var addBackButtonListener = function () {
        const backButton = document.getElementById('back');
        const container = document.getElementById('breadcrumb-container');

        if (!backButton || !container || isBackButtonInitialized) return;

        backButton.addEventListener('click', function () {
            const breadcrumbLinks = container.querySelectorAll('.breadcrumb-link');
            if (breadcrumbLinks.length > 1) {
                const previousLink = breadcrumbLinks[breadcrumbLinks.length - 2];
                const previousDir = previousLink.getAttribute('data-subdir');
                if (previousDir) {
                    KTDatatablesServerSide.reloadDatatableWithSubDir(previousDir);
                    updateBreadcrumb(previousDir);
                }
            } else {
                const root = "labshare";
                KTDatatablesServerSide.reloadDatatableWithSubDir(root);
                updateBreadcrumb(root);
            }
        });

        isBackButtonInitialized = true;
    };

    window.history.replaceState(null, null, window.location.pathname);

    // Add tab event listeners
    document.getElementById("labshareBtn")?.addEventListener("click", function (e) {
        e.preventDefault();
        const subdir = "labshare";
        initDatatable(null, subdir);     // re-init with new subdir
        updateBreadcrumb(subdir);

        // Highlight tab
        this.classList.add("active");
        document.getElementById("sequencingDataBtn")?.classList.remove("active");
    });

    document.getElementById("sequencingDataBtn")?.addEventListener("click", function (e) {
        e.preventDefault();

        const subdir = "sequencingdata";

        initDatatable(handleInitialValue(), subdir);

        updateBreadcrumb(subdir);

        this.classList.add("active");
        document.getElementById("labshareBtn")?.classList.remove("active");
    });



    var currentSubDir = ""; // Keep track of the currently loaded subdirectory

    var reloadDatatableWithSubDir = function(exact_dir) {
        if (exact_dir && exact_dir !== currentSubDir) {
            currentSubDir = exact_dir; // Update the current subdirectory

            // Add 5-second delay before loading data
            setTimeout(function() {
                console.log("reloadDatatableWithSubDir");
                dt.ajax.url(`/file_manager/filter_files?exact_dir=${exact_dir}`).load(function(json) {
                    // console.log("1"*20);
                    // setTimeout(function() {
                    //     dt.columns.adjust().draw(); // Ensures redrawing of the table
                    //     console.log("2" * 20);
                    // },5000);
                    updateBreadcrumb(exact_dir);
                    console.log("3"*20);
                });
            }, 5000); // 5000 milliseconds = 5 seconds
        }
    };

    function updateBreadcrumb(path) {
        const container = document.getElementById('breadcrumb-container');
        const backButton = document.getElementById('back');

        if (!container) return;

        const segments = decodeURIComponent(path).split('/').filter(Boolean);

        const startIndex = segments.findIndex(seg => seg === 'labshare' || seg === 'sequencingdata');
        const visibleSegments = segments.slice(startIndex);  // only show from this point on

        let fullPath = '';
        let html = `
            <div class="d-flex align-items-center flex-wrap">
                <i class="ki-duotone ki-abstract-32 fs-2 text-primary me-3">
                    <span class="path1"></span>
                    <span class="path2"></span>
                </i>`;

        visibleSegments.forEach((segment, index) => {
            fullPath += (index === 0 ? '' : '/') + segment;
            html += `<a href="#" class="breadcrumb-link" data-subdir="${segments.slice(0, startIndex + index + 1).join('/')}">${segment}</a>`;

            if (index < visibleSegments.length - 1) {
                html += `
                    <i class="ki-duotone ki-right fs-2 text-primary mx-1"></i>`;
            }
        });

        html += `</div>`;
        container.innerHTML = html;

        if (visibleSegments.length <= 1) {
            backButton.style.display = 'none';
        } else {
            backButton.style.display = 'inline-flex';
        }

        container.querySelectorAll('.breadcrumb-link').forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                const subDir = this.getAttribute('data-subdir');
                KTDatatablesServerSide.reloadDatatableWithSubDir(subDir);
                updateBreadcrumb(subDir);
            });
        });
    }




    var addReloadSubDirListeners = function() {
    // Make sure to remove ALL existing listeners from the document
        $(document).off('click', '.table .reload-subdir-link');

        // Then add a new listener at the document level
        $(document).on('click', '.table .reload-subdir-link', function() {

            var self = this;
            setTimeout(function() {
                var subDir = self.getAttribute('data-subdir');
                console.log("addReloadSubDirListeners");
                KTDatatablesServerSide.reloadDatatableWithSubDir(subDir);
            }, 5000);
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

    // Public methods
    return {
        init: function () {
            const initialSubdir = "labshare";
            initDatatable(handleInitialValue(), initialSubdir);
            updateBreadcrumb(initialSubdir); // 🌟 Initial breadcrumb set
        },
        reloadDatatableWithSubDir: reloadDatatableWithSubDir  // <== Add this line

    }
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesServerSide.init();
});
