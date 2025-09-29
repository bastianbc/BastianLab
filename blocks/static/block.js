"use strict";

// Class definition
var KTDatatablesServerSide = function () {
    // Shared variables
    var table;
    var dt;
    var filterPayment;
    var editor;
    var popupWindow;
    var selectedRows = [];

    // Private functions
    var initDatatable = function ( initialValue, p_stage, prim, body_site ) {
        $.fn.dataTable.moment( 'MM/DD/YYYY' );

        dt = $("#block_datatable").DataTable({
            // searchDelay: 500,
            processing: true,
            serverSide: true,
            order: [[9, 'desc']],
            stateSave: false,
            destroy: true,
            select: {
                style: 'multi',
                selector: 'td:first-child input[type="checkbox"]',
                className: 'row-selected'
            },
            keys: {
              columns: '.editable',
              keys: [ 9 ],
              editor: editor,
              editOnFocus: true
            },
            ajax: {
              url: '/blocks/filter_blocks',
              type: 'GET',
              data:{
                "p_stage": p_stage,
                "prim": prim,
                "body_site": body_site,
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
              { class: 'dt-control', orderable:false, data:null, defaultContent:'' },
              { data: 'id' },
              { data: 'name',className: 'editable' },
              { data: 'project' },
              { data: 'patient' },
              { data: 'diagnosis',   className: 'editable' },
              { data: 'body_site',   className: 'editable' },
              { data: 'scan_number' },
              { data: 'num_areas' },
              { data: 'num_variants' },
              { data: null }
            ],
            columnDefs: [
                {
                    targets: 1,
                    orderable: false,
                    render: function (data) {
                        return `
                            <div class="form-check form-check-sm form-check-custom form-check-solid">
                                <input class="form-check-input" type="checkbox" value="${data}" />
                            </div>`;
                    }
                },
                {
                    targets: 3,
                    orderable: true,
                    render: function (data, type, row) {
                        if (data !== null) {
                          let id = row["id"];
                          return `<a href="/projects?model=project&id=${id}&initial=true">${data}</a>`;
                        }

                        return data;
                    }
                },
                {
                    targets: 4,
                    orderable: true,
                    render: function (data, type, row) {
                        if (data !== null) {
                          let id = row["id"];
                          return `<a href="/lab?model=block&id=${id}&initial=true">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 7,
                    orderable: true,
                    render: function (data, type, row) {
                      if (data) {
                        return `<a href="javascript:;" class="scan-image" data-url="`+ row["block_url"] + row["scan_number"] +`"><i class="fa-solid fa-image fa-xl" style="color: #40f900;"></i></a>`;
                      }
                      return "";
                    }
                },
                {
                    targets: 8,
                    orderable: true,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let id = row["id"];
                          return `
                              <a href="/areas?model=block&id=${id}&initial=true">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                  targets: 9,
                  orderable: true,
                  render: function (data, type, row) {
                    if (data > 0) {
                      // no navigation; carry the block id for the delegated click handler
                      return `<a href="#" class="variant-link text-primary text-decoration-none cursor-pointer" data-block-id="${row.id}" role="button">${data}</a>`;
                    }
                    return data;
                  }
                },
                {
                    targets: -1,
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
                                    <a href="/blocks/edit/`+ row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        Edit
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                  <a href="javascript:;" class="menu-link px-3" data-block_id=` + row["id"] + ` data-block_name=` + row["name"] + ` data-bs-toggle="modal" data-bs-target="#modal_area_options">
                                      Create Area(s)
                                  </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
<!--                                <div class="menu-item px-3">-->
<!--                                    <a href="#" class="menu-link px-3 variant-link">View Variants</a>-->
<!--                                </div>-->
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/blocks/delete/` + row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="delete_row">
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
            handleBatchDeleteRows();
            toggleToolbars();
            handleDeleteRows();
            handleResetForm();
            initShowScanImage();
            handleVariantModal();
            handleSelectedRows.init();
            KTMenu.createInstances();
        });
    }

    // *************************************************************************************************************
    // It was used this way to stay true to the theme structure.The theme selects/deselects the checkboxes itself.
    // Then, we capture the checked boxes like this. We used the delay time.
    // See: "Toggle Handler" in script.bundle.js
    // *************************************************************************************************************
    var initRowSelection = function () {
        const DELAY_MS = 50; // Delay to wait for KTUtil's operation

        // Initialize all components
        initSingleCheckboxes();
        initSelectAllCheckbox();

        function initSingleCheckboxes() {
            const allCheckboxes = document.querySelectorAll('.table tbody [type="checkbox"]');

            allCheckboxes.forEach(checkbox => {
                // Handle row selection change
                checkbox.addEventListener("change", function () {
                  // toggle row selection
                  const index = selectedRows.indexOf(this.value);

                  if (index === -1) {
                      // Add row to selection
                      selectedRows.push(this.value);
                  } else {
                      // Remove row from selection
                      selectedRows.splice(index, 1);
                  }
                });

                // Handle UI updates with slight delay
                checkbox.addEventListener('click', function () {
                    setTimeout(toggleToolbars, DELAY_MS);
                });
            });
        }

        function initSelectAllCheckbox() {
            const selectAllCheckbox = document.querySelector('[data-kt-check="true"]');

            if (selectAllCheckbox) {
                selectAllCheckbox.addEventListener("change", function () {
                    setTimeout(() => {
                        const checkedBoxes = document.querySelectorAll('.table tbody .form-check-input:checked');
                        selectedRows = Array.from(checkedBoxes).map(checkbox => checkbox.value);

                        toggleToolbars();

                    }, DELAY_MS);
                });
            }
        }
    };

    var handleRestoreRowSelection = function () {
        const allCheckboxes = document.querySelectorAll('#block_datatable tbody [type="checkbox"]');
        allCheckboxes.forEach(c => {
            if ( selectedRows.indexOf(c.value) > -1 ) {
                c.checked = true;
            }
        });

    }

    var handleVariantModal = function () {
       // Delegate click so it survives redraws; prevent page navigation
        const $table = $('#block_datatable');
        $table
          .off('click.variant') // avoid duplicate bindings if initDatatable re-runs
          .on('click.variant', '.variant-link', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const blockId = this.dataset.blockId
              || $(this).closest('tr').find('input[type="checkbox"]').val();

            VariantModalByArea.open(blockId);
          });
    }

    var initShowScanImage = function () {
        document.querySelectorAll(".scan-image").forEach((item, i) => {

            item.addEventListener("click", function () {

                // if the window didn't open before or the window made closed
                if (!popupWindow || popupWindow.closed) {
                    var windowWidth = 500;
                    var windowHeight = 500;
                    var left = (window.screen.width - windowWidth) / 2;
                    var top = (window.screen.height - windowHeight) / 2;

                    popupWindow = window.open('', '_blank', 'width=' + windowWidth + ',height=' + windowHeight + ',left=' + left + ',top=' + top);
                }

                // popupWindow.document.body.innerHTML = '<h1>'+ block +'</h1><img src="' + item.getAttribute("data-url") + '" style="max-width:100%;max-height:100%;" />';
                popupWindow.location.href = item.getAttribute("data-url");

            });

        });

    }

    function getSelectedRows() {
        const container = document.querySelector('#block_datatable');
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

          var p_stage = document.getElementById("id_p_stage").value;
          var prim = document.getElementById("id_prim").value;
          var body_site = document.getElementById("id_body_site").value;

          initDatatable(null, p_stage, prim, body_site);

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
                const name = parent.querySelectorAll('td')[2].innerText;
                const id = parent.querySelectorAll('td')[1].querySelector(".form-check-input").value;

                $.ajax({
                    url: "/blocks/check_can_deleted_async",
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
                                    text: "Block deleted succesfully.",
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

            });
        });
    }

   // Reset Filter
    var handleResetForm = () => {
        // Select reset button
        const resetButton = document.querySelector('[data-kt-docs-table-filter="reset"]');

        // Reset datatable
        resetButton.addEventListener('click', function () {

          document.getElementById("id_p_stage").value = "";
          document.getElementById("id_prim").value = "";
          document.getElementById("id_body_site").value = "";

          initDatatable(null, null, null, null);

        });
    }

    // Init toggle toolbar
    var handleBatchDeleteRows = function () {
        // Toggle selected action toolbar
        // Select all checkboxes
        const container = document.querySelector('#block_datatable');
        const checkboxes = container.querySelectorAll('[type="checkbox"]');

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

                        // Calling delete request with ajax
                        $.ajax({
                            type: "GET",
                            url: "/blocks/batch_delete",
                            data: {
                              "selected_ids": JSON.stringify(selectedRows),
                            },
                            error: function (xhr, ajaxOptions, thrownError) {
                                swal("Error deleting!", "Please try again", "error");
                            }
                        }).done(function (result) {
                            if (result.deleted) {
                              Swal.fire({
                                  text: "Block(s) deleted succesfully.",
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
                                  text: "Block(s) could not be deleted!",
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

      function resetForm() {
        document.getElementById("frm_creation_options").reset();
      }

      function initModal() {
        var modalEl = document.getElementById("modal_area_options");

        // When modal is about to open
        modalEl.addEventListener("show.bs.modal", function (e) {
          selectedItem = {
            id: e.relatedTarget.getAttribute("data-block_id"),
            name: e.relatedTarget.getAttribute("data-block_name"),
          };

          resetForm();

          initModalEvents();
        });

        // Optional: reset when modal closes
        modalEl.addEventListener("hide.bs.modal", function () {
          resetForm();
        });
      }

      function initModalEvents() {
        var btn = document.getElementById("btn_continue");

        // First remove any existing listener
        btn.replaceWith(btn.cloneNode(true));
        btn = document.getElementById("btn_continue"); // reselect cloned button

        btn.addEventListener("click", function () {
          var form = document.getElementById("frm_creation_options");
          var data = new FormData(form);
          var options = Object.fromEntries(data.entries());

          $.ajax({
            type: "GET",
            url: "/areas/add_area_to_block_async",
            data: {
              block_id: selectedItem.id,
              options: JSON.stringify(options),
            },
          })
            .done(function (result) {
              if (result.success) {
                Swal.fire({
                  text: "The areas for " + selectedItem.name + " were created",
                  icon: "info",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                    confirmButton: "btn fw-bold btn-success",
                  },
                });
              } else {
                Swal.fire({
                  text: "Area(s) could not be created.",
                  icon: "error",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                    confirmButton: "btn fw-bold btn-danger",
                  },
                });
              }

              modal.hide();
              if (typeof dt !== "undefined" && dt.draw) {
                dt.draw();
              }
            })
            .fail(function (xhr, status, error) {
              Swal.fire({
                text: "An error occurred: " + error,
                icon: "error",
                buttonsStyling: false,
                confirmButtonText: "Ok, got it!",
                customClass: {
                  confirmButton: "btn fw-bold btn-danger",
                },
              });
            });
        });
      }

      function initButtonEvents() {
        const btnAddBlockToProject = document.querySelector('[data-kt-docs-table-select="event_add_block_to_project"]');
        const btnAddBlockToPatient = document.querySelector('[data-kt-docs-table-select="event_add_block_to_patient"]');
        const btnRemoveBlockFromProject = document.querySelector('[data-kt-docs-table-select="event_remove_block_from_project"]');
        const btnRemoveBlockFromPatient = document.querySelector('[data-kt-docs-table-select="event_remove_block_from_patient"]');

        if (btnAddBlockToProject) btnAddBlockToProject.addEventListener('click', addBlockToProject);
        if (btnAddBlockToPatient) btnAddBlockToPatient.addEventListener('click', addBlockToPatient);
        if (btnRemoveBlockFromProject) btnRemoveBlockFromProject.addEventListener('click', removeBlockFromProject);
        if (btnRemoveBlockFromPatient) btnRemoveBlockFromPatient.addEventListener('click', removeBlockFromPatient);
      }

      function addBlockToProject() {
        $.ajax({
          type: "GET",
          url: "/blocks/add_block_to_project_async",
          data: {
            "selected_ids": JSON.stringify(selectedRows),
            "project_id": this.getAttribute('data-project_id')
          },
        }).done(function(result) {
          if (result.success) {
            Swal.fire({
                text: "Block(s) added succesfully.",
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
                text: "Block(s) could not be added.",
                icon: "error",
                buttonsStyling: false,
                confirmButtonText: "Ok, got it!",
                customClass: {
                    confirmButton: "btn fw-bold btn-danger",
                }
            });
          }
        });
      }

      function addBlockToPatient() {
        $.ajax({
            type: "GET",
            url: "/blocks/add_block_to_patient_async",
            data: {
                "selected_ids": JSON.stringify(selectedRows),
                "patient_id": this.getAttribute('data-patient_id')
            },
        }).done(function(result) {
            if (result.success) {
                Swal.fire({
                    text: "Block(s) added to the patient successfully.",
                    icon: "info",
                    buttonsStyling: false,
                    confirmButtonText: "Ok, got it!",
                    customClass: {
                        confirmButton: "btn fw-bold btn-success",
                    }
                }).then(function(){
                    window.location.href = "/lab";
                });
            }
            else {
                Swal.fire({
                    text: "Block(s) could not be added to the patient.",
                    icon: "error",
                    buttonsStyling: false,
                    confirmButtonText: "Ok, got it!",
                    customClass: {
                        confirmButton: "btn fw-bold btn-danger",
                    }
                });
            }
        });
      };

      function removeBlockFromProject() {

        $.ajax({
          type: "GET",
          url: "/blocks/remove_block_from_project_async",
          data: {
            "selected_ids": JSON.stringify(selectedRows),
            "project_id": this.getAttribute('data-project_id')
          },
        }).done(function(result) {
          if (result.success) {
            Swal.fire({
                text: "Block(s) removed succesfully.",
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
                text: "Block(s) could not be removed.",
                icon: "error",
                buttonsStyling: false,
                confirmButtonText: "Ok, got it!",
                customClass: {
                    confirmButton: "btn fw-bold btn-danger",
                }
            });
          }
        });

      };

      function removeBlockFromPatient() {
        $.ajax({
          type: "GET",
          url: "/blocks/remove_block_from_patient_async",
          data: {
            "selected_ids": JSON.stringify(selectedRows),
            "project_id": this.getAttribute('data-patient_id')
          },
        }).done(function(result) {
          if (result.success) {
            Swal.fire({
                text: "Block(s) removed succesfully.",
                icon: "info",
                buttonsStyling: false,
                confirmButtonText: "Ok, got it!",
                customClass: {
                    confirmButton: "btn fw-bold btn-success",
                }
            }).then(function(){
              window.location.href = "/lab";
            });
          }
          else {
            Swal.fire({
                text: "Block(s) could not be removed.",
                icon: "error",
                buttonsStyling: false,
                confirmButtonText: "Ok, got it!",
                customClass: {
                    confirmButton: "btn fw-bold btn-danger",
                }
            });
          }
        });
      }

      return {
        init: function () {
          initModal();
          initButtonEvents();
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

        // Toggle toolbars
        if (selectedRows.length > 0) {
            selectedCount.innerHTML = selectedRows.length;
            toolbarBase.classList.add('d-none');
            toolbarSelected.classList.remove('d-none');
        } else {
            toolbarBase.classList.remove('d-none');
            toolbarSelected.classList.add('d-none');
        }
    };


    var initEditor = function () {

      var bodyOptions = [];
      var collectionOptions = [];

      Promise.all([
          getBodyOptions(),
      ]).then(function () {
          editor = new $.fn.dataTable.Editor({
            ajax: {
                url: "/blocks/edit_block_async",
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
            table: "#block_datatable",
            fields: [
              {
                label: "Name:",
                name: "name"
              },
              {
                label: "Diagnosis:",
                name: "diagnosis"
              },
              {
                label: "Body Site:",
                name: "body_site",
                type: "select",
                options: bodyOptions,
              },
              {
                label: "Thickness:",
                name: "thickness"
              },
              {
                 label: "Collection:",
                 name: "collection",
                 type: "select",
                 options: collectionOptions
              },
              {
                label: "Date Added:",
                name: "date_added",
                type: "readonly",
                attr: {
                  disabled:true
                }
              }
           ],
            formOptions: {
              inline: {
                onBlur: 'submit'
              }
            }
        });
      });

      function getBodyOptions() {

        $.ajax({
            url: "/body/get_bodies",
            type: "GET",
            async: false,
            success: function (data) {

             // var options = [];
             data.forEach((item, i) => {

               bodyOptions.push({
                 "label":item["name"],
                 "value":item["id"]
               })

             });

             // editor.field( 'bait' ).update( options );

            }
        });

      }

      $('#block_datatable').on('click', 'tbody td.editable', function () {
          editor.inline(dt.cell(this).index(), { onBlur: 'submit' });
        });


      $('#block_datatable').on( 'key-focus', function ( e, datatable, cell ) {
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

    // Area-based Variant Modal (define once; callable via VariantModalByArea.open)
    const VariantModalByArea = (function () {
          const modal = document.getElementById("variant_layout_by_area");
          let instance = null;
          let tabContainer = null;
          let tabContent = null;

          function ensure() {
            if (!instance) instance = new bootstrap.Modal(modal);
            if (!tabContainer) tabContainer = modal.querySelector('.variant-tab-container');
            if (!tabContent)   tabContent   = modal.querySelector('.tab-content');
          }

          function clearModal() {
            tabContainer.innerHTML = "";
            tabContent.innerHTML = "";
          }

          function populateBlockDetails(data) {
            modal.querySelector('a[name="patient_id"]').textContent = data.patient_id;
            modal.querySelector('a[name="block_name"]').textContent  = data.block.name;
            modal.querySelector('a[name="diagnosis"]').textContent   = data.block.diagnosis;
            modal.querySelector('a[name="aperio_link"]').textContent   = data.block.aperio_link;
          }

          function createTab(id, text, isActive) {
            const li = document.createElement('li');
            li.className = 'nav-item';
            li.innerHTML = `
              <a class="nav-link text-active-primary pb-4 ${isActive ? 'active' : ''}"
                 data-bs-toggle="tab" href="#${id}">${text}</a>`;
            tabContainer.appendChild(li);
          }

          function createTabPane(id, areaId, isActive) {
            const div = document.createElement('div');
            div.className = `tab-pane fade ${isActive ? 'show active' : ''}`;
            div.id = id;
            div.innerHTML = `
              <div class="table-responsive">
                <table id="variant_datatable_${areaId}" class="table align-middle table-row-dashed fs-6 gy-5">
                  <thead>
                    <tr class="text-start text-gray-400 fw-bold fs-7 text-uppercase gs-0">
                      <th>VC</th><th>Analysis Run</th><th>Gene</th><th>P Variant</th>
                      <th>Alias</th><th>Coverage</th><th>VAF</th><th>Caller</th>
                      <th>Cosmic Gene Symbol</th><th>Cosmic AA</th><th>Primary Site Counts</th>
                    </tr>
                  </thead>
                  <tbody class="text-gray-600 fw-semibold"></tbody>
                </table>
              </div>`;
            tabContent.appendChild(div);
          }

          function initAreaVariantsTable(areaId) {
            const sel = `#variant_datatable_${areaId}`;
            if ($.fn.DataTable.isDataTable(sel)) {
              $(sel).DataTable().clear().destroy();
              $(sel).off();
            }
            $(sel).DataTable({
              processing: true,
              serverSide: true,
              ajax: { url: `/variant/get_variants_by_area`, type: 'GET', data: { area_id: areaId } },
              columns: [
                { data: 'gvariant_id', visible: false },
                { data: 'analysis_run_name', className: 'text-gray-800' },
                { data: 'gene_name',         className: 'text-gray-800' },
                { data: 'p_variant',         className: 'text-gray-800' },
                { data: 'alias',             className: 'text-gray-800' },
                { data: 'coverage',          className: 'text-gray-800' },
                { data: 'vaf',               className: 'text-gray-800' },
                { data: 'caller',            className: 'text-gray-800' },
                { data: 'cosmic_gene_symbol',className: 'text-gray-800' },
                { data: 'cosmic_aa',         className: 'text-gray-800' },
                {
                  data: 'total_site_counts',
                  className: 'text-gray-800 text-center',
                  render: function (data, type, row) {
                    const tip = row.cosmic_primary_site_counts
                      ? Object.entries(row.cosmic_primary_site_counts).map(([k, v]) => `${k}: ${v}`).join('<br>')
                      : '';
                    return `<span data-toggle="tooltip" data-html="true" title="${tip}">${data}</span>`;
                  }
                }
              ],
              order: [[10, 'desc']],
              pageLength: 10,
              lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
              responsive: true
            });

            $(sel).on('draw.dt', function () {
              $('[data-toggle="tooltip"]').tooltip({ html: true });
            });
          }

          async function build(blockId) {
            clearModal();
            const resp = await fetch(`/blocks/get_block_areas/${blockId}/`);
            const data = await resp.json();

            populateBlockDetails(data);

            data.areas.forEach((area, index) => {
              const isActive = index === 0;
              const tabId = `area_${index}`;
              createTab(tabId, area.name, isActive);
              createTabPane(tabId, area.id, isActive);
              initAreaVariantsTable(area.id);
            });
          }

          return {
            init() { ensure(); },                     // call once on page init
            async open(blockId) { ensure(); instance.show(); await build(blockId); }
          };
        })();


    $(document).on('click', '.show-popup', function (e) {
        e.preventDefault();
        let details = $(this).data('details');

        $('#detailsContent').text(details);
        let modal = new bootstrap.Modal(document.getElementById('detailsModal'));
        modal.show();
    });
    // Public methods
    return {
        init: function () {
            initDatatable( handleInitialValue(), null, null, null );
            handleSearchDatatable();
            handleBatchDeleteRows();
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
