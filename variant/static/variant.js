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
    var initDatatable = function (
        initialValue,
        filterPatient,
        filterArea,
        filterBlock,
        filterSampleLib,
        filterSequencingRun,
        filterCoverage,
        filterLog2r,
        filterRefRead,
        filterAltRead,
        filterVariant,
        filterVariantFile
        ) {

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
              url: '/variant/filter_variants',
              type: 'GET',
              data:{
                "patient": filterPatient,
                "area": filterArea,
                "block": filterBlock,
                "sample_lib": filterSampleLib,
                "sequencing_run":filterSequencingRun,
                "coverage": filterCoverage,
                "log2r": filterLog2r,
                "ref_read": filterRefRead,
                "alt_read": filterAltRead,
                "variant": filterVariant,
                "variant_file": filterVariantFile
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
                { data: 'chrom' },
                { data: 'start' },
                { data: 'ref' },
                { data: 'alt' },
                { data: 'patients' },
                { data: 'areas' },
                { data: 'blocks' },
                { data: 'sample_libs' },
                { data: 'sequencing_runs' },
                { data: 'genes' },
                { data: 'cosmic_gene_symbol' },
                { data: 'cosmic_aa' },
                { data: 'cosmic_primary_site_counts' },
                { data: 'total_calls' },
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
                    // Patients column (index 5) - expects array of [id, name] tuples
                    targets: 5,
                    render: function (data, type, row) {
                        if (!data || !Array.isArray(data)) return '';
                        return data.map(function(patient) {
                            if (patient) {
                              var patientId = patient["id"]; // id
                              var patientName = patient["name"]; // name
                              return `<a href="/patients/edit/${patientId}" class="text-primary">${patientName}</a>`;
                            }
                        }).join(', ');
                    }
                },
                {
                    // Areas column (index 6) - expects array of [id, name] tuples
                    targets: 6,
                    render: function (data, type, row) {
                        if (!data || !Array.isArray(data)) return '';
                        return data.map(function(area) {
                            var areaId = area["id"]; // id
                            var areaName = area["name"]; // name
                            return `<a href="/areas/edit/${areaId}" class="text-primary">${areaName}</a>`;
                        }).join(', ');
                    }
                },
                {
                    // Blocks column (index 7) - expects array of [id, name] tuples
                    targets: 7,
                    render: function (data, type, row) {
                        if (!data || !Array.isArray(data)) return '';
                        return data.map(function(block) {
                            var blockId = block["id"]; // id
                            var blockName = block["name"]; // name
                            return `<a href="/blocks/edit/${blockId}" class="text-primary">${blockName}</a>`;
                        }).join(', ');
                    }
                },
                {
                    // Sample libraries column (index 8) - expects array of [id, name] tuples
                    targets: 8,
                    render: function (data, type, row) {
                        if (!data || !Array.isArray(data)) return '';
                        return data.map(function(sampleLib) {
                            var sampleLibId = sampleLib["id"]; // id
                            var sampleLibName = sampleLib["name"]; // name
                            return `<a href="/samplelib/edit/${sampleLibId}" class="text-primary">${sampleLibName}</a>`;
                        }).join(', ');
                    }
                },
                {
                    // Sequencing runs column (index 9) - expects array of [id, name] tuples
                    targets: 9,
                    render: function (data, type, row) {
                        if (!data || !Array.isArray(data)) return '';
                        return data.map(function(seqRun) {
                            if (seqRun) {
                              var seqRunId = seqRun["id"]; // id
                              var seqRunName = seqRun["name"]; // name
                              return `<a href="/sequencingrun/edit/${seqRunId}" class="text-primary">${seqRunName}</a>`;
                            }
                        }).join(', ');
                    }
                },
                {
                    // Genes column (index 10) - expects array of [id, name] tuples
                    targets: 10,
                    render: function (data, type, row) {
                        if (!data || !Array.isArray(data)) return '';
                        return data.map(function(gene) {
                            if (gene) {
                              var geneId = gene["id"]; // id
                              var geneName = gene["name"]; // name
                              return `<a href="/gene/edit/${geneId}" class="text-primary">${geneName}</a>`;
                            }
                        }).join(', ');
                    }
                },
                {
                  // gene symbol columns
                  targets: 11,
                  className: 'text-center'
                },
                {
                  // cosmic aa columns
                  targets: 12,
                  className: 'text-center'
                },
                {
                    // Primary sites columns
                    targets: 13,
                    className: 'text-center'
                },
                {
                    // Total calls columns
                    targets: 14,
                    className: 'text-center'
                },
               {
                    targets: -1,
                    data: null,
                    orderable: false,
                    className: 'text-end',
                    render: function (data, type, row) {
                        return `
                            <a href="#" class="btn btn-light btn-active-light-primary btn-sm" data-kt-menu-trigger="click" data-kt-menu-placement="bottom-end" data-kt-menu-flip="top-end">
                                Site Details
                                <span class="svg-icon svg-icon-5 m-0">
                                    <!-- svg content here -->
                                </span>
                            </a>
                            <!--begin::Menu-->
                            <div class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-600 menu-state-bg-light-primary fw-bold fs-7 w-125px py-4" data-kt-menu="true">
                                <div class="menu-item px-3">
                                    <a href="#" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        ${row.primary_site_count_detail ?? ''}
                                    </a>
                                </div>
                            </div>
                            <!--end::Menu-->
                        `;
                    }
                }
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
            // initRowActions();
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

        const filterButton = document.querySelector('[data-kt-docs-table-filter="filter"]');

        // Filter datatable on submit
        filterButton.addEventListener('click', function () {

          var patient = document.getElementById("id_patient").value;
          var sequencingRun = document.getElementById("id_sequencing_run").value
          var sampleLib = document.getElementById("id_sample_lib").value;
          var area = document.getElementById("id_area").value;
          var block = document.getElementById("id_block").value;
          var coverage = document.getElementById("id_coverage").value;
          var log2r = document.getElementById("id_log2r").value;
          var refRead = document.getElementById("id_ref_read").value;
          var altRead = document.getElementById("id_alt_read").value;
          var variant = document.getElementById("id_variant").value;
          var variant_file = document.getElementById("id_variant_file").value;

          console.log(sampleLib);

          // DataTable'ı başlat
          initDatatable(null, patient, area, block, sampleLib, sequencingRun ,coverage, log2r, refRead, altRead, variant, variant_file);

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

            document.getElementById("id_patient").value = "";
            document.getElementById("id_sequencing_run").value= ""
            document.getElementById("id_sample_lib").value = "";
            document.getElementById("id_area").value = "";
            document.getElementById("id_block").value = "";
            document.getElementById("id_coverage").value = "";
            document.getElementById("id_log2r").value = "";
            document.getElementById("id_ref_read").value = "";
            document.getElementById("id_alt_read").value = "";
            document.getElementById("id_variant_file").value = "";

            initDatatable(null ,null ,null ,null,null,null,null,null,null,null,null,null);
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
                                  // clean selected rows
                                  selectedRows = [];
                                  // refresh dataTable
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
          handleBatchDelete(), uncheckedFirstCheckBox();
        }
      }

    })();

    var initRowActions = () => {

      const el = document.getElementById("modal_used_sequencinglibs");
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
              <div class="col-6 align-self-center" data-id="${ data[i].id }"><a href="/sequencinglib/edit/${ data[i].id }">${ data[i].name }</a></div>
              <div class="col-3 align-self-center">${ data[i].buffer }</div>
              <div class="col-3 align-self-center text-center">${ data[i].nmol }</div>
            </div>`;
          listEl.innerHTML += row;

        }

      }

    }

    // Public methods
    return {
        init: function () {
            initDatatable( handleInitialValue() ,null,null,null,null,null,null,null,null,null,null,null);
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
