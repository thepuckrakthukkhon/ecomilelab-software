const MODES = new Set(["normal", "overheat", "low_battery", "sensor_error"]);

const mode = process.argv[2] || "normal";
const session = process.argv[3] || "test_001";
const countFlagIndex = process.argv.indexOf("--count");
const maxPackets =
  countFlagIndex === -1 ? null : Number(process.argv[countFlagIndex + 1]);
let sentPackets = 0;
const isImported = typeof module !== "undefined" && module.parent;

if (!MODES.has(mode)) {
  console.error(`Unknown mode: ${mode}`);
  console.error(`Available modes: ${Array.from(MODES).join(", ")}`);
  process.exit(1);
}

if (maxPackets !== null && (!Number.isInteger(maxPackets) || maxPackets <= 0)) {
  console.error("Invalid --count value. Example: --count 5");
  process.exit(1);
}

function randomFloat(min, max, decimals = 2) {
  return Number((min + Math.random() * (max - min)).toFixed(decimals));
}

function randomInt(min, max) {
  return Math.floor(min + Math.random() * (max - min + 1));
}

function buildDataForMode(selectedMode) {
  if (selectedMode === "overheat") {
    return {
      current_A: randomFloat(8, 18),
      temp_C: randomFloat(70, 90),
      speed_rpm: randomInt(900, 3000),
      battery_V: randomFloat(45, 49),
    };
  }

  if (selectedMode === "low_battery") {
    return {
      current_A: randomFloat(3, 12),
      temp_C: randomFloat(32, 55),
      speed_rpm: randomInt(500, 2500),
      battery_V: randomFloat(38, 42),
    };
  }

  if (selectedMode === "sensor_error") {
    return {
      current_A: null,
      temp_C: randomFloat(35, 50),
      speed_rpm: 0,
      battery_V: randomFloat(46, 49),
    };
  }

  return {
    current_A: randomFloat(3, 15),
    temp_C: randomFloat(30, 55),
    speed_rpm: randomInt(500, 3500),
    battery_V: randomFloat(45, 50),
  };
}

function getStatus(selectedMode, data) {
  if (selectedMode === "sensor_error") return "err";
  if (data.temp_C >= 75) return "err";
  if (data.temp_C >= 60) return "warn";
  if (data.battery_V <= 42) return "warn";
  return "ok";
}

function generatePacket() {
  const data = buildDataForMode(mode);

  return {
    device_id: "esp32_01",
    timestamp: Date.now(),
    session,
    data,
    status: getStatus(mode, data),
  };
}

function generateTelemetryPacket(options = {}) {
  const selectedMode = options.mode || "normal";
  const selectedSession = options.session || "test_001";

  if (!MODES.has(selectedMode)) {
    throw new Error(`Unknown mode: ${selectedMode}`);
  }

  const data = buildDataForMode(selectedMode);

  return {
    device_id: options.deviceId || "esp32_01",
    timestamp: Date.now(),
    session: selectedSession,
    data,
    status: getStatus(selectedMode, data),
  };
}

if (isImported) {
  module.exports = {
    MODES,
    generateTelemetryPacket,
  };
} else {
  console.log(`Mock Data Generator started`);
  console.log(`Mode: ${mode}`);
  console.log(`Session: ${session}`);
  console.log(`Output interval: 1 second`);
  if (maxPackets !== null) console.log(`Packet count: ${maxPackets}`);
  console.log("");

  setInterval(() => {
    console.log(JSON.stringify(generatePacket()));
    sentPackets += 1;

    if (maxPackets !== null && sentPackets >= maxPackets) {
      process.exit(0);
    }
  }, 1000);
}
