(function () {
  "use strict";

  const root = document.querySelector("#map");
  const search = new URLSearchParams(location.search);
  const requestedFailures = Number(search.get("failTiles") || 0);
  const tileFailures = Number.isInteger(requestedFailures) && requestedFailures >= 0 && requestedFailures <= 3
    ? requestedFailures
    : 0;
  let map;
  if (search.get("legacy") === "1") {
    MapHarness.simulateLegacyRace(root);
  } else {
    map = new MapHarness.MapView(root, { tileFailures });
  }
  MapHarness.bindLayerToggles(document);

  window.addEventListener("pagehide", () => map?.dispose(), { once: true });
})();
