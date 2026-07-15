requireAuth();

function getLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve(null);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => resolve(null),
      { timeout: 4000 }
    );
  });
}

async function load() {
  const loc = await getLocation();
  const qs = loc ? `?lat=${loc.lat}&lng=${loc.lng}` : "";
  const listEl = document.getElementById("clinic-list");

  try {
    const clinics = await apiFetch(`/api/clinics${qs}`);
    const center = loc || { lat: 37.5665, lng: 126.978 };
    const map = L.map("clinics-map").setView([center.lat, center.lng], 14);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    L.marker([center.lat, center.lng], { title: "내 위치" })
      .addTo(map)
      .bindPopup("내 위치")
      .openPopup();

    clinics.forEach((c) => {
      L.marker([c.lat, c.lng]).addTo(map).bindPopup(`<strong>${c.name}</strong><br/>${c.address}`);
    });

    listEl.innerHTML = clinics
      .map(
        (c) => `
      <div class="clinic-item">
        <div class="name">${c.name}</div>
        <div class="meta">${c.address} · ${c.distance_km}km</div>
        <div class="meta">📞 ${c.phone}</div>
      </div>`
      )
      .join("");
  } catch (e) {
    listEl.innerHTML = `<p class="center-note">${e.message}</p>`;
  }
}

load();
