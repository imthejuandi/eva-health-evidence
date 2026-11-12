import { loadSeed } from "../scripts/signoff/lib/seed";
import { gateRawBiomarker } from "../src/lib/biomarkers/row-gate";
const rows = loadSeed("/home/user/eva-health/docs/signoff/work/compiled")!.rows;
const keys = [...new Set(rows.map((r) => r.biomarker_key))].sort();
for (const v of ["-", "xyz", "mg/dL"]) {
  const out: string[] = [];
  for (const k of keys) {
    const row = rows.find((r) => r.biomarker_key === k)!;
    const value = [row.normal_high, row.normal_low, row.optimal_high, row.optimal_low].find((x): x is number => typeof x === "number" && x > 0) ?? 1;
    const g = gateRawBiomarker({ name: row.name_en, value, unit: v, biomarkerKey: k, matchConfidence: "exact" }, { trustUnits: false });
    if (g.stored) out.push(`${k}(${row.unit_en}) ${value}->${g.biomarkerKey} ${g.value} ${g.unit} src=${g.unitSource}`);
  }
  console.log(JSON.stringify(v), out.length, out.join("; "));
}
