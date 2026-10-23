(function (global) {
  "use strict";

  let fixtureData;
  let fixtureLoad;

  global.MapFixtures = {
    async load() {
      if (fixtureData) {
        this.data = fixtureData;
        return fixtureData;
      }
      if (!fixtureLoad) {
        fixtureLoad = Promise.all([
          fetch("./fixtures/bess.geojson"),
          fetch("./fixtures/peatland.geojson")
        ]).then(async (responses) => {
          for (const response of responses) {
            if (!response.ok) throw new Error("Fixture request failed: " + response.url);
          }
          const [bess, peatland] = await Promise.all(responses.map((response) => response.json()));
          const collections = [bess, peatland];
          if (collections.some((collection) =>
            collection.type !== "FeatureCollection" ||
            !Array.isArray(collection.features) ||
            !collection.metadata?.sourceDate ||
            !collection.metadata?.attribution
          )) {
            throw new Error("Fixture GeoJSON is missing required metadata or features");
          }
          fixtureData = {
            sourceDate: collections[0].metadata.sourceDate,
            attribution: collections[0].metadata.attribution,
            collections,
            features: collections.flatMap((collection) =>
              collection.features.map((feature) => ({
                id: feature.properties.id,
                type: feature.properties.type,
                name: feature.properties.name,
                left: feature.properties.displayPosition.left,
                top: feature.properties.displayPosition.top
              }))
            )
          };
          this.data = fixtureData;
          return fixtureData;
        }).catch((error) => {
          fixtureLoad = null;
          throw error;
        });
      }
      const loaded = await fixtureLoad;
      this.data = loaded;
      return loaded;
    }
  };
})(globalThis);
