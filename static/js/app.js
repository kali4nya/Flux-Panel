const MAX_POINTS = 15;

/* ------------------ SOCKET & POLLING ------------------ */
let socket;
let pollingSlider = document.getElementById("pollingSlider");
let pollingLabel = document.getElementById("pollingValue");

/* ------------------ COOKIE ------------------ */
function getPollingFromCookie() {
    const match = document.cookie.match(/pollingRate=(\d+)/);
    return match ? parseInt(match[1]) : 1000;
}

function setPollingCookie(value) {
    document.cookie = `pollingRate=${value}; path=/; max-age=31536000`;
}

/* ------------------ CHART ------------------ */
function createGradient(ctx, color) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 250);
    gradient.addColorStop(0, color + "88");
    gradient.addColorStop(0.4, color + "44");
    gradient.addColorStop(1, color + "00");
    return gradient;
}

function createChart(canvasId, lineColor) {
    const ctx = document.getElementById(canvasId).getContext("2d");
    const gradient = createGradient(ctx, lineColor);

    return new Chart(ctx, {
        type: "line",
        data: {
            labels: new Array(MAX_POINTS).fill(""),
            datasets: [{
                data: new Array(MAX_POINTS).fill(null),
                borderColor: lineColor,
                backgroundColor: gradient,
                borderWidth: 2,
                fill: true,
                tension: 0.35,
                pointRadius: 0
            }]
        },
        options: {
            animation: false,
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "nearest", intersect: false },
            scales: {
                x: { display: false },
                y: { min: 0, max: 100, ticks: { stepSize: 20 }, grid: { color: "#1f232b" } }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    enabled: true,
                    displayColors: false,
                    callbacks: {
                        title: () => "",
                        label: (ctx) => `${ctx.parsed.y}%`
                    }
                }
            }
        }
    });
}

const cpuChart = createChart("cpuChart", "#3b82f6");
const ramChart = createChart("ramChart", "#22c55e");

function pushData(chart, value) {
    chart.data.datasets[0].data.shift();
    chart.data.datasets[0].data.push(value);
    chart.update();
}

/* ------------------ SOCKET.IO ------------------ */
function initSocket() {
    socket = io();

    // Send initial polling interval
    const initialInterval = getPollingFromCookie();
    socket.emit("set_config", { interval: initialInterval });

    pollingSlider.value = initialInterval;
    pollingLabel.innerText = initialInterval + " ms";

    socket.on("stats_update", (data) => {
        // CPU
        const cpuUtilization = data.cpu?.usage_percent ?? 0;
        const cpuTemperature = data.cpu?.temperature_c != null ? data.cpu.temperature_c + "°C" : "--°C";
        document.getElementById("cpuUtilization").innerText = cpuUtilization + "%";
        document.getElementById("cpuTemperature").innerText = cpuTemperature;

        // RAM
        const ramUsagePercent = data.ram?.usage_percent ?? 0;
        const ramUsed = data.ram?.used_mb ?? 0;
        const ramTotal = data.ram?.total_mb ?? 0;
        document.getElementById("ramUtilization").innerHTML = `
            ${ramUsagePercent}%<div class="stat-subvalue">(${ramUsed.toFixed(1)} / ${ramTotal.toFixed(1)} MB)</div>
        `;

        // GPU
        const gpuUtilization = data.gpu?.usage_percent ?? 0;
        const gpuTemperature = data.gpu?.temperature_c != null ? data.gpu.temperature_c + "°C" : "--°C";
        document.getElementById("gpuUtilization").innerText = gpuUtilization + "%";
        document.getElementById("gpuTemperature").innerText = gpuTemperature;

        // Drives
        const drivesContainer = document.getElementById("drivesContainer");
        drivesContainer.innerHTML = ""; // clear previous

        if (Array.isArray(data.storage) && data.storage.length > 0) {
            data.storage.forEach((drive) => {
                // Convert MB to GB only if > 1024
                let used = drive.used_gb ?? 0;
                let total = drive.total_gb ?? 0;

                if (used > 1024) used = used / 1024;
                if (total > 1024) total = total / 1024;

                const usagePercent = drive.usage_percent ?? 0;
                const label = drive.mount ?? drive.name ?? "Drive";

                const driveCard = document.createElement("div");
                driveCard.className = "card stat-card";
                driveCard.innerHTML = `
                    <div class="stat-label">${label}</div>
                    <div class="stat-value">
                        ${usagePercent}% 
                        <div class="stat-subvalue">(${used.toFixed(2)} / ${total.toFixed(2)} GB)</div>
                    </div>
                `;
                drivesContainer.appendChild(driveCard);
            });
        }

        // Update charts
        pushData(cpuChart, cpuUtilization);
        pushData(ramChart, ramUsagePercent);
    });

    socket.on("config_updated", (data) => {
        console.log("Polling interval updated on server:", data.interval);
    });
}

/* ------------------ SLIDER ------------------ */
function updatePolling() {
    const newInterval = parseInt(pollingSlider.value);
    pollingLabel.innerText = newInterval + " ms";
    setPollingCookie(newInterval);

    if (socket) {
        socket.emit("set_config", { interval: newInterval });
    }
}

pollingSlider.addEventListener("input", updatePolling);

/* ------------------ INIT ------------------ */
initSocket();