const MAX_POINTS = 15;

let socket;
let slider = document.getElementById("pollingSlider");
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
            interaction: {
                mode: "nearest",
                intersect: false
            },
            scales: {
                x: { display: false },
                y: {
                    min: 0,
                    max: 100,
                    ticks: { stepSize: 20 },
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
    socket = io(); // Connect to the server

    // Send initial polling interval from cookie
    const interval = getPollingFromCookie();
    socket.emit("set_config", { interval });

    // Update slider display
    slider.value = interval;
    pollingLabel.innerText = interval + " ms";

    // Listen for stats updates
    socket.on("stats_update", (data) => {
        const cpuUsage = data.cpu?.usage_percent ?? 0;
        const ramUsage = data.ram?.usage_percent ?? 0;

        document.getElementById("cpuValue").innerText = cpuUsage + "%";
        document.getElementById("ramValue").innerText = ramUsage + "%";

        document.getElementById("gpuValue").innerText =
            data.gpu?.temperature_c != null
                ? data.gpu.temperature_c + "°C"
                : "--°C";

        if (Array.isArray(data.storage) && data.storage.length > 0) {
            document.getElementById("storageValue").innerText =
                (data.storage[0].usage_percent ?? 0) + "%";
        }

        pushData(cpuChart, cpuUsage);
        pushData(ramChart, ramUsage);
    });

    // Optional: Listen for confirmation from server
    socket.on("config_updated", (data) => {
        console.log("Polling interval updated on server:", data.interval);
    });
}

/* ------------------ SLIDER ------------------ */

function updatePolling() {
    const newInterval = parseInt(slider.value);
    pollingLabel.innerText = newInterval + " ms";
    setPollingCookie(newInterval);

    if (socket) {
        socket.emit("set_config", { interval: newInterval });
    }
}

slider.addEventListener("input", updatePolling);

/* ------------------ INIT ------------------ */

initSocket();