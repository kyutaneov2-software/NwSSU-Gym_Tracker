document.addEventListener("DOMContentLoaded", () => {

    /* ============================================================
        REGISTERED MEMBERS — FILTERS + PAGINATION
    ============================================================ */

    const filterID = document.getElementById("filterID");
    const filterType = document.getElementById("filterType");
    const filterPlan = document.getElementById("filterPlan");
    const filterStatus = document.getElementById("filterStatus");
    const tableRows = document.querySelectorAll(".registered-member-table tbody tr");

    const rowsPerPage = 10;
    let currentPage = 1;
    let filteredRows = Array.from(tableRows);

    function applyMemberFilters() {
        const idValue = filterID.value.toLowerCase();
        const typeValue = filterType.value;
        const planValue = filterPlan.value;
        const statusValue = filterStatus.value;

        filteredRows = Array.from(tableRows).filter(row => {
            const id = row.cells[0].textContent.toLowerCase();
            const type = row.cells[2].textContent;
            const plan = row.cells[3].textContent;
            const status = row.cells[4].textContent;

            return (
                id.includes(idValue) &&
                (!typeValue || type === typeValue) &&
                (!planValue || plan === planValue) &&
                (!statusValue || status === statusValue)
            );
        });

        currentPage = 1;
        updateMemberPagination();
    }

    function updateMemberPagination() {
        const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
        const tableBody = document.getElementById("memberTableBody");

        tableBody.classList.add("fade-out");

        setTimeout(() => {
            tableRows.forEach(row => (row.style.display = "none"));

            const start = (currentPage - 1) * rowsPerPage;
            const end = start + rowsPerPage;
            filteredRows.slice(start, end).forEach(row => (row.style.display = ""));

            renderMemberPageNumbers(totalPages);

            tableBody.classList.remove("fade-out");
            tableBody.classList.add("fade-in");

            setTimeout(() => tableBody.classList.remove("fade-in"), 300);
        }, 200);
    }

    function renderMemberPageNumbers(totalPages) {
        const pageNumbersDiv = document.getElementById("pageNumbers");
        pageNumbersDiv.innerHTML = "";

        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement("button");
            btn.textContent = i;
            btn.classList.add("page-number");
            if (i === currentPage) btn.classList.add("active");

            btn.addEventListener("click", () => {
                currentPage = i;
                updateMemberPagination();
            });

            pageNumbersDiv.appendChild(btn);
        }

        document.getElementById("prevPage").disabled = currentPage === 1;
        document.getElementById("nextPage").disabled =
            currentPage === totalPages || totalPages === 0;
    }

    document.getElementById("prevPage").addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage--;
            updateMemberPagination();
        }
    });

    document.getElementById("nextPage").addEventListener("click", () => {
        const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            updateMemberPagination();
        }
    });

    [filterID, filterType, filterPlan, filterStatus].forEach(input => {
        input.addEventListener("input", applyMemberFilters);
        input.addEventListener("change", applyMemberFilters);
    });

    applyMemberFilters();



    /* ============================================================
        RENEWAL REQUESTS — FILTERS + PAGINATION
    ============================================================ */

    const filterRenewalID = document.getElementById("filterRenewalID");
    const filterRenewalType = document.getElementById("filterMemberType");
    const filterRenewalPlan = document.getElementById("filterCurrentPlan");
    const filterRenewalStatus = document.getElementById("filterRenewalStatus");

    const renewalRows = document.querySelectorAll(".renewal-member-table tbody tr");

    let renewalRowsFiltered = Array.from(renewalRows);
    let renewalPage = 1;
    const renewalRowsPerPage = 10;

    function applyRenewalFilters() {
        const idValue = filterRenewalID.value.toLowerCase();
        const typeValue = filterRenewalType.value;
        const planValue = filterRenewalPlan.value;
        const statusValue = filterRenewalStatus.value;

        renewalRowsFiltered = Array.from(renewalRows).filter(row => {
            const id = row.cells[0].textContent.toLowerCase();
            const type = row.cells[2].textContent;
            const plan = row.cells[3].textContent;
            const status = row.cells[5].textContent;

            return (
                id.includes(idValue) &&
                (!typeValue || type === typeValue) &&
                (!planValue || plan === planValue) &&
                (!statusValue || status === statusValue)
            );
        });

        renewalPage = 1;
        updateRenewalPagination();
    }

    function updateRenewalPagination() {
        const totalPages = Math.ceil(renewalRowsFiltered.length / renewalRowsPerPage);
        const tableBody = document.getElementById("renewalTableBody");

        tableBody.classList.add("fade-out");

        setTimeout(() => {
            renewalRows.forEach(row => (row.style.display = "none"));

            const start = (renewalPage - 1) * renewalRowsPerPage;
            const end = start + renewalRowsPerPage;

            renewalRowsFiltered.slice(start, end).forEach(row => {
                row.style.display = "";
            });

            renderRenewalPageNumbers(totalPages);

            tableBody.classList.remove("fade-out");
            tableBody.classList.add("fade-in");

            setTimeout(() => tableBody.classList.remove("fade-in"), 250);
        }, 200);
    }


    function renderRenewalPageNumbers(totalPages) {
        const pageNumbersDiv = document.getElementById("renewalPageNumbers");
        pageNumbersDiv.innerHTML = "";

        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement("button");
            btn.textContent = i;
            btn.classList.add("page-number");
            if (i === renewalPage) btn.classList.add("active");

            btn.addEventListener("click", () => {
                renewalPage = i;
                updateRenewalPagination();
            });

            pageNumbersDiv.appendChild(btn);
        }

        document.getElementById("prevRenewalPage").disabled = renewalPage === 1;
        document.getElementById("nextRenewalPage").disabled =
            renewalPage === totalPages || totalPages === 0;
    }

    document.getElementById("prevRenewalPage").addEventListener("click", () => {
        if (renewalPage > 1) {
            renewalPage--;
            updateRenewalPagination();
        }
    });

    document.getElementById("nextRenewalPage").addEventListener("click", () => {
        const totalPages = Math.ceil(renewalRowsFiltered.length / renewalRowsPerPage);
        if (renewalPage < totalPages) {
            renewalPage++;
            updateRenewalPagination();
        }
    });

    [
        filterRenewalID,
        filterRenewalType,
        filterRenewalPlan,
        filterRenewalStatus
    ].forEach(input => {
        input.addEventListener("input", applyRenewalFilters);
        input.addEventListener("change", applyRenewalFilters);
    });

    applyRenewalFilters();

});
