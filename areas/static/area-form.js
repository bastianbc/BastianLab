document.addEventListener("DOMContentLoaded", function () {

    const blockElement = document.getElementById("id_block");

    if ( blockElement.value ) {
        getBlockInfo( blockElement.value );
    }

    blockElement.addEventListener("change", function () {

        getBlockInfo( this.value );

    });
});

function getBlockInfo( value ) {
    // Calling delete request with ajax
    $.ajax({
        type: "GET",
        url: "/blocks/get_block_async",
        data: {
          "id": value,
        },
        error: function (xhr, ajaxOptions, thrownError) {
            swal("Error deleting!", "Please try again", "error");
        }
    }).done(function (result) {
        console.log(result);
        visibleBlockInfo();

        document.querySelector('input[name="patient"]').value = result.patient;
        document.querySelector('input[name="project"]').value = result.project;
        document.querySelector('a[name="image"]').setAttribute("href",result.scan_number);
    });
}

function visibleBlockInfo() {
    const blockInfo = document.querySelector(".block-info");
    if (blockInfo.classList.contains("d-none")) {
        blockInfo.classList.remove("d-none");
    }

    blockInfo.classList.add("d-flex")
}
