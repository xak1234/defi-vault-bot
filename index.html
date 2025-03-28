<!DOCTYPE html>
<html>
<head>
  <title>Daddy's DeFi Vault</title>
  <meta charset="UTF-8">
  <style>
    body {
      background-color: #111;
      color: #0f0;
      font-family: monospace;
      padding: 20px;
    }
    .section {
      margin-bottom: 2rem;
    }
    .title {
      font-size: 1.5rem;
      font-weight: bold;
      margin-bottom: 0.5rem;
    }
    .gain-positive {
      color: #0f0;
    }
    .gain-negative {
      color: #f00;
    }
  </style>
  <script>
    async function loadData() {
      try {
        const res = await fetch('http://localhost:8000');
        const data = await res.json();
        const out = document.getElementById('output');
        out.innerHTML = "";

        const formatMoney = v => `£${parseFloat(v).toFixed(2)}`;

        for (const [vaultName, vault] of Object.entries(data)) {
          if (vaultName === "timestamp") continue;

          const gainClass = vault.gain_amount >= 0 ? "gain-positive" : "gain-negative";

          const section = document.createElement("div");
          section.className = "section";
          section.innerHTML = `
            <div class="title">💼 ${vaultName} Portfolio</div>
            Initial Investment: ${vault.initial_investment}<br>
            Current Value: ${vault.current_value}<br>
            <span class="${gainClass}">
              Gain/Loss: ${vault.gain_amount >= 0 ? "+" : ""}${formatMoney(vault.gain_amount)} (${vault.gain_percent}%)
            </span>
            <br><br>
            Token Prices:<br>
            <ul>
              ${Object.entries(vault.tokens).map(([symbol, info]) =>
                `<li>${symbol.toUpperCase()}: £${info.price.toFixed(4)}</li>`).join('')}
            </ul>
          `;
          out.appendChild(section);
        }

        document.getElementById("timestamp").textContent = `📅 Last updated: ${data.timestamp}`;

      } catch (e) {
        document.getElementById("output").innerHTML = "❌ Failed to load data.";
        console.error(e);
      }
    }

    setInterval(loadData, 60000); // Refresh every 60 seconds
    window.onload = loadData;
  </script>
</head>
<body>
  <h1>🧠 Daddy's Live DeFi Vault</h1>
  <div id="timestamp">📅 Loading...</div>
  <div id="output">Fetching data...</div>
</body>
</html>
