"""Run end-to-end: generate data -> clean -> train -> evaluate -> save artefacts."""
import json
from sarps import data_ingestion as di, preprocessing as pp, model as mdl

df = pp.clean(di.load_data())
df.to_csv("data/students_pseudonymised.csv", index=False)
m, name, results, _ = mdl.train(df)
mdl.save(m)
json.dump({"best": name, "results": results, "importance": mdl.feature_importance(m)},
          open("models/metrics.json", "w"), indent=2)
print("Best model:", name)
for k, v in results.items():
    print(k, {a: round(b, 3) for a, b in v.items() if a != "confusion"})
