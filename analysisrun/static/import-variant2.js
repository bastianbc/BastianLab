const arName = window.location.pathname.split('/').filter(Boolean).pop();
const btnImport = document.getElementById("import-btn");
const error = document.getElementById("error");
const progress = document.getElementById("progress-bar");
const status = document.getElementById("status");

let pollingInterval = null;
let importStarted = false;  // ✅ ADD THIS FLAG

// Initialize event listeners
document.addEventListener("DOMContentLoaded", function() {
    btnImport.addEventListener("click", startImport);
});

function updateProgress(data) {
    progress.style.width = `${data.progress}%`;
    progress.innerText = `${data.progress}%`;
    status.innerText = data.status;
    error.innerText = data.error || "";

    if (data.status === "processing") {
        // Start polling if not already polling
        if (!pollingInterval) {
            console.log("Starting polling...");
            pollingInterval = setInterval(checkProgress, 3000); // Poll every 3 seconds
        }
    } else if (data.status === "done") {
        // Stop polling
        console.log("Import completed, stopping polling");
        stopPolling();
        btnImport.disabled = false;
        btnImport.innerText = "Import Variants";
        importStarted = false;  // ✅ RESET FLAG
        status.innerHTML = `Import completed successfully with ${data.processed_files} of ${data.total_files} files processed! <a href="#" onclick="viewReport()">View Report</a>`;
    } else if (data.status === "error") {
        // Stop polling on error
        console.log("Import error, stopping polling");
        stopPolling();
        btnImport.disabled = false;
        btnImport.innerText = "Import Variants";
        importStarted = false;  // ✅ RESET FLAG
    }
}

function checkProgress() {
    // Just check progress, don't start new import
    console.log("Checking progress...");
    fetch(`/analysisrun/check_import_progress/${arName}/`)
      .then(res => res.json())
      .then(data => {
        console.log("Progress check:", data);
        updateProgress(data);
      })
      .catch(err => {
        console.error("Error checking progress:", err);
        error.innerText = err.message;
        stopPolling();
        btnImport.disabled = false;
        btnImport.innerText = "Import Variants";
        importStarted = false;  // ✅ RESET FLAG
      });
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
        console.log("Polling stopped");
    }
}

function startImport() {
    // ✅ PREVENT DOUBLE CLICKS
    if (importStarted) {
        console.log("Import already started, ignoring duplicate click");
        return;
    }

    console.log("Starting import...");
    importStarted = true;  // ✅ SET FLAG
    btnImport.disabled = true;
    error.innerText = "";
    progress.style.width = "0%";
    progress.innerText = "0%";
    status.innerText = "Starting import...";
    btnImport.innerText = "Importing...";

    fetch(`/analysisrun/start_import_variants/${arName}/`)
      .then(res => res.json())
      .then(data => {
        console.log("Import started:", data);
        updateProgress(data);
      })
      .catch(err => {
        console.error("Error starting import:", err);
        error.innerText = err.message;
        btnImport.disabled = false;
        btnImport.innerText = "Import Variants";
        importStarted = false;  // ✅ RESET FLAG ON ERROR
      });
}

function viewReport() {
  const modal = new bootstrap.Modal(document.getElementById('report-modal'));
  modal.show();

  fetch(`/analysisrun/report_import_status/${arName}/`)
    .then(res => res.json())
    .then(data => {
      console.log(data);
      const reportTable = document.querySelector('#report-modal .modal-body table tbody');
      reportTable.innerHTML = data.map(file => `
        <tr>
          <td>${file.file_name}</td>
          <td>${file.status}</td>
          <td>
            ${file.log_url 
              ? `<a href="${file.log_url.replace('s3://', 'https://s3.console.aws.amazon.com/s3/object/')}" 
                   target="_blank" 
                   rel="noopener noreferrer">View Log</a>` 
              : '<span class="text-muted">N/A</span>'}
          </td>
        </tr>
      `).join('');
    })
    .catch(err => {
      console.error("Error loading report:", err);
    });
}



// const arName = window.location.pathname.split('/').filter(Boolean).pop();
// const btnImport = document.getElementById("import-btn");
// const error = document.getElementById("error");
// const progress = document.getElementById("progress-bar");
// const status = document.getElementById("status");
//
// // Initialize event listeners
// document.addEventListener("DOMContentLoaded", function() {
//     btnImport.addEventListener("click", startImport);
// });
//
// function updateProgress(data) {
//     progress.style.width = `${data.progress}%`;
//     progress.innerText = `${data.progress}%`;
//     status.innerText = data.status;
//     error.innerText = data.error || "";
//
//     if (data.status === "processing") {
//       // Check status every 5 seconds
//       setTimeout(startImport, 1000);
//     } else if (data.status === "done") {
//       // Import completed successfully
//       btnImport.disabled = false;
//       btnImport.innerText = "Import Variants";
//       status.innerHTML = `Import completed successfully with ${data.processed_files} of ${data.total_files} files processed! <a href="#" onclick="viewReport()">View Report</a>`;
//     }
// }
//
// function startImport() {
//     btnImport.disabled = true;
//     error.innerText = "";
//     progress.style.width = "0%";
//     progress.innerText = "0%";
//     status.innerText = "Importing...";
//     btnImport.innerText = "Importing...";
//
//     fetch(`/analysisrun/start_import_variants/${arName}/`)
//       .then(res => res.json())
//       .then(data => {
//         console.log(data);
//         status.innerText = data.status;
//         error.innerText = data.error || "";
//         updateProgress(data);
//       })
//       .catch(err => {
//         error.innerText = err.message;
//         btnImport.disabled = false;
//         btnImport.innerText = "Import Variants";
//       });
// }
//
// function viewReport() {
//     const modal = new bootstrap.Modal(document.getElementById('report-modal'));
//     modal.show();
//     fetch(`/analysisrun/report_import_status/${arName}/`)
//       .then(res => res.json())
//       .then(data => {
//         console.log(data);
//         const reportTable = document.querySelector('#report-modal .modal-body table tbody');
//         reportTable.innerHTML = data.map(file => `<tr><td>${file.file_name}</td><td>${file.status}</td></tr>`).join('');
//       });
// }