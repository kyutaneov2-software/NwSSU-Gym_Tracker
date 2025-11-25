document.addEventListener("DOMContentLoaded", () => {

    // ===========================================================
    // FETCH AND DISPLAY MEMBERSHIP REVENUE
    // ===========================================================
    loadRevenueStats();

    // ===========================================================
    // GLOBAL CHART OPTIONS + GRADIENT MAKER
    // ===========================================================
    const chartOptions = () => ({
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 700 },
        plugins: {
            legend: { labels: { color: "#00ffe0" } },
            tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.parsed?.y ?? ctx.parsed}` } }
        },
        scales: {
            x: { ticks: { color: "#00ffe0" }, grid: { color: "rgba(0,255,234,0.05)" } },
            y: { ticks: { color: "#00ffe0" }, grid: { color: "rgba(0,255,234,0.05)" }, beginAtZero: true }
        }
    });

    const makeGradient = (ctx, top, bottom) => {
        const g = ctx.createLinearGradient(0, 0, 0, 300);
        g.addColorStop(0, top);
        g.addColorStop(1, bottom);
        return g;
    };

    // ===========================================================
    // CHART INSTANCES
    // ===========================================================
    let membershipChart = null;
    let renewalChart = null;
    let expirationChart = null;
    let paymentChartInstance = null;
    let weeklyRevenueChart = null;

    // ===========================================================
    // UPDATE MEMBER SUMMARY (SAFE FOR ANY PAGE)
    // ===========================================================
    function updateMemberSummary(summary) {
        const containers = document.querySelectorAll(".member-summary, .statistics-summary");
        if (!containers.length) return;

        containers.forEach(container => {
            container.innerHTML = "";

            // Main summary cards
            const mainCards = [
                { icon: "fas fa-users", title: "Total Members", value: summary.total },
                { icon: "fas fa-user-check", title: "Active Members", value: summary.active },
                { icon: "fas fa-chart-bar", title: "Most Active Group", value: summary.most_active }
            ];

            mainCards.forEach((card, i) => {
                const div = document.createElement("div");
                div.className = "summary-card";
                div.innerHTML = `
                    <i class="${card.icon} summary-icon"></i>
                    <h3>${card.title}</h3>
                    <p>${typeof card.value === "number" ? card.value.toLocaleString() : card.value}</p>
                `;
                div.style.animation = `fadeUp 0.6s ease ${i * 0.1}s forwards`;
                container.appendChild(div);
            });

            // Only add type breakdown for dashboard
            if (container.classList.contains("member-summary") && summary.students !== undefined) {
                const typeContainer = document.createElement("div");
                typeContainer.className = "member-type-breakdown";

                const types = [
                    { name: "Students", value: summary.students },
                    { name: "Faculty", value: summary.faculty },
                    { name: "Outsiders", value: summary.outsiders }
                ];

                types.forEach(t => {
                    const div = document.createElement("div");
                    div.className = "breakdown-card";
                    div.innerHTML = `<h4>${t.name}</h4><p>${t.value.toLocaleString()}</p>`;
                    typeContainer.appendChild(div);
                });

                container.appendChild(typeContainer);
            }
        });
    }

    // ===========================================================
    // INITIALIZE CHARTS (ONLY IF CANVAS EXISTS)
    // ===========================================================
    const initCharts = (data) => {
        if (!data) return;

        updateMemberSummary(data.summary);

        // === Payment Status Chart ===
        const paymentCtx = document.getElementById("paymentChart")?.getContext("2d");
        if (paymentCtx) {
            paymentChartInstance?.destroy();
            const gradients = [
                makeGradient(paymentCtx, "rgba(0,255,100,0.8)", "rgba(0,255,100,0.2)"),
                makeGradient(paymentCtx, "rgba(255,215,0,0.8)", "rgba(255,215,0,0.2)"),
                makeGradient(paymentCtx, "rgba(255,70,120,0.8)", "rgba(255,70,120,0.2)")
            ];
            paymentChartInstance = new Chart(paymentCtx, {
                type: "bar",
                data: {
                    labels: data.payment_status_chart.labels,
                    datasets: [{
                        data: data.payment_status_chart.values,
                        backgroundColor: gradients,
                        borderColor: ["rgba(0,255,100,0.8)", "rgba(255,215,0,0.8)", "rgba(255,70,120,0.8)"],
                        borderWidth: 2,
                        borderRadius: 8
                    }]
                },
                options: { ...chartOptions(), plugins: { legend: { display: false } } }
            });
        }

        // === Membership Overview Line Chart ===
        const overviewCtx = document.getElementById("membershipChart")?.getContext("2d");
        if (overviewCtx) {
            membershipChart?.destroy();
            membershipChart = new Chart(overviewCtx, {
                type: "line",
                data: {
                    labels: data.overview_chart.labels,
                    datasets: [
                        { label: "Students", data: data.overview_chart.students, borderColor: "#00c8ff",
                        backgroundColor: makeGradient(overviewCtx, "rgba(0,200,255,0.4)", "rgba(0,200,255,0.05)"),
                        fill: true, tension: 0.35, borderWidth: 2 },
                        { label: "Faculty", data: data.overview_chart.faculty, borderColor: "#ffd700",
                        backgroundColor: makeGradient(overviewCtx, "rgba(255,215,0,0.4)", "rgba(255,215,0,0.05)"),
                        fill: true, tension: 0.35, borderWidth: 2 },
                        { label: "Outsiders", data: data.overview_chart.outsiders, borderColor: "#ff5078",
                        backgroundColor: makeGradient(overviewCtx, "rgba(255,80,120,0.4)", "rgba(255,80,120,0.05)"),
                        fill: true, tension: 0.35, borderWidth: 2 }
                    ]
                },
                options: { ...chartOptions(), plugins: { legend: { display: false } } }
            });
        }

        // === Renewal Doughnut Chart ===
        const renewalCtx = document.getElementById("renewalChart")?.getContext("2d");
        if (renewalCtx) {
            renewalChart?.destroy();
            renewalChart = new Chart(renewalCtx, {
                type: "doughnut",
                data: {
                    labels: data.status_overview.labels,
                    datasets: [{
                        data: data.status_overview.values,
                        backgroundColor: ["rgba(0,255,100,0.6)", "rgba(255,215,0,0.6)", "rgba(255,70,120,0.6)"],
                        borderColor: ["rgba(0,255,100,1)", "rgba(255,215,0,1)", "rgba(255,70,120,1)"],
                        borderWidth: 2
                    }]
                },
                options: { ...chartOptions(), plugins: { legend: { position: "bottom", labels: { color: "#00ffe0" } } } }
            });
        }

        // === Active Member Bar Chart ===
        const expirationCtx = document.getElementById("expirationChart")?.getContext("2d");
        if (expirationCtx) {
            expirationChart?.destroy();

            // Create gradients for each bar
            const gradientStudent = expirationCtx.createLinearGradient(0, 0, 0, 400);
            gradientStudent.addColorStop(0, "rgba(0, 225, 255, 0.8)");
            gradientStudent.addColorStop(1, "rgba(0, 225, 255, 0.3)");

            const gradientFaculty = expirationCtx.createLinearGradient(0, 0, 0, 400);
            gradientFaculty.addColorStop(0, "rgba(255, 215, 0, 0.8)");
            gradientFaculty.addColorStop(1, "rgba(255, 215, 0, 0.3)");

            const gradientOutsiders = expirationCtx.createLinearGradient(0, 0, 0, 400);
            gradientOutsiders.addColorStop(0, "rgba(255, 70, 120, 0.8)");
            gradientOutsiders.addColorStop(1, "rgba(255, 70, 120, 0.3)");

            expirationChart = new Chart(expirationCtx, {
                type: "bar",
                data: {
                    labels: ["Students", "Faculty", "Outsiders"],
                    datasets: [{
                        label: "Active Members",
                        data: data.status_chart.values,
                        backgroundColor: [gradientStudent, gradientFaculty, gradientOutsiders],
                        borderColor: ["rgba(0,200,255,1)", "rgba(255,215,0,1)", "rgba(255,80,120,1)"],
                        borderWidth: 2,
                        borderRadius: 10 // <-- rounded corners
                    }]
                },
                options: {
                    ...chartOptions(),
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { 
                            grid: { display: false },
                            ticks: { color: "#fff" }
                        },
                        y: { 
                            beginAtZero: true,
                            ticks: { color: "#fff" }
                        }
                    }
                }
            });
        }


        // === Weekly Revenue Line Chart ===
        const weeklyCtx = document.getElementById("weeklyRevenueChart")?.getContext("2d");
        if (weeklyCtx && data.weekly_revenue) {
            weeklyRevenueChart?.destroy();
            weeklyRevenueChart = new Chart(weeklyCtx, {
                type: "line",
                data: {
                    labels: data.weekly_revenue.labels,
                    datasets: [{
                        label: "Revenue (₱)",
                        data: data.weekly_revenue.values,
                        borderColor: "#00ffb0",
                        backgroundColor: makeGradient(weeklyCtx, "rgba(0,255,176,0.4)", "rgba(0,255,176,0.05)"),
                        tension: 0.3,
                        fill: true,
                        borderWidth: 2,
                        pointRadius: 4,
                        pointBackgroundColor: "#00ffb0"
                    }]
                },
                options: { ...chartOptions(), plugins: { legend: { display: false } } }
            });
        }
    };

    // ===========================================================
    // FETCH DASHBOARD STATISTICS
    // ===========================================================
    fetch("/admin/statistics-summary")
        .then(res => res.json())
        .then(initCharts)
        .catch(err => console.error("Dashboard load failed:", err));

    // ===========================================================
    // FETCH MEMBERSHIP LOGS
    // ===========================================================
    const logList = document.getElementById("logList");
    const timestamp = document.getElementById("revenueTimestamp");

    if (logList) {
        fetch("/admin/membership-logs")
            .then(res => res.json())
            .then(data => {
                logList.innerHTML = "";
                if (!data || !data.length) {
                    logList.innerHTML = "<li class='log-empty'>No logs for the past 7 days.</li>";
                    return;
                }
                data.forEach(log => {
                    const li = document.createElement("li");
                    li.className = "log-item";
                    li.innerHTML = `
                        <div class="log-entry">
                            <p><strong>${log.member_name}</strong> — ${log.action_type}</p>
                            <small>${log.action_date}</small>
                        </div>
                        <p class="log-remarks">${log.remarks || ""}</p>
                    `;
                    logList.appendChild(li);
                });
                if (timestamp) {
                    timestamp.textContent = `Last updated: ${new Date().toLocaleString("en-PH", { hour12: true })}`;
                }
            })
            .catch(err => {
                console.error("Log loading failed:", err);
                logList.innerHTML = "<li class='log-error'>Failed to load logs.</li>";
            });
    }

});

// ===========================================================
// MEMBERSHIP REVENUE FETCHER
// ===========================================================
function loadRevenueStats() {
    fetch("/admin/members-statistics")
        .then(res => res.json())
        .then(data => {
            if (!data || !data.stats) return;

            const stats = data.stats;
            const formatMoney = n =>
                "₱" + parseFloat(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

            const dailyEl = document.getElementById("dailyRevenueDisplay");
            const monthlyEl = document.getElementById("monthlyRevenueDisplay");
            const totalEl = document.getElementById("totalRevenueDisplay");
            const timestamp = document.getElementById("revenueTimestamp");

            if (dailyEl) dailyEl.textContent = formatMoney(stats.daily_revenue);
            if (monthlyEl) monthlyEl.textContent = formatMoney(stats.monthly_revenue);
            if (totalEl) totalEl.textContent = formatMoney(stats.total_revenue);
            if (timestamp) {
                const now = new Date();
                timestamp.textContent = "Last updated: " + now.toLocaleString("en-US", { hour12: true, year: "numeric", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit" });
            }
        })
        .catch(err => console.error("Error loading stats:", err));
}
