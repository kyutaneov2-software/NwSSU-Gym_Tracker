//FILE NAME: user_membership.js
// Description: JavaScript functions for user membership management
// Modal Functions
    function openRenewModal() {
        document.getElementById('renewModal').style.display = 'flex';
    }
    function closeRenewModal() {
        document.getElementById('renewModal').style.display = 'none';
    }

    // Close modal on outside click
    window.onclick = function(event) {
        const modal = document.getElementById('renewModal');
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

// ========================================
// ATTENDANCE BUTTON LOGIC
// ========================================

// Run when page loads
document.addEventListener("DOMContentLoaded", () => {
    const timeInBtn = document.getElementById("time-in");
    const timeOutBtn = document.getElementById("time-out");
    const statusText = document.getElementById("attendance-status");

    if (!timeInBtn || !timeOutBtn) return;

    fetch("/user/attendance/status")
        .then(res => res.json())
        .then(data => {
            // Disable logic
            timeInBtn.disabled = data.time_in;
            timeOutBtn.disabled = !data.time_in || data.time_out;

            // Status text logic
            if (!data.time_in) {
                statusText.textContent = "You haven't timed in yet.";
            } else if (data.time_in && !data.time_out) {
                statusText.textContent = "You are currently timed in.";
            } else if (data.time_in && data.time_out) {
                statusText.textContent = "You have completed your attendance today.";
            }
        });
});


// TIME IN
document.getElementById("time-in")?.addEventListener("click", () => {
    fetch("/user/attendance/time_in", { method: "POST" })
        .then(res => res.json())
        .then(() => {
            document.getElementById("time-in").disabled = true;
            document.getElementById("time-out").disabled = false;
            document.getElementById("attendance-status").textContent =
                "You are currently timed in.";
        });
});


// TIME OUT
document.getElementById("time-out")?.addEventListener("click", () => {
    fetch("/user/attendance/time_out", { method: "POST" })
        .then(res => res.json())
        .then(() => {
            document.getElementById("time-out").disabled = true;
            document.getElementById("attendance-status").textContent =
                "You have completed your attendance today.";
        });
});
