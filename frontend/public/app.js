const API_BASE = window.localStorage.getItem('API_BASE') || `http://${window.location.hostname}:8000`;
const form = document.getElementById('server-form');
const listEl = document.getElementById('server-list');
const statusEl = document.getElementById('status');
const reloadBtn = document.getElementById('reload-btn');

const setStatus = (msg, isError = false) => {
  statusEl.style.color = isError ? '#d7263d' : '#1f6feb';
  statusEl.textContent = msg;
};

async function loadServers() {
  listEl.innerHTML = '';
  try {
    const res = await fetch(`${API_BASE}/servers`);
    const servers = await res.json();

    servers.forEach((s) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${s.id}</td>
        <td>${s.name}</td>
        <td>${s.ip}:${s.port}</td>
        <td>${s.username}</td>
        <td>${s.cpu_cores}</td>
        <td>${s.ram_gb} GB</td>
        <td>${s.environment}</td>
        <td>${s.note || ''}</td>
        <td><button class="delete-btn" data-id="${s.id}">Xóa</button></td>
      `;
      listEl.appendChild(row);
    });

    setStatus(`Đã tải ${servers.length} server.`);
  } catch (err) {
    setStatus('Không thể tải dữ liệu từ API backend.', true);
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(form).entries());
  data.port = Number(data.port);
  data.cpu_cores = Number(data.cpu_cores);
  data.ram_gb = Number(data.ram_gb);

  try {
    const res = await fetch(`${API_BASE}/servers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!res.ok) throw new Error('Failed');

    form.reset();
    setStatus('Thêm server thành công.');
    await loadServers();
  } catch {
    setStatus('Thêm server thất bại.', true);
  }
});

listEl.addEventListener('click', async (e) => {
  if (!e.target.classList.contains('delete-btn')) return;
  const id = e.target.dataset.id;
  try {
    const res = await fetch(`${API_BASE}/servers/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed');
    setStatus(`Đã xóa server #${id}.`);
    await loadServers();
  } catch {
    setStatus('Xóa server thất bại.', true);
  }
});

reloadBtn.addEventListener('click', loadServers);
loadServers();
