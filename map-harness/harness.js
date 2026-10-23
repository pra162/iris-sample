(function (global) {
  "use strict";

  const STYLE_DELAY_MS = 24;
  const TILE_DELAY_MS = 30;
  const MAX_TILE_RETRIES = 2;

  function mockStyleSource() {
    return new Promise((resolve) => {
      setTimeout(() => resolve({ id: "mock-style", version: 1 }), STYLE_DELAY_MS);
    });
  }

  function mockTileSource(attempt, failuresBeforeSuccess) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (attempt <= failuresBeforeSuccess) {
          reject(new Error("Mock tile source unavailable (attempt " + attempt + ")"));
          return;
        }
        resolve({ id: attempt > 1 ? "local-fallback-tiles" : "mock-tiles" });
      }, TILE_DELAY_MS);
    });
  }

  function bindLayerToggles(root) {
    for (const [controlId, type] of [
      ["toggle-bess", "bess"],
      ["toggle-peatland", "peatland"]
    ]) {
      const control = root.querySelector("#" + controlId);
      if (!control) continue;
      control.addEventListener("change", (event) => {
        for (const feature of root.querySelectorAll(".fixture." + type)) {
          feature.hidden = !event.currentTarget.checked;
        }
      });
    }
  }

  class MapView {
    constructor(root, options) {
      this.root = root;
      this.options = Object.assign({ tileFailures: 0 }, options);
      this.status = root.querySelector(".map-status-label");
      this.retryButton = root.querySelector("#retry-map");
      this.fixtureLayer = root.querySelector("#fixture-layer");
      this.startedAt = performance.now();
      this.readyAt = null;
      this.disposed = false;
      if (this.retryButton) {
        this.retryButton.addEventListener("click", () => {
          this.options.tileFailures = 0;
          this.loadPromise = this.initialize();
        });
      }
      this.loadPromise = this.initialize();
    }

    setState(state, message) {
      this.root.dataset.state = state;
      this.status.textContent = message;
      if (this.retryButton) this.retryButton.hidden = state !== "error";
    }

    async initialize() {
      this.startedAt = performance.now();
      this.readyAt = null;
      this.setState("loading", "Loading map style…");
      try {
        await mockStyleSource();
      } catch (error) {
        this.setState("error", "Map style failed to load. Retry to recover.");
        throw error;
      }
      if (this.disposed) return;

      this.root.dataset.styleVisible = "true";
      this.readyAt = performance.now();
      this.root.dataset.firstStyleMs = (this.readyAt - this.startedAt).toFixed(2);
      this.setState("recovering", "Map style ready; loading map tiles…");
      try {
        await global.MapFixtures.load();
        if (this.disposed) return;
        this.renderFixtures();
        this.renderSources();
      } catch (error) {
        this.setState("error", "Map fixtures failed to load. Retry to recover.");
        return;
      }

      let attempt = 0;
      while (attempt <= MAX_TILE_RETRIES) {
        attempt += 1;
        try {
          const source = await mockTileSource(attempt, this.options.tileFailures);
          if (this.disposed) return;
          this.root.dataset.tileSource = source.id;
          this.setState(
            source.id === "local-fallback-tiles" ? "fallback" : "ready",
            source.id === "local-fallback-tiles"
              ? "Map ready using fallback tiles."
              : "Map ready."
          );
          return;
        } catch (error) {
          if (this.disposed) return;
          if (attempt > MAX_TILE_RETRIES) {
            this.setState("error", "Map tiles failed. Retry to recover.");
            return;
          }
          this.setState("recovering", "Map tiles unavailable; retrying (" + attempt + "/" + MAX_TILE_RETRIES + ")…");
        }
      }
    }

    renderFixtures() {
      this.fixtureLayer.replaceChildren();
      for (const feature of global.MapFixtures.data.features) {
        const marker = document.createElement("span");
        marker.className = "fixture " + feature.type;
        marker.dataset.featureId = feature.id;
        marker.title = feature.name;
        marker.setAttribute("aria-label", feature.name);
        marker.style.left = feature.left;
        marker.style.top = feature.top;
        this.fixtureLayer.append(marker);
      }
    }

    renderSources() {
      const tbody = document.querySelector("#source-rows");
      if (!tbody) return;
      tbody.replaceChildren();
      for (const collection of global.MapFixtures.data.collections) {
        const layer = collection.metadata.layer;
        const attribution = collection.metadata.attribution;
        const row = document.createElement("tr");
        for (const value of [layer, attribution, collection.metadata.sourceDate]) {
          const cell = document.createElement("td");
          cell.textContent = value;
          row.append(cell);
        }
        tbody.append(row);
      }
    }

    dispose() {
      this.disposed = true;
    }
  }

  function simulateLegacyRace(root) {
    const status = root.querySelector(".map-status-label");
    root.dataset.state = "loading";
    root.dataset.styleVisible = "false";
    status.textContent = "Loading map style…";

    let listenerAttached = false;
    mockStyleSource().then(() => {
      if (listenerAttached) {
        root.dataset.styleVisible = "true";
        root.dataset.state = "ready";
        status.textContent = "Map ready.";
      }
    });

    return new Promise((resolve) => {
      setTimeout(() => {
        listenerAttached = true;
        if (root.dataset.styleVisible !== "true") {
          root.dataset.state = "error";
          status.textContent = "Style-ready event was missed; map remains blank.";
        }
        resolve({
          styleVisible: root.dataset.styleVisible === "true",
          state: root.dataset.state
        });
      }, STYLE_DELAY_MS + 8);
    });
  }

  global.MapHarness = {
    MapView,
    simulateLegacyRace,
    bindLayerToggles,
    constants: { STYLE_DELAY_MS, TILE_DELAY_MS, MAX_TILE_RETRIES }
  };
})(globalThis);
