(function () {
  const select = document.getElementById("register-mac");
  if (!select) return;
  fetch("/api/bluetooth/nearby", { cache: "no-store" })
    .then((response) => response.json())
    .then((data) => {
      (data.devices || []).forEach((device) => {
        const option = document.createElement("option");
        option.value = device.mac;
        option.textContent = `${device.name} (${device.mac})`;
        select.appendChild(option);
      });
    });
})();
