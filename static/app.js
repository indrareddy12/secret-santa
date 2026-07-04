document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('santaForm');
    const employeesFile = document.getElementById('employeesFile');
    const previousFile = document.getElementById('previousFile');
    const seedInput = document.getElementById('seedInput');
    const submitBtn = document.getElementById('submitBtn');

    const employeesDropZone = document.getElementById('employeesDropZone');
    const previousDropZone = document.getElementById('previousDropZone');
    const employeesFileInfo = document.getElementById('employeesFileInfo');
    const previousFileInfo = document.getElementById('previousFileInfo');

    const resultsEmpty = document.getElementById('resultsEmpty');
    const resultsLoading = document.getElementById('resultsLoading');
    const errorBox = document.getElementById('errorBox');
    const errorMessage = document.getElementById('errorMessage');
    const resultsContent = document.getElementById('resultsContent');
    const assignmentsBody = document.getElementById('assignmentsBody');
    const searchBar = document.getElementById('searchBar');
    const downloadCsvBtn = document.getElementById('downloadCsvBtn');

    const runTestsBtn = document.getElementById('runTestsBtn');
    const testConsole = document.getElementById('testConsole');

    let currentAssignments = [];
    let currentCsv = '';

    // File Drag & Drop UX Helpers
    function setupDragAndDrop(dropZone, fileInput, fileInfoEl, iconClass) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('dragover');
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length) {
                fileInput.files = files;
                updateFileInfo(files[0], fileInfoEl);
            }
        }, false);

        fileInput.addEventListener('change', (e) => {
            if (fileInput.files.length) {
                updateFileInfo(fileInput.files[0], fileInfoEl);
            } else {
                fileInfoEl.innerHTML = '';
            }
        });
    }

    function updateFileInfo(file, element) {
        element.innerHTML = `<i class="fa-solid fa-circle-check"></i> Selected: <strong>${file.name}</strong> (${(file.size / 1024).toFixed(2)} KB)`;
    }

    setupDragAndDrop(employeesDropZone, employeesFile, employeesFileInfo, 'fa-file-csv');
    setupDragAndDrop(previousDropZone, previousFile, previousFileInfo, 'fa-clock-rotate-left');

    // Handle Form Submit (Assignment Generation)
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI states
        resultsEmpty.classList.add('hidden');
        errorBox.classList.add('hidden');
        resultsContent.classList.add('hidden');
        resultsLoading.classList.remove('hidden');
        submitBtn.disabled = true;

        const formData = new FormData();
        formData.append('employees_file', employeesFile.files[0]);
        if (previousFile.files.length) {
            formData.append('previous_file', previousFile.files[0]);
        }
        formData.append('seed', seedInput.value);

        try {
            const response = await fetch('/api/assign', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'An error occurred during assignment');
            }

            // Save state
            currentAssignments = data.assignments;
            currentCsv = data.csv;

            // Render table
            renderAssignments(currentAssignments);

            // Show results
            resultsLoading.classList.add('hidden');
            resultsContent.classList.remove('hidden');

        } catch (err) {
            errorMessage.textContent = err.message;
            resultsLoading.classList.add('hidden');
            errorBox.classList.remove('hidden');
        } finally {
            submitBtn.disabled = false;
        }
    });

    // Render Table Rows
    function renderAssignments(list) {
        assignmentsBody.innerHTML = '';

        if (list.length === 0) {
            assignmentsBody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">No matching assignments found.</td></tr>`;
            return;
        }

        list.forEach(a => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>
                    <div class="employee-cell">
                        <span class="emp-name">${escapeHtml(a.giver_name)}</span>
                        <span class="emp-email">${escapeHtml(a.giver_email)}</span>
                    </div>
                </td>
                <td class="arrow-col">
                    <i class="fa-solid fa-arrow-right arrow-icon"></i>
                </td>
                <td>
                    <div class="employee-cell">
                        <span class="emp-name">${escapeHtml(a.child_name)}</span>
                        <span class="emp-email">${escapeHtml(a.child_email)}</span>
                    </div>
                </td>
            `;
            assignmentsBody.appendChild(tr);
        });
    }

    // Escape HTML Helper
    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Search / Filter
    searchBar.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
            renderAssignments(currentAssignments);
            return;
        }

        const filtered = currentAssignments.filter(a => 
            a.giver_name.toLowerCase().includes(query) ||
            a.giver_email.toLowerCase().includes(query) ||
            a.child_name.toLowerCase().includes(query) ||
            a.child_email.toLowerCase().includes(query)
        );
        renderAssignments(filtered);
    });

    // String trim/strip helper for older browsers just in case
    if (!String.prototype.strip) {
        String.prototype.strip = function() {
            return this.trim();
        };
    }

    // Download CSV
    downloadCsvBtn.addEventListener('click', () => {
        if (!currentCsv) return;
        const blob = new Blob([currentCsv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', 'secret_santa_assignments.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    // Run pytest unit tests via backend
    runTestsBtn.addEventListener('click', async () => {
        runTestsBtn.disabled = true;
        runTestsBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Running Tests...`;
        testConsole.textContent = "Running test suite on system...\n\n";
        testConsole.style.color = "#d4af37"; // gold during execution

        try {
            const response = await fetch('/api/run-tests', {
                method: 'POST'
            });
            const data = await response.json();

            if (response.ok) {
                testConsole.textContent = data.stdout || data.stderr || "No output returned.";
                if (data.exit_code === 0) {
                    testConsole.style.color = "#4af626"; // bright green
                    runTestsBtn.innerHTML = `<i class="fa-solid fa-circle-check"></i> Passed`;
                } else {
                    testConsole.style.color = "#ef4444"; // red
                    runTestsBtn.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Failed`;
                }
            } else {
                testConsole.style.color = "#ef4444";
                testConsole.textContent = `Error details: ${data.detail || 'Internal server error running tests'}`;
                runTestsBtn.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Error`;
            }
        } catch (err) {
            testConsole.style.color = "#ef4444";
            testConsole.textContent = `Error connecting to test server: ${err.message}`;
            runTestsBtn.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Error`;
        } finally {
            setTimeout(() => {
                runTestsBtn.disabled = false;
                runTestsBtn.innerHTML = `<i class="fa-solid fa-play"></i> Run Tests`;
            }, 3000);
            // Scroll to bottom
            testConsole.scrollTop = testConsole.scrollHeight;
        }
    });
});
