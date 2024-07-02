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
              url: '/capturedlib/filter_capturedlibs',
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
                { data: 'bait',
                  render: function (val, type, row) {
                    return row["bait_label"];
                  }
                },
                { data: 'frag_size' },
                { data: 'conc' },
                { data: 'amp_cycle' },
                { data: 'buffer',
                  render: function (val, type, row) {
                    return row["buffer_label"];
                  }
                },
                { data: 'nm' },
                { data: 'vol_init' },
                { data: 'vol_remain' },
                { data: 'amount' },
                { data: 'pdf' },
                { data: 'num_samplelibs' },
                { data: 'num_sequencinglibs' },
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
                    targets: 11,
                    orderable: false,
                },
                {
                    targets: 12,
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
                    targets: 13,
                    orderable: false,
                    render: function (data, type, row) {
                        if (data > 0) {
                          let id = row["id"];
                          return `
                              <a href="/samplelib?model=captured_lib&id=${id}&initial=true">${data}</a>`;
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
                          return `<a href="/sequencinglib?model=captured_lib&initial=true&id=${id}">${data}</a>`;
                        }
                        return data;
                    }
                },
                {
                    targets: 15,
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
                                    <a href="/capturedlib/edit/`+ row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="edit_row">
                                        Edit
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-2">
                                    <a href="javascript:;" class="menu-link px-3 detail-link" data-kt-docs-table-filter="detail_row">
                                        Used Library(s)
                                    </a>
                                </div>
                                <!--end::Menu item-->

                                <!--begin::Menu item-->
                                <div class="menu-item px-3">
                                    <a href="/capturedlib/delete/` + row["id"] +`" class="menu-link px-3" data-kt-docs-table-filter="delete_row">
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
                    url: "/capturedlib/check_can_deleted_async",
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
                                    text: "Captured Library deleted succesfully.",
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

      var baitOptions = [];
      var bufferOptions = [];

      Promise.all([

          getBaitOptions(),
          getBufferOptions()

      ]).then(() => {

        editor = new $.fn.dataTable.Editor({
          ajax: {
            url: "/capturedlib/edit_capturedlib_async",
            type: "POST",
            headers: {'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value },
            success: function (result) {
                if (!result.success) {
                  Swal.fire({
                      text: "Error occurred during data update.",
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
                 displayFormat: 'M/D/YYYY',
                 wireFormat: 'YYYY-MM-DD',
             }, {
                 label: "Bait:",
                 name: "bait",
                 type: "select",
                 options: baitOptions,
             }, {
                 label: "Fragment Size:",
                 name: "frag_size"
             }, {
                 label: "Concentration:",
                 name: "conc"
             }, {
                 label: "AMP Cycle:",
                 name: "amp_cycle"
             }, {
                 label: "Buffer:",
                 name: "buffer",
                 type: "select",
                 options: bufferOptions,
             }, {
                 label: "Volume Init:",
                 name: "vol_init"
             }, {
                 label: "Volume Remain:",
                 name: "vol_remain"
             }, {
                 label: "Amount:",
                 name: "amount",
                 type: "readonly"
             },
         ],
         formOptions: {
            inline: {
              onBlur: 'submit'
            }
         }
       });

      }).catch((err) => {
          console.log(err);
      });

      function  getBaitOptions() {

        $.ajax({
            url: "/bait/get_bait_choices",
            type: "GET",
            async: false,
            success: function (data) {

             // var options = [];
             data.forEach((item, i) => {

               baitOptions.push({
                 "label":item["name"],
                 "value":item["id"]
               })

             });

             // editor.field( 'bait' ).update( options );

            }
        });

      }

      function  getBufferOptions() {

        $.ajax({
            url: "/buffer/get_buffer_choices",
            type: "GET",
            async: false,
            success: function (data) {

             // var options = [];
             data.forEach((item, i) => {

               bufferOptions.push({
                 "label":item["name"],
                 "value":item["id"]
               })

             });

             // editor.field( 'buffer' ).update( options );

            }
        });

      }

      $('.table').on( 'click', 'tbody td:not(:first-child)', function (e) {
           editor.inline( this );
      });

      $('.table').on( 'key-focus', function ( e, datatable, cell ) {
           editor.inline( cell.index() );
      });

    }
    function wait(ms){
       var start = new Date().getTime();
       var end = start;
       while(end < start + ms) {
         end = new Date().getTime();
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

    var initRowActions = () => {

      const el = document.getElementById("modal_used_samplelibs");
      const modal = new bootstrap.Modal(el);

      initModal();

      function initModal() {

        el.addEventListener('hide.bs.modal', function(){

          var listEl = document.querySelector(".list-body");

          listEl.innerHTML = "";

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
                url: "/capturedlib/" + id + "/used_samplelibs",
                type: "GET",
                success: function (data) {

                  fillElements(id,data);

                  updateTotalAmount();
                  updateTotalVolume();

                  initEvents();

                  modal.show();

                },
                error: function (xhr, ajaxOptions, thrownError) {

                }
            });

          });

        }

      }

      function fillElements(id,data) {

        var listEl = document.querySelector(".list-body");

        listEl.setAttribute('data-captured_lib_id', id);

        var total_amount = 0;
        var total_volume = 0;

        for (var i = 0; i < data.length; i++) {

          var row = `<div class="row mb-1">
              <div class="col-3 align-self-center" data-id="${ data[i].id }"><a href="/samplelib/edit/${ data[i].id }">${ data[i].name }</a></div>
              <div class="col-1 align-self-center text-center">${ data[i].conc }</div>
              <div class="col-2 align-self-center text-center">${ data[i].vol_remain }</div>
              <div class="col-2 align-self-center text-center">${ data[i].barcode }</div>
              <div class="col-2 text-center"><input type="number" class="textinput textInput form-control form-control-sm text-end detail-amount" value="${ data[i].amount }"></div>
              <div class="col-2 text-center"><input type="number" class="textinput textInput form-control form-control-sm text-end detail-volume" value="${ data[i].volume }"></div>
            </div>`;
          listEl.innerHTML += row;

        }

        var footer = `<div class="mt-5">
              <button type="button" class="btn btn-lg btn-success" id="btn_save">Save</button>
            </div>`;

        listEl.innerHTML += footer;

      }

      function getValues() {

        var rows = document.querySelector(".list-body").querySelectorAll(".row");

        var values = [];

        for (var row of rows) {

          var id = row.querySelectorAll('div')[0].getAttribute("data-id");
          var volume = row.querySelector(".detail-volume").value;
          var amount = row.querySelector(".detail-amount").value;

          values.push({
            "id":id,
            "volume":volume,
            "amount":amount
          });
        }

        return JSON.stringify(values);

      }

      function updateTotalAmount() {
        var total = 0;

        for (var detail of document.querySelectorAll(".detail-amount")) {

          total += parseFloat(detail.value);

        }

        document.querySelector("#total_amount").value = total;

      }

      function updateTotalVolume() {
        var total = 0;

        for (var detail of document.querySelectorAll(".detail-volume")) {

          total += parseFloat(detail.value);

        }

        document.querySelector("#total_volume").value = total;

      }

      function initEvents() {

        for (var amount of document.querySelectorAll(".detail-amount")) {

          amount.addEventListener("change", function () {

            var parent = this.closest('.row');

            var conc = parent.querySelectorAll('div')[1].innerText;

            var volume = (this.value / conc).toFixed(2);

            parent.querySelector(".detail-volume").value = volume;
            updateTotalAmount();
            updateTotalVolume();

          });

        }

        var id = document.querySelector(".list-body").getAttribute("data-captured_lib_id");

        document.getElementById("btn_save").addEventListener('click', function () {

          $.ajax({
            type: "GET",
            url: "/capturedlib/"+ id +"/update_async",
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

                modal.hide();
              });
            }
            else {
              Swal.fire({
                  text: result.message,
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

    }

    var handleSelectedRows = ((e) => {

      var isInit = false;

      var container = document.querySelector('.table');

      var stepper = new KTStepper(document.getElementById("modal_stepper"));

      var modal = new bootstrap.Modal(document.getElementById("modal_sequencinglib_options"));

      function initModal() {

        function resetStepper() {

          stepper.goFirst();

        }

        function resetForm() {

          document.getElementById("frm_creation_options").reset();

        }

        function checkIdenticalBarcode() {

          var result = {};

          $.ajax({
            type: "GET",
            url: "/capturedlib/check_idendical_barcode",
            data: {
              "selected_ids": JSON.stringify(selectedRows)
            },
            async: false,
            error: function (xhr, ajaxOptions, thrownError) {
                swal("Error checking barcode!", "Please try again", "error");
            }
          }).done(function(data) {

            result = data;

          });

          return result;

        }

        document.getElementById("modal_sequencinglib_options").addEventListener('show.bs.modal', function(e){

          var result = checkIdenticalBarcode();

          if (!result.success) {

            Swal.fire({
                text: "Identical barcodes are used in selected rows. Clashing CLs are " + result.clasheds.toString(),
                icon: "error",
                buttonsStyling: false,
                confirmButtonText: "Ok, got it!",
                customClass: {
                    confirmButton: "btn fw-bold btn-primary",
                }
            }).then(function () {

              modal.hide();

            });

          }
          else {

            initStepper();

            if (!isInit) {

              isInit = true;

              initEvents();
            }

          }

        });

        document.getElementById("modal_sequencinglib_options").addEventListener('hide.bs.modal', function(e){

          resetForm();

          resetStepper();

        });

      }

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
          initModal(), handleBatchDelete(), uncheckedFirstCheckBox();
        }
      }

    })();

    var handleFilter = () => {

      $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
        var min = parseInt($('#min').val(), 10);
        var max = parseInt($('#max').val(), 10);
        var age = parseFloat(data[3]) || 0; // use data for the age column

        if (
            (isNaN(min) && isNaN(max)) ||
            (isNaN(min) && age <= max) ||
            (min <= age && isNaN(max)) ||
            (min <= age && age <= max)
        ) {
            return true;
        }
        return false;
      });

      $('#min, #max').keyup(function () {
          table.draw();
      });

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
            handleFilter();
        }
    }
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesServerSide.init();
});
