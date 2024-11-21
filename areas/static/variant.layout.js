// Button click event handler
document.addEventListener('DOMContentLoaded', function() {
    const openModalBtn = document.querySelector('#openModalBtn');
    openModalBtn.addEventListener('click', fetchAndShowModal);
});

function fetchAndShowModal() {
    fetch('/api/getData')
        .then(response => response.json())
        .then(data => {
            initializeModal(data);
            $('#variant_layout').modal('show');
        });
}

function initializeModal(data) {
    // Clear previous data
    clearModalData();

    // Initialize tabs
    const tabContainer = document.querySelector('.nav-tabs');
    const tabContent = document.querySelector('.tab-content');

    data.analyses.forEach((analysis, index) => {
        // Create tab
        const isActive = index === 0;
        const tabId = `analysis_${index}`;

        createTab(tabContainer, tabId, `Analysis Run ${index + 1}`, isActive);
        createTabPane(tabContent, tabId, analysis.variants, isActive);

        // Initialize DataTable
        $(`#variant_datatable_${index}`).DataTable({
            data: analysis.variants,
            columns: [
                { data: 'sampleLibrary' },
                { data: 'gene' },
                { data: 'pVariant' },
                { data: 'coverage' },
                { data: 'vaf' },
                {
                    data: null,
                    render: function(data, type, row) {
                        return '<button class="btn btn-sm btn-light">View</button>';
                    }
                }
            ]
        });
    });
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
}

function clearModalData() {
    // Destroy existing DataTables
    $('.table').each(function() {
        if ($.fn.DataTable.isDataTable(this)) {
            $(this).DataTable().destroy();
        }
    });

    // Clear tabs and content
    document.querySelector('.nav-tabs').innerHTML = '';
    document.querySelector('.tab-content').innerHTML = '';
}

// Modal close event
$('#variant_layout').on('hidden.bs.modal', clearModalData);
