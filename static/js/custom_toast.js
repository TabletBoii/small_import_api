function showToast(msg, type="err") {
  if (type === "err") {
    Toastify({
        text: msg,
        duration: 3000,
        close: true,
        gravity: "top",
        position: "right",
        className: "toastify--side",
        backgroundColor: "linear-gradient(to right, #ff3333, #ff8080)",
        offset: {
          x: 20,
          y: 20
        }
    }).showToast();
  } else {
    Toastify({
        text: msg,
        duration: 3000,
        close: true,
        gravity: "top",
        position: "right",
        className: "toastify--side",
        backgroundColor: "linear-gradient(to right, #08a30d, #005703)",
        offset: {
          x: 20,
          y: 20
        }
    }).showToast();
  }
}