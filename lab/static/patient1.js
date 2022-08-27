$(document).ready(function () {

    $('.table').DataTable({
        // processing: true,
        paging: true,
        ordering: true,
        searching: true,
        serverSide: true,
        info: true,
        columns: [
          { data: "pat_id" },
          { data: "source" },
          { data: "sex" },
          { data: "race" },
          { data: "project" },
          // { data: "blocks" },
        ],
        ajax: {
          url: '/lab/deneme',
          type: "GET",
          dataSrc: function (returnValue) {
            console.log("aaaaaaaaaaaaaaaaaa");
            console.log(returnValue);
            return JSON.parse(returnValue.data);
          }
        },
    });

});
