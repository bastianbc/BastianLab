// import-variant.js

// Extract the Analysis Run name from the URL
const arName = window.location.pathname.split('/').filter(Boolean).pop();

// Cache element references
const btnImport = document.getElementById("import-btn");
const error = document.getElementById("error");
const progress = document.getElementById("progress-bar");
const status = document.getElementById("status");

// Make the function global so inline onclick (if ever used) can access it
window.startImport = startImport;

// Initialize event listeners when DOM is ready
document.addEventListener("DOMContentLoaded", function() {
  btnImport.addEventListener("click", startImport);
});

function updateProgress(data) {
  progress.style.width = `${data.progress}%`;
  progress.innerText = `${data.progress}%`;
  status.innerText = data.status;
  error.innerText = data.error || "";

  if (data.status === "processing") {
    // Check status again after 1 second
    setTimeout(startImport, 1000);
  } else if (data.status === "done") {
    btnImport.disabled = false;
    btnImport.innerText = "Import Variants";
    status.innerHTML = `
      Import completed successfully with ${data.processed_files} of ${data.total_files} files processed!
      <a href="#" onclick="viewReport()">View Report</a>
    `;
  }
}

function startImport() {
  btnImport.disabled = true;
  error.innerText = "";
  progress.style.width = "0%";
  progress.innerText = "0%";
  status.innerText = "Importing...";
  btnImport.innerText = "Importing...";

  fetch(`/analysisrun/start_import_variants/${arName}/`)
    .then(res => res.json())
    .then(data => {
      console.log(data);
      status.innerText = data.status;
      error.innerText = data.error || "";
      updateProgress(data);
    })
    .catch(err => {
      error.innerText = err.message;
      btnImport.disabled = false;
      btnImport.innerText = "Import Variants";
    });
}

function viewReport() {
  const modal = new bootstrap.Modal(document.getElementById("report-modal"));
  modal.show();

  fetch(`/analysisrun/report_import_status/${arName}/`)
    .then(res => res.json())
    .then(data => {
      console.log(data);
      const reportTable = document.querySelector('#report-modal .modal-body table tbody');
      reportTable.innerHTML = data
        .map(file => `<tr><td>${file.file_name}</td><td>${file.status}</td></tr>`)
        .join('');
    });
}
