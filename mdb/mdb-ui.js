let db = null;
const BASE_URL = window.location.origin;

// TAB NAVIGATION
function showPage(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(pageId).classList.add('active');
  document.querySelector(`.tab[onclick="showPage('${pageId}')"]`).classList.add('active');
}

// INIT DATABASE
async function initApp() {
  try {
    const SQL = await initSqlJs({
      locateFile: f => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/${f}`
    });
    const resp = await fetch('mdb.sqlite');
    const buf = await resp.arrayBuffer();
    db = new SQL.Database(new Uint8Array(buf));

    statusEl("✓ Database loaded");
    populateDropdown("container", "containerSelect", "?");
  } catch (e) {
    statusEl("❌ Error: " + e.message);
  }
}

function statusEl(msg) { document.getElementById('status').textContent = msg; }

// DROPDOWN LOGIC
function populateDropdown(col, elementId, label, filterCol = null, filterVal = null) {
  let sql = `SELECT DISTINCT ${col} FROM machines WHERE ${col} IS NOT NULL`;
  if (filterCol) sql += ` AND ${filterCol} = ${isNaN(filterVal) ? `'${filterVal}'` : filterVal}`;
  sql += ` ORDER BY ${col} ASC`;

  const el = document.getElementById(elementId);
  try {
    const res = db.exec(sql);
    el.innerHTML = `<option value="">${label}</option>`;
    if (res.length) {
      res[0].values.forEach(v => {
	el.innerHTML += `<option value="${v[0]}">${v[0]}</option>`;
      });
    }
  } catch (e) { console.error(e); }
}

function onContainerChange() {
  const val = document.getElementById('containerSelect').value;
  const sideEl = document.getElementById('sideSelect');
  if (val) {
    populateDropdown("side", "sideSelect", "?", "container", val);
    sideEl.disabled = false;
  } else {
    // disable side until container is selected
    sideEl.innerHTML = "<option>?</option>";
    sideEl.disabled = true;
  }
  document.getElementById('rack-visual').innerHTML = "";
}

// RACK VISUALIZER
function renderRack() {
  const container = document.getElementById('containerSelect').value;
  const side = document.getElementById('sideSelect').value;
  const mode = document.getElementById('viewMode').value;
  const visual = document.getElementById('rack-visual');

  if (!container || !side) return;

  const sql = `SELECT ip_address, mac_address, worker, shelf, position
			 FROM machines WHERE container = ${container} AND side = '${side}'
			 ORDER BY shelf ASC, position ASC`;
  const res = db.exec(sql);
  visual.innerHTML = "";

  if (!res.length) {
    visual.innerHTML = "<div style='color:white;padding:20px'>No records found.</div>";
    return;
  }

  const data = {};
  res[0].values.forEach(row => {
    const [ip, mac, wrk, shelf, pos] = row;
    if (!data[shelf]) data[shelf] = [];
    const label = mode === 'ip_address' ? ip : (mode === 'mac_address' ? mac : wrk);
    data[shelf].push({ ip, label, pos });
  });

  Object.keys(data).sort((a,b) => a-b).forEach(shelfNum => {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'shelf-row';
    rowDiv.innerHTML = `<div class="shelf-label">S${shelfNum}</div>`;

    data[shelfNum].forEach(m => {
      rowDiv.innerHTML += `
			<div class="machine-box" data-ip="${m.ip}" title="Not synced">
			    <a href="http://${m.ip}">
			      <span class="display-val">${m.label || '---'}</span>
			    </a>
			    <span class="pos-sub">P${m.pos}</span>
			</div>`;
    });
    visual.appendChild(rowDiv);
  });
}

// GLOBAL SEARCH
function executeSearch() {
  const term = document.getElementById('searchInput').value.trim();
  const resultsBody = document.getElementById('searchResults');
  if (term.length < 2) { resultsBody.innerHTML = ""; return; }

  const sql = `SELECT container, side, shelf, position, ip_address, mac_address, worker
			 FROM machines
			 WHERE ip_address LIKE '%${term}%'
			 OR mac_address LIKE '%${term}%'
			 OR worker LIKE '%${term}%'
			 LIMIT 100`;

  const res = db.exec(sql);
  resultsBody.innerHTML = "";

  if (res.length) {
    res[0].values.forEach(row => {
      const tr = document.createElement('tr');
      for (let i = 0; i < 7; i++) {
	td = document.createElement('td');
	if (i < 2) {
	  td.setAttribute('onclick', 'navigateToRackView("' + row[0] + '", "' + row[1] + '")')
	  td.setAttribute('style', 'cursor:pointer; text-decoration:underline;');
	  td.setAttribute('title', "Click to view rack");
	}
	if (row[i] != null) {
	  if (i == 4) {
	    td.setAttribute('style', 'cursor:pointer');
	    td.innerHTML = `<a href=http://${row[i]}>${row[i]}</a>`;
	    td.setAttribute('title', "Click to open web UI");
	  } else {
	    td.innerHTML = `${row[i]}`;
	  }
	}
	tr.appendChild(td);
      }
      resultsBody.appendChild(tr);
    });
  } else {
    resultsBody.innerHTML = "<tr><td colspan='6' style='text-align:center'>No matches found.</td></tr>";
  }
}

function navigateToRackView(container, side) {
  document.getElementById('containerSelect').value = container;
  onContainerChange();
  document.getElementById('sideSelect').value = side;
  renderRack();
  showPage('visual-page');
}

async function syncDatabase() {
  const btn = document.getElementById('syncBtn');
  const status = document.getElementById('status');
  const btnlabel = btn.innerHTML;
  // Disable button and show loading state
  btn.disabled = true;
  btn.innerHTML = `<span class="spinning">🔄</span> Syncing...`;
  status.textContent = "Connecting to server...";

  try {
    const url = `${BASE_URL}/update`
    const response = await fetch(url)
    const result = await response.text();

    if (response.ok) {
      status.textContent = "✅ " + result + " Refreshing view...";
      // Wait 1.5 seconds so the user can see the success message
      setTimeout(() => {
	location.reload();
      }, 1500);
    } else {
      throw new Error('Server error: ' + result);
    }
  } catch (error) {
    status.textContent = "❌ Sync failed: " + error;
    console.error(error);
    btn.disabled = false;
    btn.innerHTML = btnlabel;
  }
}

async function syncRealTimeData() {
  const machines = document.querySelectorAll('.machine-box');
  const btn = document.getElementById('monSyncBtn');
  const buttonText =  btn.innerText;

  btn.disabled = true;
  btn.innerText = "Syncing...";

  // Create an array of promises to fetch all IPs in parallel
  const promises = Array.from(machines).map(async (el) => {
    const ip = el.getAttribute('data-ip');
    if (!ip) return;

    const url = `${BASE_URL}/mon?ip=` + ip

    try {
      const response = await fetch(url);
      const data = await response.json();
      if (data.hits.hits.length > 0) {
	const source = data.hits.hits[0]._source;
	updateMachineUI(el, source);
      }
    } catch (err) {
      console.error(`Failed to fetch status for ${ip}`, err);
    }
  });

  await Promise.all(promises);
  btn.disabled = false;
  btn.innerText = buttonText;
}

function updateMachineUI(element, data) {
  // Change Color based on "code"
  const temperature_alerts = [352, 350, 600, 351];
  const power_input_alerts = [250, 251, 271, 246, 247, 248, 249, 206, 207, 217, 213, 203, 204, 205];
  const power_output_alerts = [272, 276, 277,278, 279, 280];
  let bgColor = "#4b5563"; // Default Gray
  if (data.code === 7 || data.code == 9) bgColor = "#059669"; // Green
  else if (data.code === 11) bgColor = "#a5a424"; // Lime-Olive
  else if (temperature_alerts.includes(data.code)) bgColor = "#9d174d"; // Crimson
  else if (power_input_alerts.includes(data.code)) bgColor = '#2563eb'; // electric blue
  else if (power_output_alerts.includes(data.code)) bgColor = '#0891b2'; // Cyan
  else if (data.code < 0) bgColor = "#ff0000"; // Red
  else bgColor = "#ea580c"; // Orange
  element.style.backgroundColor = bgColor;

  // 2. Add Hover Content (Tooltip)
  const tooltipContent = `IP: ${data.host.ip}\n`+
	`Code: ${data.code}\n` +
	`Msg: ${data.message}\n` +
	`${new Date(data['@timestamp']).toLocaleString()}`;
  element.setAttribute('title', tooltipContent);
}


let videoFiles = [];

// Call this when the page loads
async function initVideoList() {
    try {
	// Fetch the directory listing from your server
	const response = await fetch('/video');
	const html = await response.text();

	// Use a DOM parser to extract filenames and sizes from the server's HTML listing
	const parser = new DOMParser();
	const doc = parser.parseFromString(html, 'text/html');

	const listItems = Array.from(doc.querySelectorAll('li'));

	videoFiles = listItems.map(li => {
	  const link = li.querySelector('a');
	  if (!link) return null;
	  const text = li.textContent;
	  // Regex to extract the size inside the parentheses
	  const sizeMatch = text.match(/\(([^)]+)\)/);

	  return {
	    name: link.innerText,
	    url: '/video' + new URL(link.href).pathname,
	    size: sizeMatch ? sizeMatch[1] : "Unknown"
	  };
	}).filter(item => item !== null);
	console.log("Video library indexed and ready for search.");
    } catch (e) {
	console.error("Could not load video directory", e);
    }
}

function searchVideos() {
    const query = document.getElementById('video-search-input').value.toLowerCase();
    const resultsContainer = document.getElementById('video-results');

    if (query.length < 2) {
	resultsContainer.innerHTML = '';
	return;
    }

    let filtered = [];
    try {
        // 'i' flag makes it case-insensitive
        const regex = new RegExp(query, 'i');
        filtered = videoFiles.filter(file => regex.test(file.name));
    } catch (e) {
        // If the regex is invalid while they are typing, we just stop
        // and wait for them to finish the expression.
        return;
    }

    // Build the table using your existing CSS classes
    resultsContainer.innerHTML = `
	<div class="table-container">
	    <table>
		<thead>
		    <tr>
			<th>Filename</th>
			<th style="text-align: right;">Size</th>
		    </tr>
		</thead>
		<tbody>
		    ${filtered.map(file => `
			<tr onclick="window.location.href='${file.url}'" style="cursor: pointer;">
			    <td>
				<span style="color: #a5b424; margin-right: 8px;">▶</span>
				${file.name}
			    </td>
			    <td style="text-align: right; font-family: monospace; color: #64748b;">
				${file.size}
			    </td>
			</tr>
		    `).join('')}
		</tbody>
	    </table>
	</div>
    `;
}

window.addEventListener('DOMContentLoaded', () => {
  // Initialize the Video Search List
  // This fetches the directory listing once so searching is instant
  initVideoList();
});


initApp();
