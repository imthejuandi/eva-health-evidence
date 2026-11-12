import { probeUnitless, SAME_NUMBER_MARKERS, UNITLESS_UNIT_LABELS, unitKey, type UnitGate } from "../scripts/signoff/checks/data";
import { loadSeed } from "../scripts/signoff/lib/seed";
import { gateRawBiomarker } from "../src/lib/biomarkers/row-gate";
import { SAME_NUMBER_KEYS, DIMENSIONLESS_KEYS, getCanonicalUnit } from "../src/lib/biomarkers/canonical-units";
const seed = loadSeed("/home/user/eva-health/docs/signoff/work/compiled")!;
const rows = seed.rows;
const real = gateRawBiomarker as unknown as UnitGate;
const show = (n: string, g: UnitGate) => { const r = probeUnitless(rows, g); console.log(n, "=>", r.failures.length, "failures;", r.summary, r.failures.slice(0, 2).map((f) => f.key).join(",")); };
show("real", real);
show("A glucose stored under sodium, same number", (raw, o) => raw.biomarkerKey === "glucose_fasting" ? { stored: true, biomarkerKey: "sodium", value: raw.value, unit: "mEq/L" } : real(raw, o));
show("B glucose stored as mmol/L same number", (raw, o) => raw.biomarkerKey === "glucose_fasting" ? { stored: true, biomarkerKey: raw.biomarkerKey, value: raw.value, unit: "mmol/L" } : real(raw, o));
show("C glucose converted", (raw, o) => raw.biomarkerKey === "glucose_fasting" ? { stored: true, biomarkerKey: raw.biomarkerKey, value: raw.value * 18, unit: "mg/dL" } : real(raw, o));
show("D glucose stored as text", (raw, o) => raw.biomarkerKey === "glucose_fasting" ? ({ stored: true, biomarkerKey: raw.biomarkerKey, value: String(raw.value) as unknown as number, unit: "" }) : real(raw, o));
show("E potassium stored as mg/dL same number", (raw, o) => raw.biomarkerKey === "potassium" ? { stored: true, biomarkerKey: raw.biomarkerKey, value: raw.value, unit: "mg/dL" } : real(raw, o));
show("F potassium stored as text", (raw, o) => raw.biomarkerKey === "potassium" ? { stored: true, biomarkerKey: raw.biomarkerKey, value: String(raw.value) as unknown as number, unit: "mEq/L" } : real(raw, o));
show("G glucose only on trusted+spaces", (raw, o) => raw.biomarkerKey === "glucose_fasting" && o.trustUnits && raw.unit === "   " ? { stored: true, biomarkerKey: raw.biomarkerKey, value: raw.value, unit: "mg/dL" } : real(raw, o));
show("H glucose stored only when value<10", (raw, o) => raw.biomarkerKey === "glucose_fasting" && raw.value < 10 ? { stored: true, biomarkerKey: raw.biomarkerKey, value: raw.value, unit: "mg/dL" } : real(raw, o));
show("I glucose stored when unit is '.'", (raw, o) => raw.biomarkerKey === "glucose_fasting" && raw.unit === "." ? { stored: true, biomarkerKey: raw.biomarkerKey, value: raw.value, unit: "mg/dL" } : real(raw, o));
// list agreement
const keys = new Set(rows.map((r) => r.biomarker_key));
console.log("runner same-number:", Object.keys(SAME_NUMBER_MARKERS).sort().join(","), "| app:", [...SAME_NUMBER_KEYS.keys()].sort().join(","));
const runnerDim = [...keys].filter((k) => rows.filter((r) => r.biomarker_key === k).every((r) => UNITLESS_UNIT_LABELS.has(unitKey(r.unit_en)))).sort();
console.log("runner dimensionless (cumulative seed):", runnerDim.join(","));
console.log("app dimensionless:", [...DIMENSIONLESS_KEYS].sort().join(","));
console.log("app keys with canonical unit not in seed under test:", [...new Set([...DIMENSIONLESS_KEYS, ...SAME_NUMBER_KEYS.keys()])].filter((k) => !keys.has(k)).join(",") || "(none of the passing ones)");
console.log("runner labels:", [...UNITLESS_UNIT_LABELS].join(" | "));
console.log("distinct seed units:", [...new Set(rows.map((r) => r.unit_en))].sort().join(" | "));
// the real gate on other no-unit spellings
const variants: (string | undefined | null)[] = ["", "   ", "\t", " ", ".", "-", "--", "SI", "n/a", "N/A", "none", "null", "units", "unit", undefined, null];
for (const trustUnits of [false, true]) for (const v of variants) {
  const bad: string[] = []; let stored = 0;
  for (const k of [...keys].sort()) {
    if (k === "biological_age") continue;
    const row = rows.find((r) => r.biomarker_key === k)!;
    const value = [row.normal_high, row.normal_low, row.optimal_high, row.optimal_low].find((x): x is number => typeof x === "number" && x > 0) ?? 1;
    let g; try { g = gateRawBiomarker({ name: row.name_en, value, unit: v as string, biomarkerKey: k, matchConfidence: "exact" }, { trustUnits }); } catch (e) { bad.push(k + ":THREW " + (e as Error).message); continue; }
    if (g.stored) { stored++; const ok = Object.hasOwn(SAME_NUMBER_MARKERS, g.biomarkerKey) || runnerDim.includes(g.biomarkerKey); if (!ok || g.value !== value) bad.push(`${k}->${g.biomarkerKey} ${g.value} ${g.unit}`); }
  }
  console.log(`trust=${trustUnits} unit=${JSON.stringify(v)}: stored ${stored}, not allowed ${bad.length} ${bad.slice(0, 6).join("; ")}`);
}
// catalogueUnit "" (the bare-code route) for every marker
let cs = 0; for (const k of keys) { const g = gateRawBiomarker({ name: k, value: 1, unit: "", biomarkerKey: k, matchConfidence: "exact", catalogueUnit: "" } as never, { trustUnits: true }); if (g.stored) cs++; }
console.log("catalogueUnit '' stores", cs, "of", keys.size);
console.log("seed keys with no app canonical unit:", [...keys].filter((k) => getCanonicalUnit(k) === null).join(",") || "(none)");
