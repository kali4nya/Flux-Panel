let socket;
const drivesContainer = document.getElementById("drivesContainer");

const driveCharts = {}; // Chart.js instances for right I/O graphs
const driveData = {};   // Historical I/O data
const MAX_POINTS = 20;

// Gradient helper
function createGradient(ctx, color) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 60);
    gradient.addColorStop(0, color + "88");
    gradient.addColorStop(0.4, color + "44");
    gradient.addColorStop(1, color + "00");
    return gradient;
}

// Create Chart.js line chart
function createDriveChart(canvasId, lineColor) {
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
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) + " MB/s";
                        }
                    },
                    grid: { color: "#1f232b" }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    enabled: true,
                    displayColors: false,
                    callbacks: {
                        title: () => "",
                        label: ctx => `${ctx.parsed.y.toFixed(2)} MB/s`
                    }
                }
            }
        }
    });
}

// Convert bytes to human-readable string
function formatBytes(bytes) {
    if (bytes >= 1024 ** 3) return (bytes / 1024 ** 3).toFixed(2) + " GB";
    if (bytes >= 1024 ** 2) return (bytes / 1024 ** 2).toFixed(2) + " MB";
    if (bytes >= 1024) return (bytes / 1024).toFixed(2) + " KB";
    return bytes + " B";
}

// Push new value to Chart.js
function pushData(chart, value) {
    chart.data.datasets[0].data.shift();
    chart.data.datasets[0].data.push(value);
    chart.update();
}

// ------------------ UPDATE DRIVES ------------------
function updateDrives(storage) {
    storage.forEach(drive => {
        const driveId = `drive-${drive.device.replace(/[\W]/g,'')}`;
        let card = document.getElementById(driveId);

        // Raw MB/s for chart
        const ioValue = (drive.read_speed_Bps + drive.write_speed_Bps) / (1024 * 1024);

        if (!card) {
            // Create card
            card = document.createElement("div");
            card.className = "card storage-card";
            card.id = driveId;

            card.innerHTML = `
                <div class="left-zone">
                    <div class="drive-label">${drive.mount}</div>
                    <div class="usage-bar-container">
                        <div class="usage-bar">
                            <div class="usage-fill"></div>
                        </div>
                    </div>
                    <div class="usage-text"></div>
                </div>
                <div class="right-zone">
                    <canvas id="chart-${drive.device.replace(/[\W]/g,'')}"></canvas>
                </div>
            `;
            drivesContainer.appendChild(card);

            // Initialize right I/O chart
            const canvasId = `chart-${drive.device.replace(/[\W]/g,'')}`;
            driveCharts[drive.device] = createDriveChart(canvasId, "#facc15"); // yellow
            driveData[drive.device] = Array(MAX_POINTS).fill(ioValue);
        }

        // Update left usage bar & text
        const fill = card.querySelector(".usage-fill");
        fill.style.width = drive.usage_percent + "%";

        const text = card.querySelector(".usage-text");
        text.innerText = `${formatBytes(drive.used_mb * 1024*1024)} / ${formatBytes(drive.total_mb * 1024*1024)} (${drive.usage_percent.toFixed(1)}%)`;

        // Update right chart
        driveData[drive.device].push(ioValue);
        if (driveData[drive.device].length > MAX_POINTS) driveData[drive.device].shift();
        pushData(driveCharts[drive.device], ioValue);
    });
}

// ------------------ SOCKET.IO ------------------
function initSocket() {
    socket = io();

    socket.on("stats_update", (data) => {
        if (Array.isArray(data.storage)) {
            updateDrives(data.storage);
        }
    });
}

// ------------------ INIT ------------------
window.addEventListener("load", () => {
    initSocket();
});