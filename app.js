let lastData = null;

async function fetchData() {
  try {
    const res = await fetch('/api/update');
    const data = await state.json();

    if (!data?.stablecoin?.tokens || !data?.Heaven?.tokens) {
      console.warn("Skipping update — malformed data");
      return;
    }

    lastData = data; // update backup
    renderVault(data);
  } catch (e) {
    console.error("Fetch failed:", e);
    if (lastData) {
      console.log("Rendering last known good data");
      renderVault(lastData);
    }
  }
}

function renderVault(data) {
  document.getElementById("timestamp").textContent = `Last Updated: ${data.timestamp} UTC`;

  document.getElementById("stable-total").textContent = `Total Value: ${data.stablecoin.total}`;
  updateGain("stable-gain", data.stablecoin.gain);
  renderTokens("stable-tokens", data.stablecoin.tokens);

  document.getElementById("heaven-total").textContent = `Total Value: ${data.Heaven.total}`;
  updateGain("heaven-gain", data.Heaven.gain);
  renderTokens("heaven-tokens", data.Heaven.tokens);
}

function updateGain(id, gainStr) {
  const gainEl = document.getElementById(id);
  gainEl.textContent = `Gain: ${gainStr}`;
  const gain = parseFloat(gainStr);
  gainEl.className = 'gain ' + (gain > 0 ? 'positive' : 'negative');
}

function renderTokens(containerId, tokens) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';
  for (const [token, { price, value }] of Object.entries(tokens)) {
    const row = document.createElement("div");
    row.className = "token-row";
    row.innerHTML = `<div>${token.toUpperCase()}</div><div>£${price.toFixed(4)} | Value: £${value.toFixed(2)}</div>`;
    container.appendChild(row);
  }
}

fetchData();
setInterval(fetchData, 5000);
