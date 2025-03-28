fetch('vault-data.json')
  .then((res) => res.json())
  .then((data) => {
    renderPortfolio(data.stablecoin, 'stablecoin-assets');
    renderPortfolio(data.Heaven, 'heaven-assets');
  })
  .catch((err) => console.error('Error loading JSON:', err));

function renderPortfolio(portfolio, elementId) {
  const container = document.getElementById(elementId);
  for (const [asset, value] of Object.entries(portfolio.allocations)) {
    const div = document.createElement('div');
    div.className = 'asset';
    div.innerHTML = `
      <span>${asset.toUpperCase()}</span>
      <span>£${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
    `;
    container.appendChild(div);
  }
}
