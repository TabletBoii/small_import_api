function openModal(modalId, formAction, data = {}) {
  const modal = document.getElementById(modalId);
  const form = modal.querySelector("form");

  if (!form) {
    console.error("Форма не найдена в модальном окне");
    return;
  }

  form.action = formAction;

  Object.keys(data).forEach(key => {
    const textToFind = data[key];
    const select = document.querySelector(`select[name="${key}"]`);

    if (select) {
      for (const option of select.options) {
        if (option.textContent.trim() === textToFind) {
          select.value = option.value;
          break;
        }
      }
      return;
    }
    const input = form.querySelector(`[name="${key}"]`);
    if (input) {
      input.value = data[key] ?? "";
    }
  });

  modal.style.display = "block";
}



function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  modal.style.display = "none";
}
window.onclick = function(event) {
  document.querySelectorAll(".modal").forEach(modal => {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
}
