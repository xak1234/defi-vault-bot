let lastData = null;

async function fetchData() {
  try {
    const res = await fetch('vault-data.json');
    const data = await res.json();

    if (!data?.stablecoin?.allocations || !data?.Heaven?.allocations) {
      console.warn("Skipping update — malformed data");
      return;
    }

    lastData = data;
    renderVault(data);
    renderChart(generateMockChartData());
  } catch (e) {
    console.error("Fetch failed:", e);
    if (lastData) {
      console.log("Rendering last known good data");
      renderVault(lastData);
      renderChart(generateMockChartData());
    }
  }
}

function renderVault(data) {
  document.getElementById("timestamp").textContent = `Last Updated: ${new Date().toUTCString()}`;

  renderSection("stable", data.stablecoin);
  renderSection("heaven", data.Heaven);
}

function renderSection(idPrefix, portfolio) {
  const tokens = portfolio.allocations;
  const container = document.getElementById(`${idPrefix}-tokens`);
  container.innerHTML = '';
  let total = 0;

  for (const [token, value] of Object.entries(tokens)) {
    const row = document.createElement("div");
    row.className = "token-row";
    row.innerHTML = `<div>${token.toUpperCase()}</div><div>Value: £${value.toFixed(2)}</div>`;
    container.appendChild(row);
    total += value;
  }

  document.getElementById(`${idPrefix}-total`).textContent = `Total Value: £${total.toFixed(2)}`;
  const gain = total - portfolio.initial;
  const percent = ((gain / portfolio.initial) * 100).toFixed(2);
  const gainStr = `${gain >= 0 ? '+' : '-'}£${Math.abs(gain).toFixed(2)} (${percent}%)`;
  updateGain(`${idPrefix}-gain`, gainStr);
}

function updateGain(id, gainStr) {
  const gainEl = document.getElementById(id);
  gainEl.textContent = `Gain: ${gainStr}`;
  const gain = parseFloat(gainStr);
  gainEl.className = 'gain ' + (gain > 0 ? 'positive' : 'negative');
}

function generateMockChartData() {
  const now = Date.now();
  const points = [];
  for (let i = 0; i < 6; i++) {
    const base = 1800 + Math.random() * 200;
    const high = base + Math.random() * 20;
    const low = base - Math.random() * 20;
    const open = base + Math.random() * 10;
    const close = base - Math.random() * 10;
    points.push({
      x: new Date(now - (5 - i) * 3600000),
      o: open,
      h: high,
      l: low,
      c: close
    });
  }
  return points;
}

function renderChart(chartData) {
  const ctx = document.getElementById("candleChart").getContext("2d");
  if (window.chartInstance) {
    window.chartInstance.destroy();
  }
  window.chartInstance = new Chart(ctx, {
    type: 'candlestick',
    data: {
      datasets: [{
        label: 'ETH Price (Mock)',
        data: chartData,
        borderColor: '#38bdf8'
      }]
    },
    options: {
      responsive: true,
      scales: {
        x: {
          type: 'time',
          time: {
            unit: 'hour'
          }
        }
      }
    }
  });
}

fetchData();
setInterval(fetchData, 30000);
