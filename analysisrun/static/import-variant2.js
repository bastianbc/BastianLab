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
    console.log("⏳ Starting progress polling...");

    let currentProgress = 0;
    let firstUpdateReceived = false; // Flag for first real progress update
    let warmupActive = true;         // Whether the initial slow ramp-up is active
    const warmupTarget = 5;          // Slowly move 0 → 5%
    const warmupDuration = 3000;     // 3 seconds total warmup time

    // --- Warm-up animation: reassuring initial movement ---
    const warmupStart = performance.now();
    function warmupStep(timestamp) {
        const elapsed = timestamp - warmupStart;
        const progressElement = document.querySelector('#progress-bar');
        if (!progressElement) return;

        if (elapsed < warmupDuration && !firstUpdateReceived) {
            const progress = (elapsed / warmupDuration) * warmupTarget;
            progressElement.style.width = `${progress}%`;
            progressElement.innerText = `${Math.round(progress)}%`;
            requestAnimationFrame(warmupStep);
        } else if (!firstUpdateReceived) {
            progressElement.style.width = `${warmupTarget}%`;
            progressElement.innerText = `${warmupTarget}%`;
        }
    }
    requestAnimationFrame(warmupStep);

    // --- Regular polling ---
    const interval = setInterval(() => {
        fetch(`/analysisrun/check_import_progress/${arName}/`)
            .then(res => res.json())
            .then(data => {
                console.log("📊 Progress check:", data);
                const progressElement = document.querySelector('#progress-bar');
                if (!progressElement) return;

                const targetProgress = data.progress || 0;
                const processed = data.processed_files || 0;
                const total = data.total_files || 0;
                const currentStatus = data.status || "processing";
                const logUrl = data.log_url || null;

                // --- Detect first real update ---
                if (targetProgress > 0 && !firstUpdateReceived) {
                    firstUpdateReceived = true;
                    warmupActive = false;
                    console.log("🎯 First progress update received — switching from warmup.");
                }

                // --- Smooth animation toward target ---
                const smoothProgress = () => {
                    if (currentProgress < targetProgress) {
                        currentProgress += Math.min(1, targetProgress - currentProgress);
                        progressElement.style.width = `${currentProgress}%`;
                        progressElement.innerText = `${Math.round(currentProgress)}%`;
                        requestAnimationFrame(smoothProgress);
                    } else {
                        currentProgress = targetProgress;
                        progressElement.style.width = `${currentProgress}%`;
                        progressElement.innerText = `${Math.round(currentProgress)}%`;
                    }
                };
                smoothProgress();

                // --- Color transitions ---
                progressElement.classList.remove("bg-success", "bg-danger", "bg-primary");
                if (currentStatus === "done") progressElement.classList.add("bg-success");
                else if (currentStatus === "error") progressElement.classList.add("bg-danger");
                else progressElement.classList.add("bg-primary");

                // --- Update status text ---
                const status = document.querySelector('#status');
                if (status) {
                    if (currentStatus === "processing") {
                        status.innerText = `${currentStatus} (${processed}/${total} files)`;
                    } else if (currentStatus === "done") {
                        status.innerHTML = `✅ Completed ${processed} of ${total} files`;
                        clearInterval(interval);
                    } else if (currentStatus === "error") {
                        status.innerHTML = `❌ Error after ${processed} of ${total} files`;
                        clearInterval(interval);
                    }
                }
            })
            .catch(err => {
                console.error("❌ Polling error:", err);
                clearInterval(interval);
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
