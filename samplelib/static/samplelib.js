"use strict";

// Class definition
var KTDatatablesServerSide = function () {
    // Shared variables
    var table;
    var dt;
    var filterPayment;
    var editor;
    var selectedRows = [];
    var selectedSampleLibs = [];

    // Private functions
    var initDatatable = function ( initialValue, filterSequencingRun, filterBarcode, filterI5, filterI7, filterAreaType, filterBait ) {
        $.fn.dataTable.moment( 'MM/DD/YYYY' );

        dt = $(".table").DataTable({
            // searchDelay: 500,
            processing: true,
            serverSide: true,
            order: [[0, 'desc']],
            stateSave: false,
            destroy: true,
            pageLength: 10,
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
              url: '/samplelib/filter_samplelibs',
              type: 'GET',
              data :{
                "sequencing_run": filterSequencingRun,
                "barcode": filterBarcode,
                "i5": filterI5,
                "i7": filterI7,
                "area_type": filterAreaType,
                "bait": filterBait
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
                { data: 'name' },
                { data: 'area_num' },
                { data: 'date',
                  render: function (data) {
                    return moment(data).format('MM/DD/YYYY');
                  }
                },
                { data: 'num_files' },
                { data: 'qpcr_conc' },
                { data: 'vol_init' },
                { data: 'amount_final' },
                { data: 'pcr_cycles' },
                { data: 'qubit' },
                { data: 'amount_in' },
                { data: 'vol_remain' },
                { data: 'num_blocks' },
                { data: 'num_nucacids' },
                { data: 'num_capturedlibs' },
                { data: 'barcode' },
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
                    orderable: true,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let sl_id = row["id"];
                          return `
                              <a href="/areas?model=sample_lib&id=${sl_id}&initial=true">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 4,
                    orderable: true,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let sl_id = row["id"];
                          return `
                              <a href="/sequencingfile?id=${sl_id}&initial=true&model=sample_lib">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 12,
                    orderable: false,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let id = row["id"];
                          return `
                              <a href="/blocks?model=samplelib&id=${id}&initial=true">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 13,
                    orderable: false,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let id = row["id"];
                          return `
                              <a href="/libprep?model=sample_lib&id=${id}&initial=true">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 14,
                    orderable: false,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let id = row["id"];
                          return `
                              <a href="/capturedlib?initial=${id}">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 16,
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
                                    <a href="/samplelib/edit/`+ row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        Edit
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-2">
                                    <a href="javascript:;" class="menu-link px-3 detail-link" data-kt-docs-table-filter="detail_row">
                                        Used Nucacids(s)
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/samplelib/delete/` + row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="delete_row">
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
            handleResetFilter();
            initModal();
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
                toggleSelectedSampleLibs(c.closest("tr").querySelector("td:nth-child(2)").textContent.trim());
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

        function toggleSelectedSampleLibs(name) {
            var index = selectedSampleLibs.indexOf(name);
            if (index === -1) {
                // If the row is not selected, add it to selected rows
                selectedSampleLibs.push(name);
            } else {
                // If the row is already selected, remove it in selected rows
                selectedSampleLibs.splice(index, 1);
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

          var sequencingRun = document.getElementById("id_sequencing_run").value;
          var barcode = document.getElementById("id_barcode").value;
          var i5 = document.getElementById("id_i5").value;
          var i7 = document.getElementById("id_i7").value;
          var areaType = document.getElementById("id_area_type").value;
          var bait = document.getElementById("id_bait").value;

          initDatatable(null,sequencingRun,barcode,i5,i7,areaType,bait);

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
                    url: "/samplelib/check_can_deleted_async",
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
                                    text: "Sample Library deleted succesfully.",
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
    var handleResetFilter = () => {
        // Select reset button
        const resetButton = document.querySelector('[data-kt-docs-table-filter="reset"]');

        // Reset datatable
        resetButton.addEventListener('click', function () {

          document.getElementById("id_sequencing_run").value="";
          document.getElementById("id_barcode").value="";
          document.getElementById("id_i5").value="";
          document.getElementById("id_i7").value="";
          document.getElementById("id_area_type").value="";
          document.getElementById("id_bait").value="";

          initDatatable(null, null, null, null, null, null, null);

        });
    }

    // Init toggle toolbar
    var handleBatchDeleteRows = function () {
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

      var methodOptions = [];

      Promise.all([

        getMethodOptions()

      ]).then(function () {

        editor = new $.fn.dataTable.Editor({
        ajax: {
          url: "/samplelib/edit_samplelib_async",
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
               label: "Barcode:",
               name: "barcode"
           }, {
               label: "Date:",
               name: "date",
               type: "datetime",
               displayFormat: "M/D/YYYY",
               wireFormat: 'YYYY-MM-DD'
           }, {
               label: "Method:",
               name: "method",
               type: "select",
               options: methodOptions
           }, {
               label: "Concentration:",
               name: "qpcr_conc"
           }, {
               label: "PCR Cycles:",
               name: "pcr_cycles"
           }, {
               label: "Qubit:",
               name: "qubit"
           }, {
               label: "Input Amount:",
               name: "amount_in",
               type: "readonly"
           }, {
               label: "Final Amount:",
               name: "amount_final",
               type: "readonly"
           }, {
               label: "Volume Init:",
               name: "vol_init"
           }, {
               label: "Volume Remain:",
               name: "vol_remain"
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

       function getMethodOptions() {

         $.ajax({
             url: "/method/get_methods",
             type: "GET",
             async: false,
             success: function (data) {

              // var options = [];
              data.forEach((item, i) => {

                methodOptions.push({
                  "label":item["name"],
                  "value":item["id"]
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

    var handleModalQPCRAnalysis = ((e) => {
        const container = document.querySelector('.table');
        const modalQPCRAnalysis = new bootstrap.Modal(document.getElementById("modal_qpcr_analysis"));
        const modalBody = document.querySelector("#modal_qpcr_analysis .modal-body .card-body");
        const btnExport = document.querySelector("button[name='btnExport']");
        const btnDismiss = document.querySelector("button[name='btnDismiss']");
        var sampleLibs = [];

        document.getElementById("qpcr_analysis").addEventListener("click", function () {
            // var selectedItems = Array.from(container.querySelectorAll('[type="checkbox"]:checked'));
            if (selectedSampleLibs.length > 0) {
                const modalBody = document.querySelector("#modal_qpcr_analysis .modal-body .card-body");
                var ul = modalBody.querySelector("ul");
                // if modalBody does not contain a <ul> element, then create it
                if (!ul) {
                    ul = document.createElement("ul");
                }

                // Get existing items in the list
                var existingItems = modalBody.querySelectorAll("ul li");

                // Array to store the names of existing items
                var existingSampleLibs = Array.from(existingItems).map(item => item.textContent.trim());
                // Remove items from the list that are not in the selectedItems array
                existingItems.forEach(existingItem => {
                    var existingItemName = existingItem.textContent.trim();
                    if (!selectedSampleLibs.some(item => item === existingItemName)) {
                        existingItem.remove();
                    }
                });

                // Add new selected items to the list
                for (var name of selectedSampleLibs) {
                    if (!existingSampleLibs.includes(name)) {
                        var li = document.createElement("li");
                        li.textContent = name;
                        ul.appendChild(li);
                    }
                }

                // Append the updated list to the modal body
                modalBody.innerHTML = ""; // Clear the modal body first
                modalBody.appendChild(ul);
                enableExportButton();
            } else {
                // Clear the modal body if there are no selected items
                modalBody.innerHTML = "";
            }

            modalQPCRAnalysis.show();
        });

        btnDismiss.addEventListener("click", function () {
            modalBody.innerHTML = "";
            disableExportButton();
        });

        btnExport.addEventListener("click", function () {
            exportToCSV();
            modalQPCRAnalysis.hide();
            clearSelectedItems();
        });

        function enableExportButton() {
            btnExport.disabled = false;
        }

        function disableExportButton() {
            btnExport.disabled = true;
        }

        function clearSelectedItems() {

        }

        function exportToCSV() {
            // create content from data
            var content = initialContent();
            // create csv data
            var csvData = arrayToCSV(content);
            // generate a file name according to some rules
            var fileName = generateFileName();
            // Call the function to download the CSV data
            downloadCSV(csvData, fileName);
        }

        function initialContent() {
            var cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
            var rows = ["A", "B", "C", "D", "E", "F", "G", "H"];
            var constantData = ["STD 1", "STD 2", "STD 3", "STD 4", "STD 5", "STD 6", "NTC", "EMPTY"];
            for (var i = 1; i <= 36; i++) {
                sampleLibs.push("Sample Library " + i);
            }

            // var sampleLibs = Array.from(modalBody.querySelectorAll("ul li")).map(item => item.textContent.trim());

            // Let's create groups of 8
            // var groupedSampleLibs = [];
            // for (var j = 0; j < sampleLibs.length; j += 8) {
            //     groupedSampleLibs.push(sampleLibs.slice(j, j + 8));
            // }

            function splitToGroups(veri, maxGrupSayisi) {
                var gruplar = new Array(maxGrupSayisi).fill().map(() => []);
                for (var i = 0; i < veri.length; i++) {
                    var grupIndex = i % maxGrupSayisi;
                    gruplar[grupIndex].push(veri[i]);
                }
                return gruplar;
            }

            var groupedSampleLibs = splitToGroups(sampleLibs, 8);

            console.log(groupedSampleLibs);
            // Let's duplicate grouped selected items without last one
            var extendedSampleLibs = [];
            for (var i = 0; i < groupedSampleLibs.length -1; i++) {
                // copy array
                var duplicatedSubArray = groupedSampleLibs[i].slice();

                // insert the new array to extendedSampleLibs twice
                extendedSampleLibs.push(duplicatedSubArray);
                extendedSampleLibs.push(duplicatedSubArray);
            }

            // The order of the last row on the plate is different from the others
            if (groupedSampleLibs.length == 8) {
                // Duplicate the elements of the last group and make them into consecutive double elements
                var lastGroupIndex = groupedSampleLibs.length - 1;
                var lastGroup = groupedSampleLibs[lastGroupIndex];
                var tmp = [];

                lastGroup.forEach(function(item) {
                    tmp.push(item, item);
                });

                extendedSampleLibs.push(tmp);
            }
            else {
                extendedSampleLibs = groupedSampleLibs;
            }

            console.log(extendedSampleLibs);
            // Add the ConstantData array to the beginning of extendSelectedItems three times
            for (var i = 0; i < 3; i++) {
                extendedSampleLibs.unshift(constantData);
            }

            // create a matrix from cols and rows
            var matrix = [];
            for (var i = 0; i < rows.length; i++) {
                var row = [];
                for (var j = 0; j < cols.length; j++) {
                    row.push(rows[i] + cols[j]);
                }
                matrix.push(row);
            }
            console.log(matrix);
            // Pair the matrix and data
            var mergedArray = [];
            for (var i = 0; i < matrix.length; i++) {
                var arrayA = matrix[i];
                var mergedSubArray = [];
                for (var j = 0; j < extendedSampleLibs.length; j++) {
                    mergedSubArray.push([arrayA[j], extendedSampleLibs[j][i]]);
                }
                mergedArray.push(mergedSubArray);
            }
            console.log(mergedArray);

            return mergedArray;
        }

        function arrayToCSV(array) {
            var csv = '';

            // Iterate over each row in the array
            array.forEach(function(row) {
                // Iterate over each element in the row
                row.forEach(function(pair) {
                    // Append the element to the CSV string
                    csv += pair.join(',') + '\n';
                });
            });

            return csv;
        }

        function downloadCSV(csvData, fileName) {
            // Create a Blob object from the CSV data
            var blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });

            // Create a temporary link element
            var link = document.createElement('a');
            if (link.download !== undefined) { // feature detection
                // Set the download attribute of the link
                var url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', fileName);

                // Append the link to the document body
                document.body.appendChild(link);

                // Click the link programmatically to trigger the download
                link.click();

                // Remove the link from the document body
                document.body.removeChild(link);
            } else {
                console.error('Your browser does not support downloading files programmatically. Please try another browser.');
            }
        }

        function generateFileName() {
            // qPCR_analysis should have the following format: DATE-SLprefix.
            // Date should be MMDDYY. SLprefix are any letters before the SL.name (e.g. AMLP for SLs named AMLP-1 etc.., e.g. 040224-AMLP.
            // If there are SLs with different prefixes e.g. AMLP-1 and SGP-123, use all prefixes for qPCR_analysis (e.g. 040224-AMLP+SGP).
            // Get the current date and format it as MMDDYY
            const today = new Date();
            const date = today.toLocaleDateString('en-US', {
                month: '2-digit',
                day: '2-digit',
                year: '2-digit'
            }).replace(/\//g, ''); // remove slashes

            // Extract SL prefixes
            const prefixes = new Set();
            for (const slName of sampleLibs) {
                const prefix = slName.split('-')[0]; // Get the prefix before the dash
                prefixes.add(prefix);
            }

            // Combine prefixes
            const prefixString = [...prefixes].sort().join('+');

            // Combine date and prefixes
            const fileName = `${date}-${prefixString}.csv`;
            return fileName;
            // return "deneme.csv"
        }
    })();

    var handleSelectedRows = ((e) => {
      const container = document.querySelector('.table');
      const modal = new bootstrap.Modal(document.getElementById("modal_capturedlib_options"));
      const modalCL = new bootstrap.Modal(document.getElementById("add_to_captured_library"));

      document.getElementById("create_captured_lib").addEventListener('click', function (e) {

          Swal.fire({
              title: "<h3 style='color:dodgerblue'>" + "Add to an existing Captured Library?" + "</h3>",
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
                    modalCL.show();
              } else if (result.isDenied) {
                  modal.show();
              }
          });
      });

      document.getElementById("modal_capturedlib_options").addEventListener('show.bs.modal', function(e){
        if (!checkSelectedRows()) {

          Swal.fire({
              text: "Identical barcodes are used in selected rows.",
              icon: "error",
              buttonsStyling: false,
              confirmButtonText: "Ok, got it!",
              customClass: {
                  confirmButton: "btn fw-bold btn-primary",
              }
          });

          return e.preventDefault()
        }

      });

      document.getElementById("add_to_captured_library").addEventListener('show.bs.modal', function(e){
        if (!checkSelectedRows()) {

          Swal.fire({
              text: "Identical barcodes are used in selected rows.",
              icon: "error",
              buttonsStyling: false,
              confirmButtonText: "Ok, got it!",
              customClass: {
                  confirmButton: "btn fw-bold btn-primary",
              }
          });

          return e.preventDefault()
        }

      });

      document.getElementById("modal_capturedlib_options").addEventListener('hide.bs.modal', function(e){

        resetForm();

        dt.draw();

      });

      function resetForm() {

        document.getElementById("frm_creation_options").reset();

      }

      function getCreationOptions() {

        var data = new FormData(document.getElementById('frm_creation_options'));
        var options = Object.fromEntries(data.entries());

        return JSON.stringify(options);
      }

      function checkSelectedRows() {
        var selectedRows = container.querySelectorAll('[type="checkbox"]:checked');
        var barcodeList = [];
        for (let row of selectedRows) {
          const parent = row.closest('tr');
          // Get barcode
          const barcode = parent.querySelectorAll('td')[15].innerText;
          if (barcodeList.indexOf(barcode) > -1 ) {
            return false;
          }
          barcodeList.push(barcode);
        }
        return true;
      }

      document.getElementById("btn_add_continue").addEventListener('click', function () {
          var selectElement = document.getElementById("id_captured_lib").value;
        const modalElement = document.getElementById("add_to_captured_library"); // Replace "currentlyOpenModalID" with the ID of the modal that might be open
        // const modal_cl = new bootstrap.Modal(modalElement);
        // modal_cl.show();
          $.ajax({
            url: "/samplelib/add_async",
            type: "GET",
            data: {
              "id": selectElement,
              "selected_ids": JSON.stringify(selectedRows)
            },
          }).done(function(result) {

            if (result.success) {
              Swal.fire({
                  text: "Sample Library(s) added succesfully.",
                  icon: "info",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                      confirmButton: "btn fw-bold btn-success",
                  }
              })
            }
            else {
              Swal.fire({
                  text: `Sample Library(s) could not added ${result.message}`,
                  icon: "error",
                  buttonsStyling: false,
                  confirmButtonText: "Ok, got it!",
                  customClass: {
                      confirmButton: "btn fw-bold btn-danger",
                  }
              })
            };
            modalCL.show();
            modalCL.hide();
            dt.draw();
          });

        });

      document.getElementById("btn_continue").addEventListener('click', function () {

        $.ajax({
          type: "GET",
          url: "/capturedlib/new_async",
          data: {
            "selected_ids": JSON.stringify(selectedRows),
            "options": getCreationOptions()
          },
        }).done(function(result) {
          if (result.success) {
            Swal.fire({
                text: "Captured Library(s) created succesfully.",
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
                text: "Captured Library(s) could not be created.",
                icon: "error",
                buttonsStyling: false,
                confirmButtonText: "Ok, got it!",
                customClass: {
                    confirmButton: "btn fw-bold btn-danger",
                }
            });
          }

          modal.hide()

        });

      });

      document.getElementById("id_prefix").addEventListener("keyup", function () {

        this.value = this.value.toLocaleUpperCase();

      });

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

                    Swal.fire({
                        text: "Deleting selected records",
                        icon: "info",
                        buttonsStyling: false,
                        showConfirmButton: false,
                        timer: 2000
                    }).then(function () {

                        $.ajax({
                            type: "GET",
                            url: "/samplelib/batch_delete",
                            data: {
                              "selected_ids": JSON.stringify(selectedRows),
                            },
                            error: function (xhr, ajaxOptions, thrownError) {
                                swal("Error deleting!", "Please try again", "error");
                            }
                        }).done(function (result) {
                            if (result.deleted) {
                              Swal.fire({
                                  text: "Sample Library(s) deleted succesfully.",
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
                                  text: "Sample Library(s) could not be deleted!",
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

      return {
        init: function () {
          handleBatchDelete(), uncheckedFirstCheckBox();
        }
      }

    })();

    var initModal = () => {

      var el = document.getElementById("modal_used_nacacids");
      var modal = new bootstrap.Modal(el);

      el.addEventListener('hide.bs.modal', function(){

        closeModal();

      });

      function openModal(id,data) {

        var listEl = document.querySelector(".list-body");

        for (var i = 0; i < data.length; i++) {

          var row = `<div class="row m-1">
            <div class="col-3"><a href="/samplelib/edit/${ data[i].sample_lib_id }">${ data[i].sample_lib_name }</a></div>
            <div class="col-5"><a href="/libprep/edit/${ data[i].nucacid_id }">${ data[i].nucacid_name }</a></div>
            <div class="col-2 text-center">${ data[i].input_vol }</div>
            <div class="col-2 text-center">${ data[i].input_amount }</div>
          </div>
          `;

          listEl.innerHTML += row;
        }

        modal.show();

      }

      function closeModal() {

        var listEl = document.querySelector(".list-body");

        listEl.innerHTML = "";

        // modal.hide();

      }

      const detailLinks = document.querySelectorAll(".detail-link");

      for (var detail of detailLinks) {

        detail.addEventListener("click", function (e) {
          e.preventDefault();
          // Select parent row
          const parent = this.closest('tr');
          // Get customer name
          const id = parent.querySelector('input[type=checkbox]').value;

          $.ajax({
              url: "/samplelib/" + id + "/used_nucacids",
              type: "GET",
              success: function (data) {

                openModal(id,data);

              },
              error: function (xhr, ajaxOptions, thrownError) {

              }
          });

        });

      }
    }

    // Public methods
    return {
        init: function () {
            initDatatable( handleInitialValue(), null, null, null, null, null, null );
            handleSearchDatatable();
            handleBatchDeleteRows();
            handleFilterDatatable();
            handleDeleteRows();
            handleResetFilter();
            initEditor();
        }
    }
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesServerSide.init();
});
