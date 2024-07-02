var bodies = [];
var selectedId = null;
var bodyContainer = null;

$(document).ready(function() {
    selectedId = document.getElementById("id_body_site").value;
    bodyContainer = document.querySelector('.body-site-row');

    getBodySites();

    // Load the selected body if available
    if (selectedId) {
        loadSelectedBody( selectedId );
    }
    else {
        // Initial dropdown
        const initialDropdown = createDropdown(null);
        if (initialDropdown) {
            bodyContainer.appendChild(initialDropdown);
        }
    }
});


function createDropdown(parentId, selectedValue = null) {
    var col = document.createElement("div");
    col.classList.add("col-2");

    const dropdown = document.createElement('select');
    dropdown.classList.add("select","form-control","form-control-solid");

    const defaultOption = document.createElement('option');
    defaultOption.text = 'Select...';
    defaultOption.value = '';
    dropdown.appendChild(defaultOption);

    var hasOptions = false;

    bodies.forEach(body => {
        if (body.parent == parentId) {
            const option = document.createElement('option');
            option.text = body.name;
            option.value = body.id;
            if (body.id == selectedValue) {
                option.selected = true;
            }
            dropdown.appendChild(option);
            hasOptions = true;
        }
    });

    dropdown.addEventListener('change', handleDropdownChange);

    col.appendChild(dropdown)

    // Only return the dropdown if it has options
    return hasOptions ? col : null;
}

function handleDropdownChange(event) {
    selectedId = this.value;

    // Remove all dropdowns below the current level
    let nextDropdown = this.parentElement.nextElementSibling;
    while (nextDropdown) {
        if (nextDropdown.tagName.toLowerCase() === 'div') {
            const dropdownToRemove = nextDropdown;
            nextDropdown = nextDropdown.nextElementSibling;
            dropdownToRemove.remove();
        }
        else {
            nextDropdown = nextDropdown.nextElementSibling;
        }
    }

    if (selectedId) {
        const newDropdown = createDropdown(selectedId);
        if (newDropdown) {
            bodyContainer.appendChild(newDropdown);
        }

        setBodySite();
    }
}

function loadSelectedBody(selectedBodyId) {
    let currentBody = bodies.find(body => body.id == selectedBodyId);

    while (currentBody) {
        const parentId = currentBody.parent;
        const dropdown = createDropdown(parentId, currentBody.id);

        if (dropdown) {
            bodyContainer.insertBefore(dropdown, bodyContainer.firstChild);
        }

        currentBody = bodies.find(body => body.id == parentId);
    }
}

function getBodySites() {
    $.ajax({
        url: "/body/get_bodies",
        type: "GET",
        async: false,
        success: function (data) {
          bodies = data;
        }
    });
}

// Set django form field
function setBodySite() {
    document.getElementById("id_body_site").value = selectedId;
}
