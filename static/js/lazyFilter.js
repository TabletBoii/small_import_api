document.addEventListener('DOMContentLoaded', () => {
  const container   = document.getElementById('lazy-filter-items-container');
  const searchInput = document.getElementById('search-input');
  const dropdown    = document.querySelector('.filter-dropdown');

  let skip     = 0;
  const limit  = 20;
  let loading  = false;
  let hasMore  = true;
  let queryStr = "";

  async function loadItems(reset = false) {
    if (loading || (!hasMore && !reset)) return;
    loading = true;

    if (reset) {
      skip    = 0;
      hasMore = true;
      container.innerHTML = "";
    }

    const url = `/web/report_dmc/items?q=${encodeURIComponent(queryStr)}&skip=${skip}&limit=${limit}`;
    try {
      const res   = await fetch(url);
      const json  = await res.json();
      const items = json.items;

      if (items.length < limit) hasMore = false;

      for (const it of items) {
        const div = document.createElement('div');
        div.className = 'filter-item';
        div.textContent = it.name;
        container.appendChild(div);
      }
      skip += items.length;
    } catch (err) {
      console.error('Ошибка загрузки:', err);
    } finally {
      loading = false;
    }
  }

  function debounce(fn, delay = 300) {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), delay);
    };
  }

  searchInput.addEventListener('focus', () => {
    dropdown.classList.add('open');
  });

  document.addEventListener('click', e => {
    if (!dropdown.contains(e.target)) {
      dropdown.classList.remove('open');
    }
  });

  searchInput.addEventListener('input', debounce(e => {
    queryStr = e.target.value.trim();
    hasMore  = true;
    loadItems(true);
  }, 300));

  container.addEventListener('scroll', () => {
    if (container.scrollTop + container.clientHeight >= container.scrollHeight - 10) {
      loadItems();
    }
  });

  container.addEventListener('click', e => {
    if (e.target.classList.contains('filter-item')) {
      searchInput.value = e.target.textContent;
      dropdown.classList.remove('open');
    }
  });

  loadItems();
});