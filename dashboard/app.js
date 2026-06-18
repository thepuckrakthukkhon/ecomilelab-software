const telemetryPath = "/test-data/latest_telemetry.json";

const fields = {
  speed: document.getElementById("speed"),
  batteryPercent: document.getElementById("batteryPercent"),
  batteryVoltage: document.getElementById("batteryVoltage"),
  current: document.getElementById("current"),
  power: document.getElementById("power"),
  motorTemp: document.getElementById("motorTemp"),
  controllerTemp: document.getElementById("controllerTemp"),
  status: document.getElementById("status"),
  timestamp: document.getElementById("timestamp"),
  connection: document.getElementById("connection"),
  message: document.getElementById("message"),
};

function showValue(id, value) {
  fields[id].textContent = Number.isFinite(value) ? value.toFixed(2) : "--";
}

function setStatusColor(status) {
  fields.status.className = "status-value";

  const warningStatuses = new Set([
    "LOW_BATTERY",
    "TEMP_WARM",
    "TEMP_HOT",
    "RESTART_READY",
  ]);

  if (status === "NORMAL") {
    fields.status.classList.add("status-normal");
    return;
  }

  if (warningStatuses.has(status)) {
    fields.status.classList.add("status-warning");
    return;
  }

  fields.status.classList.add("status-danger");
}

async function loadTelemetry() {
  try {
    const response = await fetch(`${telemetryPath}?time=${Date.now()}`, {
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error("Telemetry file is not available");
    }

    const data = await response.json();

    if (!data) {
      throw new Error("Telemetry file is empty");
    }

    showValue("speed", data.speed);
    showValue("batteryPercent", data.batteryPercent);
    showValue("batteryVoltage", data.batteryVoltage);
    showValue("current", data.current);
    showValue("power", data.power);
    showValue("motorTemp", data.motorTemp);
    showValue("controllerTemp", data.controllerTemp);

    fields.status.textContent = data.status || "--";
    fields.timestamp.textContent = `Last update: ${data.timestamp || "--"}`;
    fields.connection.textContent = "Live";
    fields.connection.className = "connection live";
    fields.message.textContent = "Reading live data from latest_telemetry.json";

    setStatusColor(data.status);
  } catch (error) {
    fields.connection.textContent = "No data";
    fields.connection.className = "connection error";
    fields.message.textContent = `Cannot read telemetry: ${error.message}`;
  }
}

loadTelemetry();
setInterval(loadTelemetry, 1000);
