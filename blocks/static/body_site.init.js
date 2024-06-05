$(document).ready(function() {
    var bodies = [];
    var selectedId = document.getElementById("id_body_site").value;

    const bodyContainer = document.querySelector('.body-site-row');

    function createDropdown(level, parentId, selectedValue = null) {
        var col = document.createElement("div");
        col.classList.add("col-2");

        const dropdown = document.createElement('select');
        dropdown.classList.add('level');
        dropdown.setAttribute('data-level', level);
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
        const currentLevel = parseInt(this.getAttribute('data-level'), 10);

        // Remove all dropdowns below the current level
        const dropdowns = document.querySelectorAll(`.level[data-level]`);
        dropdowns.forEach(dropdown => {
            if (parseInt(dropdown.getAttribute('data-level'), 10) > currentLevel) {
                dropdown.remove();
            }
        });

        if (selectedId) {
            const newDropdown = createDropdown(currentLevel + 1, selectedId);
            if (newDropdown) {
                bodyContainer.appendChild(newDropdown);
            }

            setBodySite();
        }
    }

    function loadSelectedBody(selectedBodyId) {
        let currentBody = bodies.find(body => body.id == selectedBodyId);
        let level = 0;

        while (currentBody) {
            const parentId = currentBody.parent;
            const dropdown = createDropdown(level, parentId, currentBody.id);
            if (dropdown) {
                bodyContainer.appendChild(dropdown);
            }
            level++;
            currentBody = bodies.find(body => body.id == parentId);
        }
    }

    function getBodySites(parent_id) {
        $.ajax({
            url: "/body/get_bodies/" + parent_id,
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

    getBodySites("");

    // Initial dropdown
    const initialDropdown = createDropdown(0, null);
    if (initialDropdown) {
        bodyContainer.appendChild(initialDropdown);
    }

    // Load the selected body if available
    if (selectedId) {
        loadSelectedBody( selectedId );
    }
});
