const arName = window.location.pathname.split('/').filter(Boolean).pop();
const btnImport = document.getElementById("import-btn");
const error = document.getElementById("error");
const progress = document.getElementById("progress-bar");
const status = document.getElementById("status");

let importStarted = false;

// Initialize event listeners
document.addEventListener("DOMContentLoaded", function() {
    btnImport.addEventListener("click", startImport);
});

function startProgressPolling() {
    console.log("⏳ Starting 2-second polling to /check_import_progress/");

    let currentProgress = 0; // Track current displayed progress

    const interval = setInterval(() => {
        fetch(`/analysisrun/check_import_progress/${arName}/`)
            .then(res => res.json())
            .then(data => {
                console.log("📊 Progress check:", data);

                const targetProgress = data.progress || 0;
                const processed = data.processed_files || 0;
                const total = data.total_files || 0;
                const currentStatus = data.status || "processing";
                const logUrl = data.log_url || null;

                // ✅ Update Log File button (if exists)
                const logBtn = document.querySelector('#report-modal .card-toolbar a');
                if (logBtn && logUrl) {
                    const awsUrl = logUrl.replace('s3://', 'https://s3.console.aws.amazon.com/s3/object/');
                    logBtn.href = awsUrl;
                    logBtn.target = "_blank";
                    logBtn.textContent = "Open Log File";
                    logBtn.classList.remove("btn-light");
                    logBtn.classList.add("btn-primary");
                }

                // ✅ Smooth progress bar animation
                const smoothProgress = () => {
                    if (currentProgress < targetProgress) {
                        currentProgress += Math.min(1, targetProgress - currentProgress);
                        progress.style.width = `${currentProgress}%`;
                        progress.innerText = `${Math.round(currentProgress)}%`;
                        requestAnimationFrame(smoothProgress);
                    } else {
                        currentProgress = targetProgress;
                        progress.style.width = `${currentProgress}%`;
                        progress.innerText = `${Math.round(currentProgress)}%`;
                    }
                };
                smoothProgress();

                // ✅ Color transitions
                progress.classList.remove("bg-success", "bg-danger", "bg-primary");
                if (currentStatus === "done") progress.classList.add("bg-success");
                else if (currentStatus === "error") progress.classList.add("bg-danger");
                else progress.classList.add("bg-primary");

                // ✅ Update status while processing
                if (currentStatus === "processing") {
                    status.innerText = `${currentStatus} (${processed}/${total} files)`;
                }

                // ✅ Completion
                if (currentStatus === "done") {
                    clearInterval(interval);
                    btnImport.disabled = false;
                    btnImport.innerText = "Import Complete";
                    progress.classList.remove("progress-bar-striped", "progress-bar-animated");
                    importStarted = false;

                    status.innerHTML = `
                        ✅ Import completed successfully with ${processed} of ${total} files processed!
                        <a href="#" onclick="viewReport()" class="fw-bold text-primary ms-2">View Report</a>
                    `;

                    Swal.fire({
                        icon: 'success',
                        title: 'Import Complete!',
                        text: `Successfully processed ${processed} of ${total} files.`,
                        confirmButtonText: 'OK'
                    });
                }

                // ✅ Error state
                if (currentStatus === "error") {
                    clearInterval(interval);
                    btnImport.disabled = false;
                    btnImport.innerText = "Retry Import";
                    progress.classList.remove("progress-bar-striped", "progress-bar-animated");
                    progress.classList.add("bg-danger");
                    error.innerText = data.error || "Unknown error occurred";
                    importStarted = false;

                    status.innerHTML = `
                        ❌ Import failed after ${processed} of ${total} files.
                        <span class="text-danger fw-bold">Check logs or retry.</span>
                    `;

                    Swal.fire({
                        icon: 'error',
                        title: 'Import Failed',
                        text: data.error || 'An error occurred during import'
                    });
                }
            })
            .catch(err => {
                console.error("❌ Polling error:", err);
                clearInterval(interval);
                btnImport.disabled = false;
                btnImport.innerText = "Import Variants";
                progress.classList.add("bg-danger");
                status.innerText = "❌ Connection lost while polling progress.";
                error.innerText = err.message;
                importStarted = false;
            });
    }, 10000);
}

function startImport() {
    if (importStarted) {
        console.log("⚠️ Import already started — ignoring duplicate click");
        return;
    }

    console.log("🚀 Starting import...");
    importStarted = true;
    btnImport.disabled = true;
    error.innerText = "";
    progress.style.width = "0%";
    progress.innerText = "0%";
    status.innerText = "Starting import...";
    btnImport.innerText = "Importing...";

    // Start polling immediately (before backend finishes)
    console.log("⏱ Launching progress polling before fetch finishes...");
    startProgressPolling();

    // Fire backend import
    fetch(`/analysisrun/start_import_variants/${arName}/`)
        .then(res => res.json())
        .then(data => {
            console.log("✅ Import request acknowledged:", data);
            status.innerText = "Import in progress...";
        })
        .catch(err => {
            console.error("❌ Error starting import:", err);
            error.innerText = err.message;
            btnImport.disabled = false;
            btnImport.innerText = "Import Variants";
            importStarted = false;
        });
}

function viewReport() {
    const modal = new bootstrap.Modal(document.getElementById('report-modal'));
    modal.show();

    fetch(`/analysisrun/report_import_status/${arName}/`)
        .then(res => res.json())
        .then(data => {
            const reportTable = document.querySelector('#report-modal .modal-body table tbody');
            reportTable.innerHTML = data.map((file, index) => `
                <tr>
                  <td class="text-gray-800 fw-bold fs-6">${index + 1}</td>
                  <td colspan="2"><span class="text-gray-800 fw-bold text-hover-primary mb-1 fs-6">${file.file_name}</span></td>
                  <td colspan="2" class="text-end pe-0"><span class="text-gray-800 fw-bold fs-6">${file.status}</span></td>
                  <td colspan="2" class="text-end">
                    ${file.log_url 
                        ? `<a href="${file.log_url.replace('s3://', 'https://s3.console.aws.amazon.com/s3/object/')}" 
                               target="_blank" rel="noopener noreferrer"
                               class="text-primary fw-bold fs-6">View Log</a>`
                        : '<span class="text-muted fw-bold fs-6">N/A</span>'}
                  </td>
                </tr>
            `).join('');
        })
        .catch(err => {
            console.error("Error loading report:", err);
        });
}
