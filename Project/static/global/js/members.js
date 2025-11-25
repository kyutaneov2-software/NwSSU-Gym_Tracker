    document.addEventListener('DOMContentLoaded', () => {

    /* ==========================
        ADD MEMBER MODAL
    ========================== */
        const addModal = document.getElementById('memberModal');
        const openAddBtn = document.getElementById('openModalBtn');
        const closeAddBtn = document.getElementById('closeModalBtn');
        const cancelAddBtn = document.getElementById('cancelModalBtn');

        const openAddModal = () => {
            if (!addModal) return;
            addModal.style.display = 'flex';
            addModal.setAttribute('aria-hidden', 'false');
        };

        const closeAddModal = () => {
            if (!addModal) return;
            addModal.style.display = 'none';
            addModal.setAttribute('aria-hidden', 'true');
        };

        if (openAddBtn) openAddBtn.addEventListener('click', openAddModal);
        if (closeAddBtn) closeAddBtn.addEventListener('click', closeAddModal);
        if (cancelAddBtn) cancelAddBtn.addEventListener('click', closeAddModal);

        window.addEventListener('click', e => {
            if (e.target === addModal) closeAddModal();
        });
        window.addEventListener('keydown', e => {
            if ((e.key === 'Escape' || e.key === 'Esc') && addModal.style.display === 'flex') {
                closeAddModal();
            }
        });

    /* ==========================
    ADD MEMBER FORM SUBMISSION
    ========================== */
    const addForm = document.getElementById('addMemberForm');

    if (addForm) {
        addForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(addForm);

            try {
                const res = await fetch('/admin/add-member', {
                    method: 'POST',
                    body: formData
                });

                const result = await res.json();

                if (result.success) {
                    alert(result.message); // shows "New member registered successfully! Paid ₱XXX.XX"

                    // Refresh members list & dashboard stats
                    await refreshMemberTable();
                    await refreshDashboardSummary();

                    // Close the modal
                    document.getElementById('memberModal').style.display = 'none';
                    addForm.reset();
                } else {
                    alert('❌ Registration failed: ' + (result.error || 'Unknown error'));
                }
            } catch (err) {
                console.error('Error submitting form:', err);
                alert('Something went wrong while adding the member.');
            }
        });
    }


    /* ==========================
        SHOW STUDENT FIELD ON TYPE SELECT
    ========================== */
        const memberTypeSelect = document.getElementById("member_type");
        const studentField = document.getElementById("studentField");

        if (memberTypeSelect && studentField) {
            memberTypeSelect.addEventListener("change", () => {
                if (memberTypeSelect.value === "Student") {
                    studentField.classList.remove("hidden");
                } else {
                    studentField.classList.add("hidden");
                }
            });
        }


    /* ==========================
        START & END DATE LIMITS
    ========================== */
        const today = new Date().toISOString().split("T")[0];
        const startDate = document.getElementById("Start_date");
        const endDate = document.getElementById("End_date");

        if (startDate && endDate) {
            startDate.min = today;
            endDate.min = today;

            startDate.addEventListener("change", () => {
                endDate.min = startDate.value;
            });
        }


    /* ==========================
        VIEW / EDIT / DELETE MEMBER
    ========================== */
        const memberModal = document.getElementById('memberInformation');
        const closeViewBtn = document.getElementById('closeMemberInfoBtn');
        const editModal = document.getElementById('editMemberModal');
        const closeEditBtn = document.getElementById('closeEditModalBtn');
        const editForm = document.getElementById('editMemberForm');

        const viewButtons = document.querySelectorAll('.table-btn.view');
        const editButtons = document.querySelectorAll('.table-btn.edit');
        const deleteButtons = document.querySelectorAll('.table-btn.delete');

        // ========== VIEW ==========
        viewButtons.forEach(btn => {
            btn.addEventListener('click', async () => {
                const memberId = btn.dataset.id;
                try {
                    // Fetch member data from python route
                    const res = await fetch(`/admin/member/${memberId}`);
                    if (!res.ok) throw new Error('Failed to fetch member data');
                    const data = await res.json();

                    // Fill users modal data
                    document.getElementById('infoName').textContent = `${data.first_name} ${data.last_name}`;
                    document.getElementById('infoMemberId').textContent = `Member ID: ${data.unique_code}`;
                    document.getElementById('infoAge').textContent = data.age || '—';
                    document.getElementById('infoGender').textContent = data.gender || '—';
                    document.getElementById('infoType').textContent = data.member_type;
                    document.getElementById('infoPlan').textContent = data.gym_plan;
                    document.getElementById('infoEmail').textContent = data.email || '—';
                    document.getElementById('infoContact').textContent = data.contact_number || '—';
                    document.getElementById('infoAddress').textContent = data.address || '—';
                    document.getElementById('infoStart').textContent = data.start_date;
                    document.getElementById('infoEnd').textContent = data.end_date;
                    document.getElementById('infoStatus').textContent = data.status;
                    document.getElementById('infoPayment').textContent = data.payment_status;

                    memberModal.style.display = 'flex';
                    memberModal.setAttribute('aria-hidden', 'false');
                } catch (err) {
                    console.error(err);
                    alert('Error loading member information.');
                }
            });
        });

        // Close View Button
        if (closeViewBtn) {
            closeViewBtn.addEventListener('click', () => {
                memberModal.style.display = 'none';
                memberModal.setAttribute('aria-hidden', 'true');
            });
        }
        window.addEventListener('click', e => {
            if (e.target === memberModal) {
                memberModal.style.display = 'none';
                memberModal.setAttribute('aria-hidden', 'true');
            }
        });


        // ========== EDIT ==========
        editButtons.forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.dataset.id;

                // Fetch member data from python route
                const res = await fetch(`/admin/member/${id}`);
                if (!res.ok) return alert('Failed to fetch member data');
                const data = await res.json();

                // Store the member ID in hidden input
                document.getElementById('editHiddenId').value = id;

                // Fill users modal data and chnage the value
                document.getElementById('editFirstName').value = data.first_name;
                document.getElementById('editLastName').value = data.last_name;
                document.getElementById('editAge').value = data.age || '';
                document.getElementById('editGender').value = data.gender || 'Male';
                document.getElementById('editPlan').value = data.gym_plan;
                document.getElementById('editEmail').value = data.email || '';
                document.getElementById('editContact').value = data.contact_number || '';
                document.getElementById('editAddress').value = data.address || '';
                document.getElementById('editStart').value = data.start_date;
                document.getElementById('editEnd').value = data.end_date;
                document.getElementById('editStatus').value = data.status;
                document.getElementById('paymentStatus').value = data.payment_status;

                // Open modal
                editModal.style.display = 'flex';
                editModal.setAttribute('aria-hidden', 'false');
            });
        });

        // Close Edit Button
        if (closeEditBtn) {
            closeEditBtn.addEventListener('click', () => {
                editModal.style.display = 'none';
                editModal.setAttribute('aria-hidden', 'true');
            });
        }

        // Edit form submission
        if (editForm) {
            editForm.addEventListener('submit', async e => {
                e.preventDefault();

                //Get user ID and store it as a dict
                const id = document.getElementById('editHiddenId').value;
                const updatedData = {
                    first_name: document.getElementById('editFirstName').value,
                    last_name: document.getElementById('editLastName').value,
                    age: document.getElementById('editAge').value,
                    gender: document.getElementById('editGender').value,
                    //member_type: document.getElementById('editType').value,
                    gym_plan: document.getElementById('editPlan').value,
                    email: document.getElementById('editEmail').value,
                    contact_number: document.getElementById('editContact').value,
                    address: document.getElementById('editAddress').value,
                    start_date: document.getElementById('editStart').value,
                    end_date: document.getElementById('editEnd').value,
                    status: document.getElementById('editStatus').value,
                    payment_status: document.getElementById('paymentStatus').value
                };


                const res = await fetch(`/admin/member/${id}/edit`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(updatedData)
                });

                const result = await res.json();

                if (result.success) {
                    editModal.style.display = 'none';
                    location.reload();

                    // Refresh table and dashboard
                    await refreshMemberTable();
                } else {
                    alert('Update failed: ' + (result.error || 'Unknown error'));
                }
            });
        }

        // ========== DELETE ==========
        deleteButtons.forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.dataset.id;
                if (!confirm('Are you sure you want to delete this member?')) return;
                const res = await fetch(`/admin/member/${id}/delete`, { method: 'DELETE' });
                const result = await res.json();

                if (result.success) {
                    alert('Member deleted!');
                    location.reload();
                } else {
                    alert(result.error);
                }
            });
        });

        // ========== Refresh Registered Members Table ==========
        async function refreshMemberTable() {
            const res = await fetch("/admin/members-json");
            const data = await res.json();
            const tableBody = document.getElementById("memberTableBody");

            tableBody.innerHTML = ""; // Clear old rows

            data.members.forEach(member => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${member.unique_code}</td>
                    <td>${member.first_name} ${member.last_name}</td>
                    <td>${member.member_type}</td>
                    <td>${member.gym_plan}</td>
                    <td>${member.status}</td>
                    <td>${member.payment_status}</td>
                    <td>
                        <button class="table-btn view" data-id="${member.member_id}">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="table-btn edit" data-id="${member.member_id}">
                            <i class="fas fa-pen"></i>
                        </button>
                        <button class="table-btn delete" data-id="${member.member_id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tableBody.appendChild(row);
            });

            // Reattach button listeners so new rows work too
            attachMemberActionButtons();
        }

        // ========== Refresh Renewal Requests Table ==========
        async function refreshRenewalTable() {
            const res = await fetch("/admin/renewals-json");
            const data = await res.json();
            const tableBody = document.getElementById("renewalTableBody");

            tableBody.innerHTML = ""; // Clear old rows

            data.renewals.forEach(r => {
                const row = document.createElement("tr");

                row.innerHTML = `
                    <td>${r.id}</td>
                    <td>${r.first_name} ${r.last_name}</td>
                    <td>${r.member_type}</td>
                    <td>${r.current_plan}</td>
                    <td>${r.requested_plan}</td>
                    <td class="${r.status === "Pending" ? "pending-status" :
                            r.status === "Approved" ? "approved-status" :
                            "denied-status"}">
                        ${r.status}
                    </td>
                    <td>
                        ${
                            r.status === "Pending"
                                ? `
                                    <button class="table-btn approve" 
                                        data-id="${r.id}"
                                        data-url="/admin/renewal/${r.id}">
                                        Approve
                                    </button>
                                    <button class="table-btn deny" 
                                        data-id="${r.id}"
                                        data-url="/admin/renewal/${r.id}">
                                        Deny
                                    </button>
                                `
                                : `<button class="table-btn delete" data-id="${r.id}">Delete</button>`
                        }
                    </td>
                `;

                tableBody.appendChild(row);
            });

            // Reattach buttons
            attachRenewalActionButtons();
            attachDeleteButtons();

            // Reapply filters + pagination
            applyRenewalFilters();
        }



        function attachMemberActionButtons() {
            document.querySelectorAll('.table-btn.edit').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const id = btn.dataset.id; 
                    const res = await fetch(`/admin/member/${id}`);
                    if (!res.ok) return alert('Failed to fetch member data');
                    const data = await res.json();

                    // get and show edit modal
                    document.getElementById('editMemberId').value = data.member_id;
                    document.getElementById('editFirstName').value = data.first_name;
                    document.getElementById('editLastName').value = data.last_name;
                    document.getElementById('editType').value = data.member_type;
                    document.getElementById('editPlan').value = data.gym_plan;
                    document.getElementById('editStatus').value = data.status;
                    document.getElementById('paymentStatus').value = data.status;
                    editModal.style.display = 'flex';
                });
            });

            // 
            document.querySelectorAll('.table-btn.delete').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const id = btn.dataset.id;
                    if (!confirm('Are you sure you want to delete this member?')) return;
                    const res = await fetch(`/admin/member/${id}/delete`, { method: 'DELETE' });
                    const result = await res.json();
                    if (result.success) {
                        alert('Member deleted!');
                        await refreshMemberTable();
                        await refreshDashboardSummary();
                    } else {
                        alert(result.error);
                    }
                });
            });
        }

        /* ==========================
        HANDLE RENEWAL REQUEST APPROVE / DENY
        ========================== */
        function attachRenewalActionButtons() {
            document.querySelectorAll(".table-btn.approve").forEach(btn => {
                btn.addEventListener("click", async () => {
                    const url = btn.dataset.url;

                    if (!confirm("Approve this renewal request?")) return;

                    const response = await fetch(url, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ status: "Approved" })
                    });

                    const result = await response.json();
                    if (result.success) {
                        alert("Renewal approved!");
                        await refreshRenewalTable();
                    } else {
                        alert("Failed: " + result.message);
                    }
                });
            });


            document.querySelectorAll(".table-btn.deny").forEach(btn => {
                btn.addEventListener("click", async () => {
                    const url = btn.dataset.url;

                    if (!confirm("Deny this renewal request?")) return;

                    const response = await fetch(url, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ status: "Denied" })
                    });

                    const result = await response.json();
                    if (result.success) {
                        alert("Renewal denied.");
                        await refreshRenewalTable();
                    } else {
                        alert("Failed to deny.");
                    }
                });
            });

        }
        function attachDeleteButtons() {
            document.querySelectorAll(".table-btn.delete").forEach(btn => {
                btn.addEventListener("click", async () => {
                    const id = btn.dataset.id;

                    if (!confirm("Delete this renewal request?")) return;

                    const response = await fetch(`/admin/renewal/delete/${id}`, {
                        method: "DELETE"
                    });

                    const result = await response.json();
                    if (result.success) {
                        alert("Renewal request deleted.");
                        location.reload();
                    } else {
                        alert("Delete failed: " + result.message);
                    }
                });
            });
        }


        // Attach once when page loads
        attachRenewalActionButtons();
        attachDeleteButtons();
    });


