document.addEventListener('DOMContentLoaded', () => {
  Object.entries(window.tableConfig || {}).forEach(([id, cfg]) => {
    const { headers, saveUrl } = cfg;
    console.log(id)
    console.log(cfg)

    const table   = document.getElementById(id);
    const saveBtn = document.getElementById(`save-btn-${id}`);
    const addBtn  = document.getElementById(`add-row-${id}`);
    const impBtn  = document.getElementById(`import-excel-${id}`);
    const inpFile = document.getElementById(`excel-file-${id}`);

    table.querySelectorAll('.th-with-menu').forEach(th => {
      const colIdx = +th.dataset.colIndex;
      const btn    = th.querySelector('.menu-btn');
      const menu   = th.querySelector('.filter-menu');
      menu.classList.remove('show');
      menu.addEventListener('click', e => e.stopPropagation());

      initFilterMenu(table, colIdx, menu);
      btn.addEventListener('click', e => {
        e.stopPropagation();
        document.querySelectorAll('.filter-menu.show').forEach(m => m.classList.remove('show'));
        menu.classList.toggle('show');
      });
    });

    document.addEventListener('click', () => {
      document.querySelectorAll('.filter-menu.show').forEach(m => m.classList.remove('show'));
    });

    impBtn.addEventListener('click', () => inpFile.click());
    inpFile.addEventListener('change', async e => {
      const file = e.target.files[0];
      if (!file) return;
      const data = await file.arrayBuffer();
      const wb   = XLSX.read(data, {type:'array'});
      const ws   = wb.Sheets[wb.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json(ws, {header:headers, range:1, defval:''});
      const tbody = table.querySelector('tbody');
      let rowCount = tbody.rows.length;
      rows.forEach(record => {
        const tr = document.createElement('tr');
        tr.setAttribute('data-index', rowCount++);
        tr.innerHTML = headers
          .map(h => `<td><input type="text" name="${h}" value="${record[h] ?? ''}"></td>`)
          .join('')
          + `<td><button type="button" class="btn delete-row">Удалить</button></td>`;
        tbody.appendChild(tr);
      });
      e.target.value = '';
    });

    table.addEventListener('click', e => {
      const tr = e.target.closest('tr');
      if (!tr) return;

      if (e.target.matches('.delete-row')) {
        tr.remove();
        return;
      }

      if (e.target.matches('.duplicate-row')) {
        const clone = tr.cloneNode(true);

        const incInput = clone.querySelector('input[name="inc"]');
        if (incInput) incInput.value = '0';

        const currentIdx = Number(tr.getAttribute('data-index'));
        const newIdx = currentIdx + 1;
        clone.setAttribute('data-index', newIdx);

        tr.parentNode.insertBefore(clone, tr.nextSibling);
        clone.classList.add('tr-highlight');
        clone.addEventListener('animationend', () => {
          clone.classList.remove('tr-highlight');
        }, { once: true });
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        rows.forEach((r, idx) => r.setAttribute('data-index', idx));

        return;
      }
    });

    addBtn.addEventListener('click', () => {
      const tbody = table.querySelector('tbody');
      const rowCount = tbody.rows.length;
      const tr = document.createElement('tr');
      tr.setAttribute('data-index', rowCount);
      tr.innerHTML = headers
        .map(h => {
                if (h !== 'inc') {
                    return `<td><input type="text" name="${h}" value=""></td>`;
                } else {
                    return `<td style="display: none;"><input type="text" name="${h}" value="0"></td>`;
                }
            }
        )
        .join('')
        + `<td><button type="button" class="btn delete-row">Удалить</button></td>`;
      tbody.appendChild(tr);
      tr.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });

    saveBtn.addEventListener('click', async () => {
      const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr => {
        const obj = {};
        obj["inc"] = tr.querySelector(`input[name="inc"]`) ? tr.querySelector(`input[name="inc"]`).value : 0;
        headers.forEach(h => {
          const inp = tr.querySelector(`input[name="${h}"]`);
          obj[h] = inp ? inp.value : '';
        });
        return obj;
      });

      const resp = await fetch(saveUrl, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(rows)
      });

      const path = new URL(resp.url).pathname;

      if (path == '/web/login') {
        window.location.href = resp.url;
        return;
      }

      if (!resp.ok) {
        showToast("Ошибка");
      }
      const data = await resp.json();
      showToast("Успешно сохранено", "suc");
    });
  });
});

function initFilterMenu(table, colIdx, menu) {
  menu.innerHTML = '';
  const separator = document.createElement('hr');
  const separator1 = document.createElement('hr');
  const separator2 = document.createElement('hr');

  const search = document.createElement('input');
  search.type = 'text';
  search.placeholder = 'Поиск…';
  search.style.width = '100%';
  search.style.margin = '0.5rem 0';

  const allDiv = document.createElement('div');
  allDiv.style.padding = '3px';

  const allCb = document.createElement('input');
  allCb.type = 'checkbox';
  allCb.checked = true;
  allCb.id = `select-all-${colIdx}`;

  const allLbl = document.createElement('label');
  allLbl.htmlFor = allCb.id;
  allLbl.textContent = 'Выбрать все';
  allDiv.append(allCb, ' ', allLbl);

  const sortAsc = document.createElement('div');
  const sortDesc = document.createElement('div');
  sortAsc.textContent = 'Сортировка по возрастанию ↑';
  sortDesc.textContent = 'Сортировка по убыванию ↓';

  sortAsc.style.cursor = 'pointer';
  sortAsc.style.padding = '3px';
  sortAsc.classList.add('filter-table-sort-btn')

  sortDesc.style.cursor = 'pointer';
  sortDesc.style.padding = '3px';
  sortDesc.classList.add('filter-table-sort-btn')


  menu.append(separator, sortAsc, sortDesc, separator1, search, separator, allDiv, separator2);

  sortAsc.addEventListener('click', () => sortTable(table, colIdx, 'asc'));
  sortDesc.addEventListener('click', () => sortTable(table, colIdx, 'desc'));

  // собираем уникальные значения из текущей таблицы
  const values = Array.from(table.querySelectorAll('tbody tr'))
    .map(tr => tr.cells[colIdx].querySelector('input').value)
    .filter((v,i,a) => a.indexOf(v)===i)
    .sort((a,b) => a.localeCompare(b, 'ru', { numeric: true }));

  values.forEach(val => {
    const row = document.createElement('div');
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.value = val;
    cb.checked = true;
    cb.id = `f-${colIdx}-${val}`;
    const lbl = document.createElement('label');
    lbl.htmlFor = cb.id;
    lbl.textContent = val;
    row.append(cb, ' ', lbl);
    row.style.padding = '2px';
    menu.append(row);
    cb.addEventListener('change', () => applyFilter(table, colIdx));
  });

  search.addEventListener('input', () => {
    const term = search.value.trim().toLowerCase();
    menu.querySelectorAll('div').forEach(div => {
      const label = div.querySelector('label');
      if (!label) return;
      div.style.display = label.textContent.toLowerCase().includes(term) ? '' : 'none';
    });
  });

  allCb.addEventListener('change', () => {
    const checked = allCb.checked;
    menu.querySelectorAll('input[type=checkbox]').forEach(cb => {
      if (cb !== allCb) cb.checked = checked;
    });
    applyFilter(table, colIdx);
  });
}

function applyFilter(table, colIdx) {
  const menu = table.querySelector(`.th-with-menu[data-col-index="${colIdx}"] .filter-menu`);
  const checked = Array.from(menu.querySelectorAll(`input[type=checkbox]:not(#select-all-${colIdx}):checked`))
                       .map(c => c.value);
  table.querySelectorAll('tbody tr').forEach(tr => {
    const cell = tr.cells[colIdx].querySelector('input').value;
    tr.style.display = checked.includes(cell) ? '' : 'none';
  });
}

function sortTable(table, colIdx, direction) {
  const tbody = table.querySelector('tbody');
  Array.from(tbody.rows)
    .filter(r => r.style.display !== 'none')
    .sort((a, b) => {
      const va = a.cells[colIdx].querySelector('input').value.toLowerCase();
      const vb = b.cells[colIdx].querySelector('input').value.toLowerCase();
      return direction === 'asc'
        ? va.localeCompare(vb, 'ru', { numeric: true })
        : vb.localeCompare(va, 'ru', { numeric: true });
    })
    .forEach(r => tbody.appendChild(r));
}
