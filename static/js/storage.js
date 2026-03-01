let socket;
const drivesContainer = document.getElementById("drivesContainer");
const pollingSlider = document.getElementById("pollingSlider");
const pollingLabel = document.getElementById("pollingValue");

const driveCharts = {}; 
const MAX_POINTS = 20;

function getFSColorSet(fsType) {
    return FS_THEME[fsType] || FS_THEME["DEFAULT"];
}

/* ------------------ COOKIE HELPERS ------------------ */
function getPollingFromCookie() {
    const match = document.cookie.match(/pollingRate=(\d+)/);
    return match ? parseInt(match[1]) : null;
}

function setPollingCookie(value) {
    document.cookie = `pollingRate=${value}; path=/; max-age=31536000`;
}

/* ------------------ CHART LOGIC ------------------ */
function createGradient(ctx, color) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 60);
    gradient.addColorStop(0, color + "66");
    gradient.addColorStop(1, color + "00");
    return gradient;
}

function createDriveChart(canvasId, readColor, writeColor) {
    const ctx = document.getElementById(canvasId).getContext("2d");
    return new Chart(ctx, {
        type: "line",
        data: {
            labels: new Array(MAX_POINTS).fill(""),
            datasets: [
                {
                    label: "Read",
                    data: new Array(MAX_POINTS).fill(0),
                    borderColor: readColor,
                    backgroundColor: createGradient(ctx, readColor),
                    borderWidth: 1.5,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                },
                {
                    label: "Write",
                    data: new Array(MAX_POINTS).fill(0),
                    borderColor: writeColor,
                    backgroundColor: createGradient(ctx, writeColor),
                    borderWidth: 1.5,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                }
            ]
        },
        options: {
            animation: false,
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { display: false },
                y: {
                    beginAtZero: true,
                    ticks: { display: true, font: { size: 9 }, callback: (v) => v === 0 ? "0" : v.toFixed(1) },
                    grid: { color: "rgba(255, 255, 255, 0.05)" }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: { 
                    mode: 'index', 
                    intersect: false,
                    callbacks: {
                        label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)} MB/s`
                    }
                }
            }
        }
    });
}

function formatBytes(bytes) {
    if (bytes >= 1024 ** 3) return (bytes / 1024 ** 3).toFixed(2) + " GB";
    if (bytes >= 1024 ** 2) return (bytes / 1024 ** 2).toFixed(2) + " MB";
    if (bytes >= 1024) return (bytes / 1024).toFixed(2) + " KB";
    return bytes + " B";
}

function updateDrives(storage) {
    storage.forEach(drive => {
        const cleanId = drive.device.replace(/[^\w]/g, '');
        const driveId = `drive-${cleanId}`;
        let card = document.getElementById(driveId);

        const readMBps = drive.read_speed_Bps / (1024 * 1024);
        const writeMBps = drive.write_speed_Bps / (1024 * 1024);

        // Get Dynamic Color Set
        const colors = getFSColorSet(drive.fstype);

        if (!card) {
            card = document.createElement("div");
            card.className = "card storage-card";
            card.id = driveId;

            card.innerHTML = `
                <div class="left-zone">
                    <div class="drive-header">
                        <span class="drive-label">${drive.mount}</span>
                        <span class="fs-badge" style="border: 1px solid ${colors.write}44; color: ${colors.write}">${drive.fstype}</span>
                    </div>
                    <div class="usage-bar-container">
                        <div class="usage-bar"><div class="usage-fill"></div></div>
                    </div>
                    <div class="usage-text"></div>
                </div>
                <div class="right-zone">
                    <div class="io-labels">
                        <span style="color: ${colors.read}" class="read-label"></span>
                        <span style="color: ${colors.write}" class="write-label"></span>
                    </div>
                    <canvas id="chart-${cleanId}"></canvas>
                </div>
            `;
            drivesContainer.appendChild(card);
            
            // Apply both dynamic Read and Write colors
            driveCharts[cleanId] = createDriveChart(`chart-${cleanId}`, colors.read, colors.write);
        }

        // Update Values
        card.querySelector(".usage-fill").style.width = drive.usage_percent + "%";
        card.querySelector(".usage-text").innerText = 
            `${formatBytes(drive.used_mb * 1024 * 1024)} / ${formatBytes(drive.total_mb * 1024 * 1024)} (${drive.usage_percent.toFixed(1)}%)`;
        
        card.querySelector(".read-label").innerText = `R: ${readMBps.toFixed(2)} MB/s`;
        card.querySelector(".write-label").innerText = `W: ${writeMBps.toFixed(2)} MB/s`;

        // Update Chart
        const chart = driveCharts[cleanId];
        chart.data.datasets[0].data.shift();
        chart.data.datasets[0].data.push(readMBps);
        chart.data.datasets[1].data.shift();
        chart.data.datasets[1].data.push(writeMBps);
        chart.update();
    });
}

/* ------------------ POLLING CONTROL ------------------ */
let debounceTimer;
function updatePolling() {
    const newInterval = parseInt(pollingSlider.value);
    pollingLabel.innerText = newInterval + " ms";
    
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        setPollingCookie(newInterval);
        if (socket) {
            socket.emit("set_config", { interval: newInterval });
        }
    }, 300);
}

/* ------------------ SOCKET INIT ------------------ */
function initSocket() {
    socket = io();
    const initialInterval = getPollingFromCookie() || DEFAULT_POLLING;
    pollingSlider.value = initialInterval;
    pollingLabel.innerText = initialInterval + " ms";
    socket.emit("set_config", { interval: initialInterval });

    socket.on("stats_update", (data) => {
        if (data.storage) updateDrives(data.storage);
    });

    pollingSlider.addEventListener("input", updatePolling);
}

window.addEventListener("load", initSocket);