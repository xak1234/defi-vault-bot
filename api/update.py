<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>DeFi Vault Tracker</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 2em; background: #0b0c10; color: #f0f0f0; }
    .vault { margin-bottom: 2em; border-bottom: 1px solid #333; padding-bottom: 1em; }
    .token-row { display: flex; justify-content: space-between; padding: 0.3em 0; }
    .gain { font-weight: bold; }
    .gain.positive { color: #4aff81; }
    .gain.negative { color: #ff4e4e; }
  </style>
</head>
<body>

  <h1>📊 DeFi Vault Tracker</h1>
  <div id="timestamp"></div>

  <div class="vault">
    <h2>stablecoin Portfolio</h2>
    <div id="stable-total"></div>
    <div id="stable-gain" class="gain"></div>
    <div id="stable-tokens"></div>
  </div>

  <div class="vault">
    <h2>heaven's Vault Portfolio</h2>
    <div id="heaven-total"></div>
    <div id="heaven-gain" class="gain"></div>
    <div id="heaven-tokens"></div>
  </div>

  <script>
    let lastData = null;

    async function fetchData() {
      try {
        const res = await fetch('/api/update');
        const data = await res.json();

        if (!data?.stablecoin?.tokens || !data?.heaven?.tokens) {
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

      document.getElementById("heaven-total").textContent = `Total Value: ${data.heaven.total}`;
      updateGain("heaven-gain", data.heaven.gain);
      renderTokens("heaven-tokens", data.heaven.tokens);
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
  </script>

</body>
</html>
