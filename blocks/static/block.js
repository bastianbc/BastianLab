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
              columns: ':not(:first-child)',
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
              {
                class: 'dt-control',
                orderable: false,
                data: null,
                defaultContent: ''
              },
              { data: 'id' },
              { data: 'name'},
              { data: 'project'},
              { data: 'patient' },
              { data: 'diagnosis' },
              { data: 'body_site' },
              { data: 'scan_number'},
              { data: 'num_areas' },
              { data: 'num_variants' },
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
                        return `<a href="javascript:;" class="scan-image" data-url="`+ row["block_url"]["url"] + row["scan_number"] +`"><i class="fa-solid fa-image fa-xl" style="color: #40f900;"></i></a>`;
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
                          let id = row["id"];
                          return `
                              <a href="#" class="variant-link-by-area">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 10,
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
            handleRowActions();
            KTMenu.createInstances();
        });

    }

    var initRowSelection = function () {
        // Select all checkboxes
        const allCheckboxes = document.querySelectorAll('#block_datatable tbody [type="checkbox"]');
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
        const allCheckboxes = document.querySelectorAll('#block_datatable tbody [type="checkbox"]');
        allCheckboxes.forEach(c => {
            if ( selectedRows.indexOf(c.value) > -1 ) {
                c.checked = true;
            }
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
                  text: "Areas(s) could not be created.",
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

      const btnAddBlockToProject = document.querySelector('[data-kt-docs-table-select="event_add_block_to_project"]');

      const btnAddBlockToPatient = document.querySelector('[data-kt-docs-table-select="event_add_block_to_patient"]');


      const btnRemoveBlockFromProject = document.querySelector('[data-kt-docs-table-select="event_remove_block_from_project"]');
      const btnRemoveBlockFromPatient = document.querySelector('[data-kt-docs-table-select="event_remove_block_from_patient"]');

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

        });

      }
      if (btnAddBlockToPatient) {

        btnAddBlockToPatient.addEventListener('click', function () {

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

        });

    }

      if (btnRemoveBlockFromProject) {

        btnRemoveBlockFromProject.addEventListener('click', function () {

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

        });

      }

      if (btnRemoveBlockFromPatient) {

        btnRemoveBlockFromPatient.addEventListener('click', function () {

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
        const container = document.querySelector('#block_datatable');
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

      $('#block_datatable').on( 'click', 'tbody td:not(:first-child)', function (e) {
        editor.inline( dt.cell( this ).index(), {
            onBlur: 'submit'
        });
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

    var handleRowActions = function () {
        // Area Base Variant Modal
        const VariantModalByArea = {
            modal: document.getElementById("variant_layout_by_area"),
            instance: null,
            tabContainer: null,
            tabContent: null,

            init: function() {
                console.log("this:",this);
                console.log("this:",document.getElementById("variant_layout_by_area"));
                this.instance = new bootstrap.Modal(this.modal);
                console.log("this.instance:",this.instance);
                this.tabContainer = this.modal.querySelector('.variant-tab-container');
                this.tabContent = this.modal.querySelector('.tab-content');
                this.setupEventListeners();
            },

            setupEventListeners: function() {
                document.querySelectorAll('.variant-link-by-area').forEach((item, i) => {
                    item.addEventListener('click', (e) => {
                        // Select parent row
                        const parent = e.target.closest('tr');
                        // Get customer name
                        const id = parent.querySelector('input[type=checkbox]').value;
                        // Open modal
                        this.instance.show();
                        this.initializeModal(id);
                    });
                });

            },

            initializeModal: function(blockId) {
                // Clear modal first
                this.tabContainer.innerHTML = "";
                this.tabContent.innerHTML = "";

                fetch(`/blocks/get_block_areas/${blockId}/`)
                    .then(response => response.json())
                    .then(data => {
                        console.log(data);
                        // fill the details
                        this.populateBlockDetails(data);

                        // create areas
                        data.areas.forEach((area, index) => {
                            // Create tab
                            const isActive = index === 0;
                            const tabId = `area_${index}`;

                            this.createTab(tabId, area.name, isActive);
                            this.createTabPane(tabId, area.id, isActive, data.block.id);
                            this.initializeDataTable(area.id);
                        });
                    })
                    .catch(error => {
                        console.error('Could not get block data:', error);
                    });

            },

            populateBlockDetails: function(data) {
                this.modal.querySelector('a[name="patient_id"]').textContent = data.patient_id;
                this.modal.querySelector('a[name="block_name"]').textContent = data.block.name;
                this.modal.querySelector('a[name="diagnosis"]').textContent = data.block.diagnosis;
                this.modal.querySelector('a[name="body_site"]').textContent = data.block.body_site;
            },

            showNoDataMessage: function(message) {
                tabContainer.innerHTML = `
                    <div class="card">
                        <div class="card-body p-10 text-center">
                            <i class="ki-duotone ki-information-5 fs-5x text-primary mb-5">
                                <span class="path1"></span>
                                <span class="path2"></span>
                                <span class="path3"></span>
                            </i>
                            <p class="fs-3 fw-semibold text-gray-800 mb-2">${message}</p>
                            <p class="fs-6 text-gray-600">Please select a different area or check if analysis has been completed.</p>
                        </div>
                    </div>
                `;
            },

            createTab: function(id, text, isActive) {
                const li = document.createElement('li');
                li.className = 'nav-item';
                li.innerHTML = `
                    <a class="nav-link text-active-primary pb-4 ${isActive ? 'active' : ''}"
                       data-bs-toggle="tab"
                       href="#${id}">
                       ${text}
                    </a>`;
                this.tabContainer.appendChild(li);
            },

            createTabPane: function(id, areaId, isActive, blockId) {
                const div = document.createElement('div');
                div.className = `tab-pane fade ${isActive ? 'show active' : ''}`;
                div.id = id;
                div.innerHTML = `
                  <div class="table-responsive">
                      <table id="variant_datatable_${areaId}" class="table align-middle table-row-dashed fs-6 gy-5">
                          <thead>
                              <tr class="text-start text-gray-400 fw-bold fs-7 text-uppercase gs-0">
                                  <th>VC</th>
                                  <th>Analysis Run</th>
                                  <th>Gene</th>
                                  <th>P Variant</th>
                                  <th>Alias</th>
                                  <th>Coverage</th>
                                  <th>VAF</th>
                                  <th>Cosmic</th>
                                  <th class="text-end min-w-100px">Actions</th>
                              </tr>
                          </thead>
                          <tbody class="text-gray-600 fw-semibold"></tbody>
                      </table>
                  </div>`;
                this.tabContent.appendChild(div);
            },

            initializeDataTable: function(areaId) {
                $(`#variant_datatable_${areaId}`).DataTable({
                    processing: true,
                    serverSide: true,
                    ajax: {
                        url: `/variant/get_variants_by_area`,
                        type: 'GET',
                        data: {
                            area_id: areaId,
                        }
                    },
                    columns: [
                        {
                            data: 'variantcall_id',
                        },
                        {
                            data: 'analysis_run_name',
                            className: 'text-gray-800'
                        },
                        {
                            data: 'gene_name',
                            className: 'text-gray-800'
                        },
                        {
                            data: 'p_variant',
                            className: 'text-gray-800'
                        },
                        {
                            data: 'alias',
                            className: 'text-gray-800'
                        },
                        {
                            data: 'coverage',
                            className: 'text-gray-800'
                        },
                        {
                            data: 'vaf',
                            className: 'text-gray-800',
                        },
                        {
                            data: 'primary_site_total',
                            className: 'text-gray-800',
                            render: function(data, type, row) {
                                let id = row["primary_site_counts"];
                                console.log(id, typeof(id));
                                return `
                                    <a href="#" 
                                       class="show-popup" 
                                       data-details='${JSON.stringify(row.primary_site_counts)}'>${data}
                                    </a>
                                `;
                            }
                        },
                        {
                            data: null,
                            className: 'text-end',
                            render: function() {

                                return `
                                    <button type="button" class="btn btn-icon btn-light-primary btn-sm" 
                                        data-bs-toggle="tooltip" data-bs-placement="top" 
                                        title="View Details"> 
                                        <i class="ki-duotone ki-eye fs-2"> 
                                            <span class="path1"></span> 
                                            <span class="path2"></span> 
                                            <span class="path3"></span> 
                                        </i> 
                                    </button>
                                `;
                            }
                        }
                    ],
                    columnDefs: [
                        {
                            targets: 0,
                            visible: false,
                        },
                        {
                            targets: 1,
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
                    ],
                    order: [[7, 'desc']],  // Sort by areas by default
                    pageLength: 10,
                    lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
                    responsive: true
                });
            },

        };

        // start the modals
        VariantModalByArea.init();
    }
    $(document).on('click', '.show-popup', function (e) {
        e.preventDefault();
        let details = $(this).data('details');
        console.log(details, typeof(details));

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
