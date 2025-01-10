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
    var initDatatable = function ( initialValue, p_stage, prim, collection , body_site ) {
        $.fn.dataTable.moment( 'MM/DD/YYYY' );

        dt = $("#block_datatable").DataTable({
            // searchDelay: 500,
            processing: true,
            serverSide: true,
            order: [[1, 'desc']],
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
                "collection": collection,
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
                          console.log(data);
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
                    orderable: false,
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
                                    <a href="#" class="menu-link px-3 variant-link">View Variants</a>
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
                // show image
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
          var collection = document.getElementById("id_collection").value;
          var body_site = document.getElementById("id_body_site").value;

          initDatatable(null, p_stage, prim, collection, body_site);

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
          document.getElementById("id_collection").value = "";
          document.getElementById("id_body_site").value = "";

          initDatatable(null, null, null, null, null);

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
              "selected_ids": getSelectedRows(),
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
                    "selected_ids": getSelectedRows(),
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
              "selected_ids": getSelectedRows(),
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
              "selected_ids": getSelectedRows(),
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
                // type: "select",
                // options: bodyOptions
                type: "readonly",
                attr: {
                  disabled:true
                }
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
        const variantModal = document.getElementById("variant_layout");
        const variantInstance = new bootstrap.Modal(variantModal);

        document.querySelectorAll('.variant-link').forEach((item, i) => {

            item.addEventListener('click', function () {
                // Select parent row
                const parent = this.closest('tr');
                // Get customer name
                const id = parent.querySelector('input[type=checkbox]').value;
                // Open modal
                variantInstance.show();
                getVariantData( id );
            });
        });

        function getVariantData( block_id ) {
            fetch(`/variant/get_variants_by_block?block_id=${block_id}`)
                .then(response => response.json())
                .then(data => {
                    initializeModal(data);
                    $('#variant_layout').modal('show');
                });
        }

        function initializeModal( data ) {
            // Initialize tabs
            const tabContainer = document.getElementById('variantTabList');
            const tabContent = document.getElementById('variantTabContent');

            // Clear modal first
            tabContainer.innerHTML = "";
            tabContent.innerHTML = "";

            // Fill the data
            populateBlockDetails(data.block);

            // Check if there are any analyses
            if (!data.analyses || data.analyses.length === 0) {
                showNoDataMessage(tabContent, "No analysis runs found for this area.");
                return;
            }

            // Check if any analysis has variants
            const hasVariants = data.analyses.some(analysis => analysis.variants && analysis.variants.length > 0);
            if (!hasVariants) {
                showNoDataMessage(tabContent, "No variants found in any analysis runs.");
                return;
            }

            data.analyses.forEach((analysis, index) => {
                // Create tab
                const isActive = index === 0;
                const tabId = `analysis_${index}`;

                createTab(tabContainer, tabId, analysis.analysis_name, isActive);
                createTabPane(tabContent, tabId, analysis.variants, isActive);

            });
        }

        function showNoDataMessage(container, message) {
            container.innerHTML = `
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
        }

        function populateBlockDetails( data ) {
            document.querySelector('input[name="block_name"]').value = data.name;
            document.querySelector('input[name="body_site"]').value = data.body_site;
            document.querySelector('textarea[name="diagnosis"]').textContent = data.diagnosis;

            if (data.he_image) {
                document.querySelector('a[name="he_image"]').href = data.he_image;
            }
        }

        function createTab(container, id, text, isActive) {
            const li = document.createElement('li');
            li.className = 'nav-item';
            li.innerHTML = `
                <a class="nav-link text-active-primary pb-4 ${isActive ? 'active' : ''}"
                   data-bs-toggle="tab"
                   href="#${id}">
                   ${text}
                </a>`;
            container.appendChild(li);
        }

        function createTabPane(container, id, data, isActive) {
            const div = document.createElement('div');
            div.className = `tab-pane fade ${isActive ? 'show active' : ''}`;
            div.id = id;
            div.innerHTML = `
                <div class="card card-flush mt-2 flex-row-fluid overflow-hidden">
                    <div class="card-body pt-0">
                        <div class="table-responsive">
                            <table id="variant_datatable_${id}" class="table align-middle table-row-dashed fs-6 gy-5">
                                <thead>
                                    <tr class="text-start text-gray-400 fw-bold fs-7 text-uppercase gs-0">
                                        <th>Area</th>
                                        <th>Sample Library</th>
                                        <th>Gene</th>
                                        <th>P Variant</th>
                                        <th>Coverage</th>
                                        <th>VAF</th>
                                        <th class="text-end min-w-100px">Actions</th>
                                    </tr>
                                </thead>
                                <tbody class="text-gray-600 fw-semibold"></tbody>
                            </table>
                        </div>
                    </div>
                </div>`;
            container.appendChild(div);

            // Initialize DataTable
            initializeDataTable(`variant_datatable_${id}`, data);
        }

        function initializeDataTable(tableId, variants) {
            $(`#${tableId}`).DataTable({
                data: variants,
                columns: [
                    {
                        data: 'areaName',
                        className: 'text-gray-800 text-hover-primary'
                    },
                    {
                        data: 'sampleLibrary',
                        className: 'text-gray-800 text-hover-primary'
                    },
                    {
                        data: 'gene',
                        className: 'text-gray-800'
                    },
                    {
                        data: 'pVariant',
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
                        data: null,
                        className: 'text-end',
                        render: function() {
                            return `
                                <button type="button"
                                        class="btn btn-icon btn-light-primary btn-sm"
                                        data-bs-toggle="tooltip"
                                        data-bs-placement="top"
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
                order: [[1, 'asc']],  // Sort by gene by default
                pageLength: 10,
                lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
                responsive: true
            });
        }

        // Add event listener for dt-control click
        document.querySelectorAll('#block_datatable tbody td.dt-control').forEach((item) => {
            item.addEventListener('click', function () {
                var tr = this.closest('tr');
                var row = dt.row(tr);
                var data = row.data();

                // Make AJAX request to get_block_async view
                fetch(`/blocks/get_block_async?id=${data.id}`)
                    .then(response => response.json())
                    .then(blockData => {
                        // Populate modal with block details
                        var modalBody = document.querySelector('#blockDetailsTable tbody');
                        modalBody.innerHTML = format(blockData);

                        // Show modal
                        var blockDetailsModal = new bootstrap.Modal(document.getElementById('blockDetailsModal'));
                        blockDetailsModal.show();
                    });
            });
        });

        // Add event listener for modal close button
        document.querySelectorAll('#blockDetailsModal .btn-close, #blockDetailsModal .btn-secondary').forEach((item) => {
            item.addEventListener('click', function () {
                var blockDetailsModal = bootstrap.Modal.getInstance(document.getElementById('blockDetailsModal'));
                blockDetailsModal.hide();
                document.querySelectorAll('.modal-backdrop').forEach((backdrop) => {
                    backdrop.remove();
                });
            });
        });

        function format(d) {
            // `d` is the original data object for the row
            let details = '';

            if (d.name) {
                details += `
                    <tr>
                        <td>Full name:</td>
                        <td>${d.name}</td>
                    </tr>`;
            }
            if (d.patient) {
                details += `
                    <tr>
                        <td>Patient:</td>
                        <td>${d.patient}</td>
                    </tr>`;
            }
            if (d.age) {
                details += `
                    <tr>
                        <td>Age:</td>
                        <td>${d.age}</td>
                    </tr>`;
            }
            if (d.body_site) {
                details += `
                    <tr>
                        <td>Body site:</td>
                        <td>${d.body_site}</td>
                    </tr>`;
            }
            if (d.ulceration !== null) {
                details += `
                    <tr>
                        <td>Ulceration:</td>
                        <td>${d.ulceration}</td>
                    </tr>`;
            }
            if (d.thickness) {
                details += `
                    <tr>
                        <td>Thickness:</td>
                        <td>${d.thickness}</td>
                    </tr>`;
            }
            if (d.mitoses) {
                details += `
                    <tr>
                        <td>Mitoses:</td>
                        <td>${d.mitoses}</td>
                    </tr>`;
            }
            if (d.p_stage) {
                details += `
                    <tr>
                        <td>P Stage:</td>
                        <td>${d.p_stage}</td>
                    </tr>`;
            }
            if (d.prim) {
                details += `
                    <tr>
                        <td>Prim:</td>
                        <td>${d.prim}</td>
                    </tr>`;
            }
            if (d.subtype) {
                details += `
                    <tr>
                        <td>Subtype:</td>
                        <td>${d.subtype}</td>
                    </tr>`;
            }
            if (d.slides) {
                details += `
                    <tr>
                        <td>Slides:</td>
                        <td>${d.slides}</td>
                    </tr>`;
            }
            if (d.slides_left) {
                details += `
                    <tr>
                        <td>Slides Left:</td>
                        <td>${d.slides_left}</td>
                    </tr>`;
            }
            if (d.fixation) {
                details += `
                    <tr>
                        <td>Fixation:</td>
                        <td>${d.fixation}</td>
                    </tr>`;
            }
            if (d.storage) {
                details += `
                    <tr>
                        <td>Storage:</td>
                        <td>${d.storage}</td>
                    </tr>`;
            }
            if (d.scan_number) {
                details += `
                    <tr>
                        <td>Scan Number:</td>
                        <td>${d.scan_number}</td>
                    </tr>`;
            }
            if (d.icd10) {
                details += `
                    <tr>
                        <td>ICD10:</td>
                        <td>${d.icd10}</td>
                    </tr>`;
            }
            if (d.diagnosis) {
                details += `
                    <tr>
                        <td>Diagnosis:</td>
                        <td>${d.diagnosis}</td>
                    </tr>`;
            }
            if (d.notes) {
                details += `
                    <tr>
                        <td>Notes:</td>
                        <td>${d.notes}</td>
                    </tr>`;
            }
            if (d.micro) {
                details += `
                    <tr>
                        <td>Micro:</td>
                        <td>${d.micro}</td>
                    </tr>`;
            }
            if (d.gross) {
                details += `
                    <tr>
                        <td>Gross:</td>
                        <td>${d.gross}</td>
                    </tr>`;
            }
            if (d.clinical) {
                details += `
                    <tr>
                        <td>Clinical:</td>
                        <td>${d.clinical}</td>
                    </tr>`;
            }
            if (d.date_added) {
                const date = new Date(d.date_added);
                const formattedDate = `${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')}/${date.getFullYear()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
                details += `
                    <tr>
                        <td>Date Added:</td>
                        <td>${formattedDate}</td>
                    </tr>`;
            }
            if (d.old_body_site) {
                details += `
                    <tr>
                        <td>Old Body Site:</td>
                        <td>${d.old_body_site}</td>
                    </tr>`;
            }
            if (d.path_note) {
                details += `
                    <tr>
                        <td>Path Note:</td>
                        <td>${d.path_note}</td>
                    </tr>`;
            }
            if (d.ip_dx) {
                details += `
                    <tr>
                        <td>IP DX:</td>
                        <td>${d.ip_dx}</td>
                    </tr>`;
            }

            return details;
        }

    }

    // Public methods
    return {
        init: function () {
            initDatatable( handleInitialValue(), null, null, null, null );
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
