fetch('vault-data.json')
  .then((res) => res.json())
  .then((data) => {
    renderPortfolio(data.stablecoin, 'stablecoin-assets', 'stablecoin-total', 'stablecoin-gain-loss');
    renderPortfolio(data.Heaven, 'heaven-assets', 'heaven-total', 'heaven-gain-loss');
  })
  .catch((err) => console.error('Error loading JSON:', err));

function renderPortfolio(portfolio, assetsId, totalId, gainLossId) {
  const assetsContainer = document.getElementById(assetsId);
  let currentValue = 0;

  for (const [asset, value] of Object.entries(portfolio.allocations)) {
    const div = document.createElement('div');
    div.className = 'asset';
    div.innerHTML = `
      <span>${asset.toUpperCase()}</span>
      <span>£${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
    `;
    assetsContainer.appendChild(div);
    currentValue += value;
  }

  const totalEl = document.getElementById(totalId);
  totalEl.textContent = `Current Value: £${currentValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;

  const gainLossEl = document.getElementById(gainLossId);
  const initial = portfolio.initial;
  const diff = currentValue - initial;
  const percent = ((diff / initial) * 100).toFixed(2);

  const status = diff >= 0 ? 'Gain' : 'Loss';
  const color = diff >= 0 ? '#4ade80' : '#f87171';
  gainLossEl.innerHTML = `<span style="color: ${color}">${status}: £${Math.abs(diff).toLocaleString(undefined, { minimumFractionDigits: 2 })} (${percent}%)</span>`;
}
