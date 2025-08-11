function openModal(modalId, formAction, data = {}, item_keys=[]) {
  const modal = document.getElementById(modalId);
  const form = modal.querySelector("form");

  if (!form) {
    console.error("Форма не найдена в модальном окне");
    return;
  }

  form.action = formAction;
  const modalItemName = form.querySelector(`span[id="${modalId}-item"]`);
  if (modalItemName && item_keys) {
    let modalItemNameStr = ""
    for (let i = 0; i < item_keys.length; i++) {
        if (i === item_keys.length-1) {
            modalItemNameStr += data[item_keys[i]]
            break;
        }
        modalItemNameStr += data[item_keys[i]] + "---"

    }
    modalItemName.innerHTML = modalItemNameStr;
  }
  console.log(data);
  if (data) {
      Object.keys(data).forEach(key => {
        const textToFind = data[key];
        const select = document.querySelector(`select[name="${key}"]`);
        const input = form.querySelector(`[name="${key}"]`);
        const div = form.querySelector(`div[name="${key}"]`)
        if (div) {
            div.innerHTML = data[key] ?? "";
        }
        if (select) {
          for (const option of select.options) {
            if (option.textContent.trim() === textToFind) {
              select.value = option.value;
              break;
            }
          }
          return;
        }

        if (input) {
          input.value = data[key] ?? "";
        }
      });
  }


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
