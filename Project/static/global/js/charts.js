// charts.js
if (!window.dashboardChartsInitialized) {
    window.dashboardChartsInitialized = true;

    document.addEventListener("DOMContentLoaded", () => {

        // =========================
        // GLOBAL CHART CACHE
        // =========================
        window.membershipChart = null;
        window.renewalChart = null;
        window.expirationChart = null;
        window.weeklyRevenueChart = null;
        window.paymentChartInstance = null;

        // =========================
        // HELPER FUNCTIONS
        // =========================
        const makeGradient = (ctx, top, bottom) => {
            const g = ctx.createLinearGradient(0, 0, 0, ctx.canvas.height);
            g.addColorStop(0, top);
            g.addColorStop(1, bottom);
            return g;
        };

        const chartOptions = () => ({
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 700 },
            plugins: {
                legend: { labels: { color: "#00ffe0" } },
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: ${ctx.parsed?.y ?? ctx.parsed}`
                    }
                }
            },
            scales: {
                x: { ticks: { color: "#00ffe0" }, grid: { color: "rgba(0,255,234,0.05)" } },
                y: { ticks: { color: "#00ffe0" }, grid: { color: "rgba(0,255,234,0.05)" }, beginAtZero: true }
            }
        });

        const barOptions = () => ({ ...chartOptions(), plugins: { legend: { display: false } } });

        const doughnutOptions = () => ({
            responsive: true,
            maintainAspectRatio: false,
            cutout: "70%",
            plugins: { legend: { display: false } }
        });

        // =========================
        // CHART INITIALIZER
        // =========================
        window.initCharts = (data) => {

            // --- Membership Overview Line Chart ---
            const overviewCtx = document.getElementById("membershipChart")?.getContext("2d");
            if (overviewCtx) {
                window.membershipChart?.destroy();
                window.membershipChart = new Chart(overviewCtx, {
                    type: "line",
                    data: {
                        labels: data.overview_chart.labels,
                        datasets: [
                            {
                                label: "Students",
                                data: data.overview_chart.students,
                                borderColor: "#00c8ff",
                                backgroundColor: ctx => makeGradient(ctx.chart.ctx, "rgba(0,200,255,0.4)", "rgba(0,200,255,0.05)"),
                                fill: true,
                                tension: 0.35,
                                borderWidth: 2
                            },
                            {
                                label: "Faculty",
                                data: data.overview_chart.faculty,
                                borderColor: "#ffd700",
                                backgroundColor: ctx => makeGradient(ctx.chart.ctx, "rgba(255,215,0,0.4)", "rgba(255,215,0,0.05)"),
                                fill: true,
                                tension: 0.35,
                                borderWidth: 2
                            },
                            {
                                label: "Outsiders",
                                data: data.overview_chart.outsiders,
                                borderColor: "#ff5078",
                                backgroundColor: ctx => makeGradient(ctx.chart.ctx, "rgba(255,80,120,0.4)", "rgba(255,80,120,0.05)"),
                                fill: true,
                                tension: 0.35,
                                borderWidth: 2
                            }
                        ]
                    },
                    options: chartOptions()
                });
            }

            // --- Renewal/Payments Bar Chart ---
            const renewCtx = document.getElementById("renewalChart")?.getContext("2d");
            if (renewCtx) {
                window.renewalChart?.destroy();
                window.renewalChart = new Chart(renewCtx, {
                    type: "bar",
                    data: {
                        labels: data.status_overview.labels,
                        datasets: [{
                            data: data.status_overview.values,
                            backgroundColor: ctx => makeGradient(ctx.chart.ctx, "rgba(0,255,163,0.8)", "rgba(0,255,234,0.2)"),
                            borderColor: "rgba(0,255,163,0.8)",
                            borderWidth: 2,
                            borderRadius: 8
                        }]
                    },
                    options: barOptions()
                });
            }

            // --- Active Members Doughnut ---
            const expCtx = document.getElementById("expirationChart")?.getContext("2d");
            if (expCtx) {
                window.expirationChart?.destroy();
                const colors = [
                    ["rgba(6, 46, 58, 0.7)", "rgba(0,200,255,0.2)"],
                    ["rgba(72,218,32,0.7)", "rgba(72,218,32,0.2)"],
                    ["rgba(255,80,120,0.7)", "rgba(255,80,120,0.2)"]
                ];
                window.expirationChart = new Chart(expCtx, {
                    type: "doughnut",
                    data: {
                        labels: ["Students", "Faculty", "Outsiders"],
                        datasets: [{
                            data: data.status_chart.values,
                            backgroundColor: ctx => makeGradient(ctx.chart.ctx, colors[ctx.dataIndex][0], colors[ctx.dataIndex][1]),
                            borderColor: "#00ffe0",
                            borderWidth: 1
                        }]
                    },
                    options: doughnutOptions()
                });
            }

            // --- Weekly Revenue Line Chart ---
            const weeklyCtx = document.getElementById("weeklyRevenueChart")?.getContext("2d");
            if (weeklyCtx && data.weekly_revenue) {
                window.weeklyRevenueChart?.destroy();
                window.weeklyRevenueChart = new Chart(weeklyCtx, {
                    type: "line",
                    data: {
                        labels: data.weekly_revenue.labels,
                        datasets: [{
                            label: "Revenue (₱)",
                            data: data.weekly_revenue.values,
                            borderColor: "#00ffb0",
                            backgroundColor: ctx => makeGradient(ctx.chart.ctx, "rgba(0,255,176,0.4)", "rgba(0,255,176,0.05)"),
                            fill: true,
                            tension: 0.3,
                            borderWidth: 2,
                            pointRadius: 4,
                            pointBackgroundColor: "#00ffb0"
                        }]
                    },
                    options: { ...chartOptions(), plugins: { legend: { display: false } } }
                });
            }

            // --- Payment Status Chart ---
            const paymentCtx = document.getElementById("paymentChart")?.getContext("2d");
            if (paymentCtx && data.payment_status_chart) {
                window.paymentChartInstance?.destroy();
                const colors = [
                    ["rgba(0,255,100,0.8)", "rgba(0,255,100,0.2)"],
                    ["rgba(255,215,0,0.8)", "rgba(255,215,0,0.2)"],
                    ["rgba(255,70,120,0.8)", "rgba(255,70,120,0.2)"]
                ];
                window.paymentChartInstance = new Chart(paymentCtx, {
                    type: "bar",
                    data: {
                        labels: data.payment_status_chart.labels,
                        datasets: [{
                            data: data.payment_status_chart.values,
                            backgroundColor: ctx => makeGradient(ctx.chart.ctx, colors[ctx.dataIndex][0], colors[ctx.dataIndex][1]),
                            borderColor: ["rgba(0,255,100,0.8)","rgba(255,215,0,0.8)","rgba(255,70,120,0.8)"],
                            borderWidth: 2,
                            borderRadius: 8
                        }]
                    },
                    options: barOptions()
                });
            }

        };

    });
}
