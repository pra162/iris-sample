(async function () {
  "use strict";

  const output = document.querySelector("#results");
  const mounts = document.querySelector("#mounts");
  const results = [];
  const timings = [];

  function assert(condition, description) {
    if (!condition) throw new Error(description);
    results.push("PASS " + description);
  }

  function createMount() {
    const host = document.createElement("div");
    host.className = "test-mount";
    host.append(document.querySelector("#map-template").content.cloneNode(true));
    mounts.append(host);
    return { host, map: host.firstElementChild };
  }

  try {
    await MapFixtures.load();
    const legacy = createMount();
    const before = await MapHarness.simulateLegacyRace(legacy.map);
    assert(!before.styleVisible, "before fix: fast style event is missed and basemap stays blank");

    const first = createMount();
    const afterMap = new MapHarness.MapView(first.map, { tileFailures: 0 });
    MapHarness.bindLayerToggles(first.host);
    await afterMap.loadPromise;
    assert(first.map.dataset.styleVisible === "true", "after fix: style is visible on initial mount without switching");
    assert(first.map.dataset.state === "ready", "successful tile load reaches ready state");
    assert(first.map.querySelectorAll(".fixture").length === 3, "BESS and peatland fixture features render");
    assert(MapFixtures.data.features.some((feature) => feature.type === "bess"), "BESS fixture layer is present");
    assert(MapFixtures.data.features.some((feature) => feature.type === "peatland"), "peatland fixture layer is present");
    assert(first.map.querySelector(".map-legend"), "map legend is displayed");
    assert(first.map.querySelector(".attribution").textContent.includes("synthetic sample"), "map attribution is displayed");
    assert(document.querySelectorAll("#source-rows tr").length === 2, "source rows are displayed");
    assert(document.querySelector("#source-rows").textContent.includes(MapFixtures.data.sourceDate), "fixture source date is displayed");
    first.host.querySelector("#toggle-bess").click();
    assert(first.map.querySelector(".fixture.bess").hidden, "BESS layer toggle hides BESS features");
    first.host.querySelector("#toggle-peatland").click();
    assert(first.map.querySelector(".fixture.peatland").hidden, "peatland layer toggle hides peatland features");
    afterMap.dispose();

    const recovering = createMount();
    const recoveryMap = new MapHarness.MapView(recovering.map, { tileFailures: 2 });
    await recoveryMap.loadPromise;
    assert(recovering.map.dataset.styleVisible === "true", "map style remains visible when tiles fail");
    assert(recovering.map.dataset.state === "fallback", "failed tiles recover through local fallback tiles");
    assert(recovering.map.dataset.tileSource === "local-fallback-tiles", "fallback tile source is identified");
    recoveryMap.dispose();

    const terminal = createMount();
    const terminalMap = new MapHarness.MapView(terminal.map, { tileFailures: 3 });
    await terminalMap.loadPromise;
    assert(terminal.map.dataset.state === "error", "exhausted tiles report a visible error state");
    assert(terminal.map.dataset.styleVisible === "true", "tile errors never hide the basemap style");
    assert(!terminal.map.querySelector("#retry-map").hidden, "manual retry is offered after fallback exhaustion");
    terminalMap.options.tileFailures = 3;
    terminal.map.querySelector("#retry-map").click();
    await terminalMap.loadPromise;
    assert(terminal.map.dataset.state === "ready", "retry recovers from an exhausted tile error");
    terminalMap.dispose();

    const start = performance.now();
    const timingMap = new MapHarness.MapView(first.map, { tileFailures: 0 });
    while (timingMap.readyAt === null) {
      await new Promise((resolve) => setTimeout(resolve, 1));
    }
    timings.push(Number((timingMap.readyAt - start).toFixed(2)));
    await timingMap.loadPromise;
    timingMap.dispose();

    for (let run = 1; run < 3; run += 1) {
      const mount = createMount();
      const runStart = performance.now();
      const measuredMap = new MapHarness.MapView(mount.map, { tileFailures: 0 });
      while (measuredMap.readyAt === null) {
        await new Promise((resolve) => setTimeout(resolve, 1));
      }
      timings.push(Number((measuredMap.readyAt - runStart).toFixed(2)));
      await measuredMap.loadPromise;
      assert(mount.map.dataset.styleVisible === "true", "timed run " + (run + 1) + " shows style on first load");
      measuredMap.dispose();
    }

    results.push("BEFORE: styleVisible=false (deterministic missed style-ready event)");
    results.push("AFTER: styleVisible=true; tile-failure scenario recovered using local fallback");
    results.push("FIRST-STYLE LATENCY (ms, 3 runs): " + timings.join(", "));
    results.push("MEAN FIRST-STYLE LATENCY (ms): " +
      (timings.reduce((sum, value) => sum + value, 0) / timings.length).toFixed(2));
    output.dataset.result = "pass";
    output.textContent = results.join("\n");
  } catch (error) {
    results.push("FAIL " + error.message);
    output.dataset.result = "fail";
    output.textContent = results.join("\n");
    throw error;
  } finally {
    mounts.replaceChildren();
  }
})();
