const API_BASE = "http://192.168.31.106:5000"; 
// If same origin, use: const API_BASE = "";

const cpuCtx = document.getElementById("cpuChart");
const ramCtx = document.getElementById("ramChart");

const cpuChart = new Chart(cpuCtx, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            data: [],
            borderColor: "#9ca3af",
            borderWidth: 2,
            tension: 0.4,
            pointRadius: 0
        }]
    },
    options: {
        animation: false,
        scales: {
            y: { min: 0, max: 100 }
        },
        plugins: { legend: { display: false } }
    }
});

const ramChart = new Chart(ramCtx, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            data: [],
            borderColor: "#6b7280",
            borderWidth: 2,
            tension: 0.4,
            pointRadius: 0
        }]
    },
    options: {
        animation: false,
        scales: {
            y: { min: 0, max: 100 }
        },
        plugins: { legend: { display: false } }
    }
});

async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/api/stats`);
        const data = await res.json();

        document.getElementById("cpuValue").innerText =
            data.cpu.usage_percent + "%";

        document.getElementById("ramValue").innerText =
            data.ram.usage_percent + "%";

        document.getElementById("gpuValue").innerText =
            data.gpu.temperature_c
                ? data.gpu.temperature_c + "°C"
                : "--°C";

        if (data.storage.length > 0) {
            document.getElementById("storageValue").innerText =
                data.storage[0].usage_percent + "%";
        }

        const time = new Date().toLocaleTimeString();

        if (cpuChart.data.labels.length > 30) {
            cpuChart.data.labels.shift();
            cpuChart.data.datasets[0].data.shift();
            ramChart.data.labels.shift();
            ramChart.data.datasets[0].data.shift();
        }

        cpuChart.data.labels.push(time);
        cpuChart.data.datasets[0].data.push(data.cpu.usage_percent);

        ramChart.data.labels.push(time);
        ramChart.data.datasets[0].data.push(data.ram.usage_percent);

        cpuChart.update();
        ramChart.update();

    } catch (err) {
        console.error("Failed to fetch stats:", err);
    }
}

setInterval(fetchStats, 1000);
fetchStats();