(() => {
  const input = document.getElementById('selected-date');
  const label = document.getElementById('day-label');
  const availability = document.getElementById('availability');
  const fmt = new Intl.DateTimeFormat('en-US', { weekday: 'long', month: 'long', day: 'numeric', timeZone: 'UTC' });
  function render() {
    const [y, m, d] = input.value.split('-').map(Number);
    if (!y || !m || !d) return;
    const date = new Date(Date.UTC(y, m - 1, d));
    label.textContent = fmt.format(date).toUpperCase();
    availability.textContent = 'NOT ENOUGH VERIFIED DATA';
  }
  function shift(amount) {
    const date = new Date(`${input.value}T12:00:00Z`);
    date.setUTCDate(date.getUTCDate() + amount);
    input.value = date.toISOString().slice(0, 10);
    render();
  }
  input.addEventListener('change', render);
  document.getElementById('prev').addEventListener('click', () => shift(-1));
  document.getElementById('next').addEventListener('click', () => shift(1));
  document.getElementById('today').addEventListener('click', () => {
    const now = new Date();
    input.value = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate())).toISOString().slice(0, 10);
    render();
  });
  render();
})();
