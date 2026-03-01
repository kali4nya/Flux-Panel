/* ------------------ SOCKET & POLLING ------------------ */
let socket;
let pollingSlider = document.getElementById("pollingSlider");
let pollingLabel = document.getElementById("pollingValue");
let debounceTimer; // Added for performance optimization

/* ------------------ COOKIE ------------------ */
function getPollingFromCookie() {
    const match = document.cookie.match(/pollingRate=(\d+)/);
    return match ? parseInt(match[1]) : null;
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
            labels: new Array(MAX_GRAPH_POINTS).fill(""),
            datasets: [{
                data: new Array(MAX_GRAPH_POINTS).fill(null),
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

let cpuChart, ramChart;

function pushData(chart, value) {
    chart.data.datasets[0].data.shift();
    chart.data.datasets[0].data.push(value);
    chart.update();
}

/* ------------------ SOCKET.IO ------------------ */
function initSocket() {
    socket = io();

    const initialInterval = getPollingFromCookie() || DEFAULT_POLLING;
    pollingSlider.value = initialInterval;
    pollingLabel.innerText = initialInterval + " ms";

    socket.emit("set_config", { interval: initialInterval });

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
        drivesContainer.innerHTML = "";

        if (Array.isArray(data.storage) && data.storage.length > 0) {
            data.storage.forEach((drive) => {
                let used = drive.used_mb ?? 0;
                let total = drive.total_mb ?? 0;

                let usedValue = used;
                let totalValue = total;
                let unit = "GB";

                if (used > 1024) usedValue = used / 1024;
                else unit = "MB";
                if (total > 1024) totalValue = total / 1024;
                else if (unit !== "GB") unit = "MB";

                const usagePercent = drive.usage_percent ?? 0;
                const label = drive.mount ?? drive.name ?? "Drive";

                const driveCard = document.createElement("div");
                driveCard.className = "card stat-card";

                if (DYNAMIC_DRIVE_COLORS) {
                    let color;
                    if (usagePercent <= 50) {
                        color = interpolateColor(DYNAMIC_DRIVE_COLOR_LOW, DYNAMIC_DRIVE_COLOR_MEDIUM, usagePercent / 50);
                    } else {
                        color = interpolateColor(DYNAMIC_DRIVE_COLOR_MEDIUM, DYNAMIC_DRIVE_COLOR_HIGH, (usagePercent - 50) / 50);
                    }
                    driveCard.style.backgroundColor = color;
                } else {
                    if (STORAGE_ALERT && usagePercent >= STORAGE_ALERT_THRESHOLD_PERCENT) {
                        driveCard.style.backgroundColor = STORAGE_ALERT_COLOR;
                    } else {
                        driveCard.style.backgroundColor = ""; 
                    }
                }

                driveCard.innerHTML = `
                    <div class="stat-label">${label}</div>
                    <div class="stat-value">
                        ${usagePercent}% 
                        <div class="stat-subvalue">(${usedValue.toFixed(2)} / ${totalValue.toFixed(2)} ${unit})</div>
                    </div>
                `;
                drivesContainer.appendChild(driveCard);
            });
        }

        pushData(cpuChart, cpuUtilization);
        pushData(ramChart, ramUsagePercent);
    });

    socket.on("config_updated", (data) => {
        console.log("Polling interval updated on server:", data.interval);
    });

    // Added event listener here to keep logic encapsulated
    pollingSlider.addEventListener("input", updatePolling);
}

/* ------------------ SLIDER (DEBOUNCED) ------------------ */
function updatePolling() {
    const newInterval = parseInt(pollingSlider.value);
    
    // Immediate UI feedback
    pollingLabel.innerText = newInterval + " ms";

    // Debounce: Wait 300ms before hitting the network/cookie
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        setPollingCookie(newInterval);
        if (socket) {
            socket.emit("set_config", { interval: newInterval });
        }
    }, 300);
}

/* ------------------ INIT ------------------ */
window.addEventListener("load", () => {
    cpuChart = createChart("cpuChart", "#3b82f6");
    ramChart = createChart("ramChart", "#22c55e");
    initSocket();
});

// Helper to interpolate two hex colors
function interpolateColor(color1, color2, factor) {
    const c1 = parseInt(color1.slice(1), 16);
    const c2 = parseInt(color2.slice(1), 16);

    const r1 = (c1 >> 16) & 0xff;
    const g1 = (c1 >> 8) & 0xff;
    const b1 = c1 & 0xff;

    const r2 = (c2 >> 16) & 0xff;
    const g2 = (c2 >> 8) & 0xff;
    const b2 = c2 & 0xff;

    const r = Math.round(r1 + factor * (r2 - r1));
    const g = Math.round(g1 + factor * (g2 - g1));
    const b = Math.round(b1 + factor * (b2 - b1));

    return `rgb(${r},${g},${b})`;
}