const API_BASE = "";
const MAX_POINTS = 15;

let pollingInterval = 1000;
let pollingTimer;

function createGradient(ctx, color) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 250);
    gradient.addColorStop(0, color + "55");
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
                x: {
                    display: false,
                    grid: { display: false }
                },
                y: {
                    min: 0,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        color: "#6b7280"
                    },
                    grid: {
                        color: "#1f232b"
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    enabled: true,
                    backgroundColor: "#111418",
                    borderColor: "#1f232b",
                    borderWidth: 1,
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

async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/api/stats`);
        const data = await res.json();

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

    } catch (err) {
        console.error("Failed to fetch stats:", err);
    }
}

function startPolling() {
    clearInterval(pollingTimer);
    pollingTimer = setInterval(fetchStats, pollingInterval);
}

const slider = document.getElementById("pollingSlider");
const pollingLabel = document.getElementById("pollingValue");

function updatePolling() {
    // Invert value so right = faster
    const max = parseInt(slider.max);
    const min = parseInt(slider.min);

    const inverted = max - slider.value + min;

    pollingInterval = inverted;
    pollingLabel.innerText = inverted + " ms";

    startPolling();
}

slider.addEventListener("input", updatePolling);

// Initialize correctly on load
updatePolling();

startPolling();
fetchStats();