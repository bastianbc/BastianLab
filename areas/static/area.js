"use strict";

// Class definition
var KTDatatablesServerSide = function () {
    // Shared variables
    var table;
    var dt;
    var filterPayment;
    var editor;
    var selectedRows = [];

    /*
   * Initializes the datatable.
   * @param  {String} initialValue  If it comes from another page, it is initialized with this value.
   */
    var initDatatable = function ( initialValue ) {
        $.fn.dataTable.moment( 'MM/DD/YYYY' );

        dt = $("#area_datatable").DataTable({
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
              url: '/areas/filter_areas',
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
              { data: 'ar_id' },
              { data: 'name' },
              { data: 'num_blocks' },
              { data: 'num_projects' },
              { data: 'area_type',
                render: function (val, type, row) {
                  return row["area_type_label"];
                }
              },
              { data: 'completion_date',
                render: function (data) {
                  return moment(data).format('MM/DD/YYYY');
                }
              },
              { data: 'investigator' },
              { data: 'num_nucacids' },
              { data: 'num_samplelibs' },
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
                    targets: 2,
                    orderable: false,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let ar_id = row["ar_id"];
                          return `
                              <a href="/blocks?model=area&id=${ar_id}&initial=true">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 3,
                    orderable: true,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let ar_id = row["ar_id"];
                          return `
                              <a href="/projects?model=area&id=${ar_id}&initial=true">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 7,
                    orderable: true,
                    className: "text-center",
                    render: function (data, type, row) {
                        if (data > 0) {
                          let ar_id = row["ar_id"];
                          return `
                              <a href="/libprep?model=area&id=${ar_id}&initial=true">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 8,
                    orderable: true,
                    className: "text-center",
                    render: function (data, type, row) {
                        if (data > 0) {
                          let id = row["ar_id"];
                          return `
                              <a href="/samplelib?model=area&id=${id}&initial=true">${data}</a>`;
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
                                <div class="menu-item px-3">
                                    <a href="/areas/edit/`+ row["ar_id"] +`" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        Edit
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/areas/delete/` + row["ar_id"] +`" class="menu-link px-3" data-kt-docs-table-filter="delete_row">
                                        Delete
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="#" class="menu-link px-3 variant-link">View Variants</a>
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
            handleRowActions();
            KTMenu.createInstances();
        });
    }

    var initRowSelection = function () {
        // Select all checkboxes
        const allCheckboxes = document.querySelectorAll('#area_datatable tbody [type="checkbox"]');
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
        const allCheckboxes = document.querySelectorAll('#area_datatable tbody [type="checkbox"]');
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

    // Delete area
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
                    url: "/areas/check_can_deleted_async",
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
                                    text: "Area deleted succesfully.",
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
    var handleBatchDeleteRows = function () {
        // Toggle selected action toolbar
        // Select all checkboxes
        const container = document.querySelector('#area_datatable');
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
                            url: "/areas/batch_delete",
                            data: {
                              "selected_ids": JSON.stringify(selectedRows),
                            },
                            error: function (xhr, ajaxOptions, thrownError) {
                                swal("Error deleting!", "Please try again", "error");
                            }
                        }).done(function (result) {
                            if (result.deleted) {
                              Swal.fire({
                                  text: "Area(s) deleted succesfully.",
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
                                  text: "Area(s) could not be deleted!",
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

    // Functions in selected rows
    var handleSelectedRows = function (e) {
        const nucleicAcidModal = document.getElementById("modal_extract_nucleic_acid");
        const nucleicAcidInstance = new bootstrap.Modal(nucleicAcidModal);

        const btnExtractNucleicAcid = document.querySelector('[data-kt-docs-table-select="event_extract_nucleic_acid"]');
        const btnNucleicAcidContinue = document.getElementById("btn_continue");

        function getFormOptions(formId) {
            var data = new FormData(document.getElementById(formId));
            var options = Object.fromEntries(data.entries());
            return JSON.stringify(options);
        }

        function handleSuccess(message) {
            Swal.fire({
                text: message,
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

        function handleError(message) {
            Swal.fire({
                text: message,
                icon: "error",
                buttonsStyling: false,
                confirmButtonText: "Ok, got it!",
                customClass: {
                    confirmButton: "btn fw-bold btn-danger",
                }
            });
        }

        btnExtractNucleicAcid.addEventListener('click', () => nucleicAcidInstance.show());
        btnNucleicAcidContinue.addEventListener('click', function () {
            $.ajax({
                type: "GET",
                url: "/libprep/new_async",
                data: {
                    "selected_ids": JSON.stringify(selectedRows),
                    "options": getFormOptions('frm_extraction_options')
                },
            }).done(function(result) {
                if (result.success) {
                    handleSuccess("Nucleic acid(s) created successfully.");
                } else {
                    handleError("Area(s) could not be created.");
                }
                nucleicAcidInstance.hide();
            });
        });
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

        function getVariantData( area_id ) {
            fetch(`/variant/get_variants_by_area?area_id=${area_id}`)
                .then(response => response.json())
                .then(data => {
                    initializeModal(data);
                    $('#variant_layout').modal('show');
                });
        }

        function initializeModal(data) {
            // Initialize tabs
            const tabContainer = document.getElementById('variantTabList');
            const tabContent = document.getElementById('variantTabContent');

            // Clear modal first
            tabContainer.innerHTML = "";
            tabContent.innerHTML = "";

            // Fill the data
            populateAreaDetails(data.area);

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

        function populateAreaDetails( data ) {
            document.querySelector('input[name="area_name"]').value = data.name;
            document.querySelector('input[name="block_name"]').value = data.block_name;
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
                <div class="card card-flush py-4 flex-row-fluid overflow-hidden">
                    <div class="card-body pt-0">
                        <div class="table-responsive">
                            <table id="variant_datatable_${id}" class="table align-middle table-row-dashed fs-6 gy-5">
                                <thead>
                                    <tr class="text-start text-gray-400 fw-bold fs-7 text-uppercase gs-0">
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

    }

    // Toggle toolbars
    var toggleToolbars = function () {
        // Define variables
        const container = document.querySelector('#area_datatable');
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

    // Provides the datatable to be fully editable. official docs for more info  --> https://editor.datatables.net
    var initEditor = function () {

      var areaTypeOptions = [];

      Promise.all([

        getAreaTypeOptions()

      ]).then(function () {

        editor = new $.fn.dataTable.Editor({
        ajax: {
          url: "/areas/edit_area_async",
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
        table: "#area_datatable",
        fields: [
            {
             label: "Name:",
             name: "name"
            }, {
              label: "Block",
              name: "num_blocks",
              type: "readonly",
              attr: { disabled:true }
            }, {
              label: "Project",
              name: "num_projects",
              type: "readonly",
              attr: { disabled:true }
            }, {
              label: "Area Type:",
              name: "area_type",
              type: "select",
              options: areaTypeOptions
            }, {
              label: "Completion Date:",
              name: "completion_date",
              type: "datetime",
              displayFormat: "M/D/YYYY",
              wireFormat: 'YYYY-MM-DD'
            }, {
              label: "Investigator:",
              name: "investigator",
              type: "readonly",
              attr: { disabled:true }
          }, {
            label: "Nucleic Acids",
            name: "num_nucacids",
            type: "readonly",
            attr: { disabled:true }
          }, {
            label: "Sample Libraries",
            name: "num_samplelibs",
            type: "readonly",
            attr: { disabled:true }
          },
       ],
       formOptions: {
          inline: {
            onBlur: 'submit'
          }
       }
     });

      });

      $('#area_datatable').on( 'click', 'tbody td:not(:first-child)', function (e) {
        editor.inline( dt.cell( this ).index(), {
            onBlur: 'submit'
        } );
      } );

      $('#area_datatable').on( 'key-focus', function ( e, datatable, cell ) {
        editor.inline( cell.index() );
      });

      // Gets the area type options and fills the dropdown. It is executed synchronous.
      function getAreaTypeOptions() {

        $.ajax({
            url: "/areas/get_area_types",
            type: "GET",
            async: false,
            success: function (data) {

              data.forEach((item, i) => {

               areaTypeOptions.push({
                 "label":item["label"],
                 "value":item["value"]
               })

             });
            }
        });
      }

      // Gets the collection options and fills the dropdown. It is executed synchronous.
      function getCollectionOptions() {

        $.ajax({
            url: "/areas/get_collections",
            type: "GET",
            async: false,
            success: function (data) {

             data.forEach((item, i) => {

               collectionOptions.push({
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
    // Public methods
    return {
        init: function () {
            initDatatable( handleInitialValue() );
            handleSearchDatatable();
            handleBatchDeleteRows();
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
