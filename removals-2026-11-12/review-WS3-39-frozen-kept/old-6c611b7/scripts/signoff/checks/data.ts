/**
 * D. Data and source of truth (D1-D6) of docs/signoff/ACCEPTANCE-TEST.md.
 */
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import type { Check, CheckResult, Ctx, Failure } from "../types";
import { byKey, loadSeed, rowKey, rowsFor, sortFailures, type RawEn, type RawEs, type Row } from "../lib/seed";
import { rowTraceKey } from "./governance";
import { CATALOGUE_PATH, CODE_MAP_PATH, CONDITION_TO_AGE_GROUP, loadCodeMap, parseCatalogue, type CatalogueRow } from "../lib/echevarne";
import { ageGroupContains } from "../../../src/lib/biomarkers/reference-row";
import { normalizeUnit } from "../../../src/lib/biomarkers/canonical-units";
import { gateRawBiomarker } from "../../../src/lib/biomarkers/row-gate";

const dedupe = (failures: Failure[]): Failure[] => {
  const seen = new Map<string, Failure>();
  for (const f of failures) if (!seen.has(f.key)) seen.set(f.key, f);
  return [...seen.values()];
};
const result = (id: string, failures: Failure[], summary: string, metrics?: Record<string, number | string | boolean>): CheckResult => ({
  id,
  status: failures.length ? "fail" : "pass",
  summary,
  failures: sortFailures(dedupe(failures)),
  ...(metrics ? { metrics } : {}),
});

/**
 * Qualitative "units" the Spanish file translates; both spellings are the same unit. unitKey looks a unit up after
 * normalizeUnit, which removes spaces ("Grupo Sanguíneo" → "gruposanguíneo"), so the table is keyed and valued the
 * same way; written with spaces, its two-word entries were never found.
 */
const UNIT_TRANSLATIONS: Record<string, string> = Object.fromEntries(
  Object.entries({
    "grupo sanguíneo": "blood type",
    patrón: "pattern",
    "patrón a o b": "pattern a or b",
    "positivo/negativo": "positive/negative",
    título: "titer",
    índice: "index",
    años: "years",
    alelos: "alleles",
  }).map(([es, en]) => [normalizeUnit(es), normalizeUnit(en)]),
);
export function unitKey(u: string): string {
  const n = normalizeUnit(u);
  return UNIT_TRANSLATIONS[n] ?? n;
}
const blocked = (id: string, on: string, summary = `blocked: ${on} is missing`): CheckResult => ({ id, status: "blocked", summary, failures: [], blocked_on: on });

// ─── D1 row integrity ───

export const NON_ANALYTE_KEYS: Record<string, string> = {
  biological_age: "pseudo-row removed from part A; its text belongs to the biological age display copy",
};

export function checkRowIntegrity(rows: Row[], opts: { unitByKey?: Map<string, Set<string>> } = {}): { failures: Failure[]; metrics: Record<string, number> } {
  const failures: Failure[] = [];
  const seen = new Map<string, number[]>();
  let orderingViolations = 0;
  let unitMismatches = 0;
  let nonAnalyte = 0;
  for (const r of rows) {
    const k = rowKey(r);
    const list = seen.get(k) ?? [];
    list.push(r.index);
    seen.set(k, list);
    if (NON_ANALYTE_KEYS[r.biomarker_key] || r.category_en === "Biological Age") {
      nonAnalyte++;
      failures.push({ key: `${k}|non_analyte`, detail: `row is not a measurable analyte or defined calculated metric: ${NON_ANALYTE_KEYS[r.biomarker_key] ?? r.category_en}` });
    }
    // Ordering: critical_low < normal_low ≤ optimal_low ≤ optimal_high ≤ normal_high < critical_high, where present.
    const chain: [string, number | null, boolean][] = [
      ["critical_low", r.critical_low, true],
      ["normal_low", r.normal_low, false],
      ["optimal_low", r.optimal_low, false],
      ["optimal_high", r.optimal_high, false],
      ["normal_high", r.normal_high, true],
      ["critical_high", r.critical_high, false],
    ];
    const present = chain.filter((c) => c[1] != null);
    for (let i = 1; i < present.length; i++) {
      const [an, av, strictAfter] = present[i - 1];
      const [bn, bv] = present[i];
      const strict = (an === "critical_low" && strictAfter) || bn === "critical_high";
      const bad = strict ? (av as number) >= (bv as number) : (av as number) > (bv as number);
      if (bad) {
        orderingViolations++;
        failures.push({ key: `${k}|ordering|${an}>${bn}`, detail: `${an} ${av} is not ${strict ? "below" : "at or below"} ${bn} ${bv}` });
      }
    }
    if (opts.unitByKey) {
      const labUnits = opts.unitByKey.get(r.biomarker_key);
      if (labUnits && labUnits.size && ![...labUnits].some((u) => unitKey(u) === unitKey(r.unit_en))) {
        unitMismatches++;
        failures.push({ key: `${k}|unit`, detail: `seed unit "${r.unit_en}" is not Echevarne's reported unit (${[...labUnits].sort().join(", ")})` });
      }
    }
  }
  let duplicates = 0;
  for (const [k, idx] of seen) {
    if (idx.length > 1) {
      duplicates++;
      failures.push({ key: `${k}|duplicate`, detail: `${idx.length} rows share this key (file indexes ${idx.join(", ")}); the seeder keeps the last one silently` });
    }
  }
  return { failures, metrics: { rows: rows.length, duplicate_keys: duplicates, ordering_violations: orderingViolations, unit_mismatches: unitMismatches, non_analyte_rows: nonAnalyte } };
}

/** Echevarne's reported unit per mapped key (several codes can map one key, e.g. HbA1c % and mmol/mol). */
function labUnitsByKey(catalogue: CatalogueRow[], codeMap: Record<string, string>): Map<string, Set<string>> {
  const m = new Map<string, Set<string>>();
  for (const c of catalogue) {
    const key = codeMap[c.code];
    if (!key || !c.unit) continue;
    const set = m.get(key) ?? new Set<string>();
    set.add(c.unit);
    m.set(key, set);
  }
  return m;
}

const D1: Check = {
  id: "D1",
  group: "data",
  title: "Row integrity",
  how: "script",
  run(ctx) {
    const data = rowsFor(ctx);
    if (!data) return blocked("D1", `${ctx.seedDir}/biomarker-ranges-en.json`);
    const catalogue = parseCatalogue(ctx.root);
    const codeMap = loadCodeMap(ctx.root);
    const unitByKey = catalogue && codeMap ? labUnitsByKey(catalogue, codeMap) : undefined;
    const { failures, metrics } = checkRowIntegrity(data.rows, { unitByKey });
    const decimalsTable = ctx.load(`${ctx.workDir}/governance/decimals.json`);
    return result("D1", failures, `${failures.length} violations in ${data.rows.length} rows (${metrics.duplicate_keys} duplicate keys, ${metrics.ordering_violations} ordering, ${metrics.unit_mismatches} unit, ${metrics.non_analyte_rows} non-analyte)`, {
      ...metrics,
      echevarne_unit_check: Boolean(unitByKey),
      decimals_table_present: Boolean(decimalsTable),
      decimals_checked: false,
    });
  },
};

// ─── D2 EN/ES parity ───

/**
 * The Spanish label of each English age group and physiological state. The state labels are the ones the compile
 * writes (docs/signoff/tools/lib/compile-rows.js, STATE_LABEL); a state row with an age band is labelled
 * "<state> <band>" in both files, so its Spanish label is the state's Spanish label and the same band.
 */
const AGE_GROUP_ES: Record<string, string> = {
  "All Adults": "Todos los Adultos",
  "Premenopausal (follicular)": "Premenopáusica (folicular)",
  "Premenopausal (ovulatory)": "Premenopáusica (ovulatoria)",
  "Premenopausal (luteal)": "Premenopáusica (lútea)",
  Postmenopausal: "Posmenopáusica",
  "Ovulatory peak": "Pico ovulatorio",
  Premenopausal: "Premenopáusica",
  Perimenopausal: "Perimenopáusica",
  "On Hormone Therapy": "En Terapia Hormonal",
  "On Oral Contraception": "Con Anticonceptivos Orales",
  Pregnancy: "Embarazo",
  Lactation: "Lactancia",
};
const BANDED_STATE = /^(.+) (\d{1,3}-\d{1,3}|\d{1,3}\+)$/;
export function expectedAgeGroupEs(en: string): string {
  if (Object.hasOwn(AGE_GROUP_ES, en)) return AGE_GROUP_ES[en];
  const m = BANDED_STATE.exec(en);
  if (m && m[1] !== "All Adults" && Object.hasOwn(AGE_GROUP_ES, m[1])) return `${AGE_GROUP_ES[m[1]]} ${m[2]}`;
  return en;
}

export function checkParity(rows: Row[], enCount: number, esCount: number): Failure[] {
  const failures: Failure[] = [];
  if (enCount !== esCount) failures.push({ key: "_count", detail: `English has ${enCount} rows, Spanish ${esCount}` });
  for (const r of rows) {
    const k = rowKey(r);
    if (!r.es_present) {
      failures.push({ key: `${k}|missing_es`, detail: "no Spanish row at this index" });
      continue;
    }
    if (r.sex !== (({ ambos: "both", masculino: "male", femenino: "female" } as Record<string, string>)[r.sex_raw_es.toLowerCase()] ?? r.sex_raw_es.toLowerCase())) failures.push({ key: `${k}|sex`, detail: `EN ${r.sex_raw_en} vs ES ${r.sex_raw_es}` });
    const expectedEs = expectedAgeGroupEs(r.age_group_en);
    if (r.age_group_es !== expectedEs) failures.push({ key: `${k}|age_group`, detail: `EN "${r.age_group_en}" vs ES "${r.age_group_es}" (expected "${expectedEs}")` });
    if (unitKey(r.unit_en) !== unitKey(r.unit_es)) failures.push({ key: `${k}|unit`, detail: `EN "${r.unit_en}" vs ES "${r.unit_es}"` });
    // The six bounds: the compile writes the critical limits in both files (Critical_Low / Crítico_Bajo, …).
    const bounds: [string, number | null, number | null][] = [
      ["normal_low", r.normal_low, r.es_normal_low],
      ["normal_high", r.normal_high, r.es_normal_high],
      ["optimal_low", r.optimal_low, r.es_optimal_low],
      ["optimal_high", r.optimal_high, r.es_optimal_high],
      ["critical_low", r.critical_low, r.es_critical_low],
      ["critical_high", r.critical_high, r.es_critical_high],
    ];
    for (const [name, en, es] of bounds) if (en !== es) failures.push({ key: `${k}|${name}`, detail: `EN ${en} vs ES ${es}` });
    for (const zone of ["critical_low", "below_optimal", "optimal", "above_optimal", "critical_high"] as const) {
      const m = r.msg[zone];
      if ((m.en == null) !== (m.es == null)) failures.push({ key: `${k}|msg_${zone}`, detail: `message present in ${m.en ? "EN" : "ES"} only` });
    }
  }
  return failures;
}

/**
 * The Spanish columns that carry the English text because the row has no Spanish counterpart: the compile lists them
 * in compile-report.json ("untranslated": Unidad, Fuente_Referencia, Motivo_Sin_Crítico or Nota_Método with the
 * row field that would supply it). Each is a parity failure, since the Spanish file then shows English. A compile
 * output is a seed directory with the compile's changes.json; one without its compile-report.json cannot say which
 * columns are untranslated and fails. Today's seed, which no compile wrote, has neither file.
 */
export function untranslatedFailures(report: unknown, compiled: boolean): Failure[] {
  if (report == null) return compiled ? [{ key: "_untranslated", detail: "compile output without compile-report.json: the Spanish columns that carry English text cannot be read" }] : [];
  const list = (report as { untranslated?: unknown }).untranslated;
  if (!Array.isArray(list)) return [{ key: "_untranslated", detail: "compile-report.json has no untranslated list" }];
  return list.map((x) => {
    const e = (x ?? {}) as { seed_key?: string; row_key?: string; field?: string; from_field?: string; spanish_field?: string };
    return { key: `${e.seed_key ?? e.row_key ?? "?"}|untranslated|${e.field ?? "?"}`, detail: `${e.field ?? "a Spanish column"} carries the English text of ${e.from_field ?? "its English field"}: the row has no ${e.spanish_field ?? "Spanish counterpart"}` };
  });
}

/** The Spanish text columns the compile fills from a row's Spanish field, with their English columns (docs/signoff/tools/lib/compile-rows.js, EXT and ES_TEXT). */
const TEXT_COLUMNS: readonly (readonly [english: string, spanish: string])[] = [
  ["Critical_None_Reason", "Motivo_Sin_Crítico"],
  ["Reference_Source", "Fuente_Referencia"],
  ["Method_Note", "Nota_Método"],
];
const sameText = (v: unknown): string => (typeof v === "string" ? v.trim().replace(/\s+/g, " ").toLowerCase() : "");

/**
 * The same fact read from the two seed files themselves, which G1 holds to the compile byte for byte: a Spanish text
 * column that holds its English column's non-empty text (after trimming, collapsing spaces and ignoring case) shows
 * English in the Spanish file, whatever compile-report.json lists, whether the row gave no Spanish field or stated the
 * English text as its Spanish field, and whether or not the report is there. The key is the one a report entry has,
 * so a column both name is counted once. A unit is mostly written the same in both languages (mg/dL), so equal units
 * say nothing, and a Unidad entry is read from the report only.
 */
export function copiedTextFailures(rows: Row[], en: RawEn[], es: RawEs[]): Failure[] {
  const failures: Failure[] = [];
  for (const r of rows) {
    if (!r.es_present) continue;
    for (const [ce, cs] of TEXT_COLUMNS) {
      const t = sameText(en[r.index]?.[ce]);
      if (t && sameText(es[r.index]?.[cs]) === t) failures.push({ key: `${rowKey(r)}|untranslated|${cs}`, detail: `${cs} holds the English text of ${ce}` });
    }
  }
  return failures;
}

const D2: Check = {
  id: "D2",
  group: "data",
  title: "English and Spanish parity",
  how: "script",
  run(ctx) {
    const data = rowsFor(ctx);
    if (!data) return blocked("D2", `${ctx.seedDir}/rangos-biomarcadores-es.json`);
    const failures = checkParity(data.rows, data.seed.enCount, data.seed.esCount);
    const reportFile = path.join(ctx.seedDir, "compile-report.json");
    const listed = untranslatedFailures(fs.existsSync(reportFile) ? ctx.load(reportFile) ?? {} : null, fs.existsSync(path.join(ctx.seedDir, "changes.json")));
    const untranslated: Failure[] = [];
    const seen = new Set<string>();
    for (const f of [...listed, ...copiedTextFailures(data.rows, data.seed.en, data.seed.es)]) {
      if (seen.has(f.key)) continue;
      seen.add(f.key);
      untranslated.push(f);
    }
    failures.push(...untranslated);
    return result("D2", failures, `${failures.length} mismatches across ${data.rows.length} row pairs (${untranslated.length} Spanish columns carrying English text: those compile-report.json lists, and the method note, reference source and none-because reason read from both files)`, { rows: data.rows.length, en_rows: data.seed.enCount, es_rows: data.seed.esCount, untranslated: untranslated.length });
  },
};

// ─── D3 laboratory concordance ───

interface Deviation extends Failure {}

export function catalogueFor(catalogue: CatalogueRow[], codeMap: Record<string, string>, key: string, unit: string): CatalogueRow[] {
  const codes = Object.entries(codeMap)
    .filter(([, k]) => k === key)
    .map(([c]) => c);
  return catalogue.filter((c) => codes.includes(c.code) && normalizeUnit(c.unit) === normalizeUnit(unit));
}

function catalogueRowAt(cat: CatalogueRow[], sex: string, age: number, ageGroup: string): CatalogueRow | null {
  const labelled = Object.entries(CONDITION_TO_AGE_GROUP).find(([, g]) => g === ageGroup)?.[0];
  const want = cat.filter((c) => {
    if (c.age_low != null && c.age_high != null && !(age >= c.age_low && age <= c.age_high)) return false;
    if (c.sex !== "both" && c.sex !== sex) return false;
    if (labelled) return c.condition === labelled;
    return !c.condition || !(c.condition in CONDITION_TO_AGE_GROUP);
  });
  if (!want.length) return null;
  // The most specific row wins: the person's sex over "general", no clinical condition over one the map
  // does not know, a narrower age band over a wider one.
  want.sort((a, b) => (a.sex === "both" ? 1 : 0) - (b.sex === "both" ? 1 : 0) || (a.condition ? 1 : 0) - (b.condition ? 1 : 0) || (a.age_high ?? 999) - (a.age_low ?? 0) - ((b.age_high ?? 999) - (b.age_low ?? 0)));
  return want[0];
}

const sameBound = (seed: number | null, lab: number | null, floor: boolean): boolean => {
  if (lab == null) return seed == null || (floor && seed === 0);
  if (seed == null) return false;
  return Math.abs(seed - lab) < 1e-9;
};

export function checkLabConcordance(rows: Row[], catalogue: CatalogueRow[], codeMap: Record<string, string>): { failures: Deviation[]; metrics: Record<string, number> } {
  const failures: Deviation[] = [];
  let mappedRows = 0;
  let exempt = 0;
  let compared = 0;
  const mappedKeys = new Set(Object.values(codeMap));
  for (const r of rows) {
    if (!mappedKeys.has(r.biomarker_key)) continue;
    mappedRows++;
    const k = rowKey(r);
    if (r.reference_basis && /^(decision_limit|population_study)$/.test(r.reference_basis) && r.source) {
      exempt++;
      continue;
    }
    const cat = catalogueFor(catalogue, codeMap, r.biomarker_key, r.unit_en);
    if (!cat.length) {
      failures.push({ key: `${k}|no_catalogue_row`, detail: `no catalogue row for this key in unit "${r.unit_en}"` });
      continue;
    }
    const sexes = r.sex === "both" ? ["male", "female"] : [r.sex];
    const bands = new Map<string, { low: number | null; high: number | null; ages: number[]; line: number }>();
    let uncovered = 0;
    for (const sex of sexes) {
      for (let age = 18; age <= 120; age++) {
        if (!ageGroupContains(r.age_group_en, age)) continue;
        const c = catalogueRowAt(cat, sex, age, r.age_group_en);
        if (!c) {
          uncovered++;
          continue;
        }
        const id = `${sex}|${c.low}|${c.high}|${c.age_raw}|${c.sex_raw}`;
        const b = bands.get(id) ?? { low: c.low, high: c.high, ages: [], line: c.line };
        b.ages.push(age);
        bands.set(id, b);
      }
    }
    if (!bands.size) {
      failures.push({ key: `${k}|no_catalogue_band`, detail: `the catalogue has no band covering this row's ages for ${sexes.join("/")}` });
      continue;
    }
    compared++;
    const distinct = new Map<string, { low: number | null; high: number | null; ages: number[]; line: number }>();
    for (const b of bands.values()) distinct.set(`${b.low}|${b.high}`, b);
    if (distinct.size > 1) {
      const parts = [...bands.values()].map((b) => `${b.low ?? "–"}–${b.high ?? "–"} (ages ${b.ages[0]}-${b.ages[b.ages.length - 1]}, line ${b.line})`).sort();
      failures.push({ key: `${k}|band_split`, detail: `EVA band "${r.age_group_en}" (${r.sex}) spans ${distinct.size} laboratory bands: ${parts.join("; ")}` });
      continue;
    }
    const lab = [...distinct.values()][0];
    const lowOk = sameBound(r.normal_low, lab.low, true);
    const highOk = sameBound(r.normal_high, lab.high, false);
    if (!lowOk || !highOk) {
      failures.push({ key: `${k}|bounds`, detail: `seed reference ${r.normal_low ?? "null"}–${r.normal_high ?? "null"} vs catalogue ${lab.low ?? "none"}–${lab.high ?? "none"} ${r.unit_en} (catalogue line ${lab.line})${r.reference_basis ? `; reference_basis ${r.reference_basis} without a source` : ""}` });
    }
    if (uncovered) failures.push({ key: `${k}|uncovered_ages`, detail: `${uncovered} (sex, age) points of this row have no catalogue band` });
  }
  return { failures, metrics: { mapped_rows: mappedRows, exempt_rows: exempt, compared_rows: compared, deviations: failures.length } };
}

const D3: Check = {
  id: "D3",
  group: "data",
  title: "Laboratory concordance",
  how: "script",
  run(ctx) {
    const data = rowsFor(ctx);
    if (!data) return blocked("D3", `${ctx.seedDir}/biomarker-ranges-en.json`);
    const catalogue = parseCatalogue(ctx.root);
    if (!catalogue) return blocked("D3", CATALOGUE_PATH);
    const codeMap = loadCodeMap(ctx.root);
    if (!codeMap) return blocked("D3", `ECH_CODE_TO_BIOMARKER in ${CODE_MAP_PATH}`);
    const lab = checkLabConcordance(data.rows, catalogue, codeMap);
    // Duplicate seed rows (D1) share a key; count each key once so the summary matches the failure list.
    const failures = dedupe(lab.failures);
    const metrics: Record<string, number> = { ...lab.metrics, deviations: failures.length };
    return result("D3", failures, `${failures.length} unexplained deviations over ${metrics.mapped_rows} Echevarne-mapped rows (${metrics.exempt_rows} exempt by reference_basis)`, { ...metrics, catalogue_rows: catalogue.length, mapped_codes: Object.keys(codeMap).length });
  },
};

// ─── D4 conversions ───

export interface ConversionEntry {
  file: string;
  line: number;
  expression: string;
  factor: number;
  note: string;
  source: string;
  approximation: boolean;
  tested: boolean;
}

const CONVERSION_FILES = ["src/lib/biomarkers/unit-conversions.ts", "src/lib/biomarkers/kdm-adapter.ts", "src/lib/biomarkers/biological-age-v3-adapter.ts", "src/lib/biomarkers/canonical-units.ts"];
const TEST_FILES = ["src/lib/biomarkers/unit-conversions.test.ts", "src/lib/biomarkers/kdm-adapter.test.ts", "src/lib/biomarkers/biological-age-v3-adapter.test.ts"];

export function inventoryConversions(root: string): ConversionEntry[] {
  const tests = TEST_FILES.map((f) => path.resolve(root, f))
    .filter((f) => fs.existsSync(f))
    .map((f) => fs.readFileSync(f, "utf8"))
    .join("\n");
  const out: ConversionEntry[] = [];
  for (const rel of CONVERSION_FILES) {
    const file = path.resolve(root, rel);
    if (!fs.existsSync(file)) continue;
    const lines = fs.readFileSync(file, "utf8").split(/\r?\n/);
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (/^\s*(\/\/|\*|\/\*)/.test(line) || /Math\.round/.test(line)) continue;
      const m = line.match(/value\s*([*/])\s*(\d+(?:\.\d+)?)(?:\s*\+\s*(\d+(?:\.\d+)?))?/) ?? line.match(/^\s*"[^"]+":\s*(\d+(?:\.\d+)?)(?!\d*\s*\/)/);
      let factor: number;
      let expression: string;
      if (m && m.length >= 3 && (m[1] === "*" || m[1] === "/")) {
        factor = m[1] === "*" ? Number(m[2]) : 1 / Number(m[2]);
        expression = `value ${m[1]} ${m[2]}${m[3] ? ` + ${m[3]}` : ""}`;
      } else if (m && rel.endsWith("kdm-adapter.ts")) {
        factor = Number(m[1]);
        expression = line.trim().replace(/,\s*$/, "");
      } else continue;
      if (factor === 1) continue;
      // The note string on the following lines, and the comment above, give the conversion its source.
      const window = lines.slice(i, i + 4).join(" ");
      const note = window.match(/note:\s*[`"]([^`"]+)[`"]/)?.[1] ?? "";
      const above = lines.slice(Math.max(0, i - 4), i).filter((l) => /^\s*(\/\/|\*)/.test(l)).map((l) => l.replace(/^\s*(\/\/|\*)\s?/, "").trim());
      const inline = line.match(/\/\/\s*(.+)$/)?.[1]?.trim() ?? "";
      const source = [...above, inline].filter(Boolean).join(" ");
      const approximation = /approximat|isoform|roughly|not linear|NOT linear/i.test(`${note} ${source}`);
      const literal = m[2] ?? m[1];
      const tested = tests.includes(literal) || (note ? tests.includes(note.split(" via ")[0]) : false);
      out.push({ file: rel, line: i + 1, expression, factor, note, source, approximation, tested });
    }
  }
  return out.sort((a, b) => a.file.localeCompare(b.file) || a.line - b.line);
}

/**
 * Canonical units that name no unit (ruling U-01 (a): the ratios, the indices and the qualitative markers), compared
 * as unitKey compares units. A marker whose canonical unit in the seed under test is one of these may be read
 * without a unit.
 */
export const UNITLESS_UNIT_LABELS: ReadonlySet<string> = new Set(["ratio", "index", "Blood Type", "Pattern", "Pattern A or B", "Positive/Negative", "Titer"].map(unitKey));

/**
 * Ruling U-01 (b): the markers whose number is the same in every unit laboratories report them in, each with the
 * reason. TSH and MCV are on it because the WS3-39 audit of the units table found every unit EVA lists for them
 * numerically equal; the ruling names RDW, MCH, the enzymes, HbA1c and the differential percentages as not on it.
 */
export const SAME_NUMBER_MARKERS: Readonly<Record<string, string>> = {
  sodium: "mmol/L and mEq/L give one number for a monovalent ion",
  potassium: "mmol/L and mEq/L give one number for a monovalent ion",
  chloride: "mmol/L and mEq/L give one number for a monovalent ion",
  tsh: "µIU/mL, mIU/L and mU/L give one number",
  mcv: "fL is the only unit",
};

/** The row gate as the probe calls it: the shape of the app's gateRawBiomarker, narrowed to what the probe reads. */
export type UnitGate = (
  raw: { name: string; value: number; unit: string; biomarkerKey: string; matchConfidence: "exact" },
  options: { trustUnits: boolean },
) => { stored: true; biomarkerKey: string; value: number; unit: string; unitSource?: string | null } | { stored: false; unmatched: { reason?: string } };

/**
 * The ways the probe gives a result with no unit: an empty unit and one of spaces only (the ruling's "empty after
 * trimming"), on an upload or manual entry and on the laboratory feed when its catalogue gives the code no unit.
 */
const NO_UNIT_GIVEN = [false, true].flatMap((trustUnits) =>
  ["", "   "].map((unit) => ({ unit, trustUnits, where: `unit ${JSON.stringify(unit)} ${trustUnits ? "on the laboratory feed, its catalogue giving none" : "on an upload or manual entry"}` })),
);

/**
 * A result given without a unit (ruling U-01, WS3-39). EVA cannot know the unit of a number given without one, so
 * reading it in the marker's own unit is a conversion by a factor of 1 from a unit nobody named: a glucose of 5.5
 * meant in mmol/L becomes 5.5 mg/dL. The app's row gate, given each marker of the seed with no unit, on an upload or
 * manual entry and on the laboratory feed when its catalogue gives the code no unit, must set it aside
 * (unit_missing), except a marker whose canonical unit names no unit (UNITLESS_UNIT_LABELS) or one on the
 * same-number list (SAME_NUMBER_MARKERS); one it reads without a unit keeps its number. A marker that may pass and is
 * set aside is no failure: the ruling lets those pass, it does not require it. One failure per marker, naming the
 * first way it was given that the gate stored.
 */
export function probeUnitless(rows: Row[], gate: UnitGate = gateRawBiomarker): { failures: Failure[]; summary: string; metrics: Record<string, number | string> } {
  const failures: Failure[] = [];
  const keys = byKey(rows.filter((r) => !NON_ANALYTE_KEYS[r.biomarker_key]));
  const mayPass = (key: string) => {
    const list = keys.get(key) ?? [];
    return Object.hasOwn(SAME_NUMBER_MARKERS, key) || (list.length > 0 && list.every((r) => UNITLESS_UNIT_LABELS.has(unitKey(r.unit_en))));
  };
  const passed: string[] = [];
  const count = { setAside: 0, misread: 0, renumbered: 0, threw: 0 };
  for (const key of [...keys.keys()].sort()) {
    const row = keys.get(key)![0];
    const value = [row.normal_high, row.normal_low, row.optimal_high, row.optimal_low].find((v): v is number => typeof v === "number" && v > 0) ?? 1;
    const given = `${row.name_en} ${value} given with no unit`;
    const misread: string[] = [];
    const renumbered: string[] = [];
    let stored = 0;
    let threw: string | null = null;
    for (const way of NO_UNIT_GIVEN) {
      let gated: ReturnType<UnitGate>;
      try {
        gated = gate({ name: row.name_en, value, unit: way.unit, biomarkerKey: key, matchConfidence: "exact" }, { trustUnits: way.trustUnits });
      } catch (e) {
        threw ??= `${way.where}: ${e instanceof Error ? e.message : String(e)}`;
        continue;
      }
      if (!gated.stored) continue;
      stored++;
      const as = `stored as ${gated.value} ${gated.unit.trim() || "(no unit)"}${gated.biomarkerKey !== key ? ` under ${gated.biomarkerKey}` : ""}${gated.unitSource ? `, unit_source ${gated.unitSource}` : ""} (${way.where})`;
      if (!mayPass(gated.biomarkerKey)) misread.push(as);
      else if (gated.value !== value) renumbered.push(as);
    }
    const of = (n: number) => (n > 1 ? `; so on ${n} of the ${NO_UNIT_GIVEN.length} ways the probe gives it` : "");
    if (threw) {
      count.threw++;
      failures.push({ key: `unitless|${key}|error`, detail: `the row gate threw on ${given} (${threw})` });
    }
    if (misread.length) {
      count.misread++;
      failures.push({ key: `unitless|${key}`, detail: `${given} is ${misread[0]}${of(misread.length)}: read in the marker's unit, a unit nobody named; only a marker whose canonical unit names no unit, or one on the same-number list, may be read without one, and the rest are set aside as unit_missing (U-01)` });
    } else if (renumbered.length) {
      count.renumbered++;
      failures.push({ key: `unitless|${key}|value`, detail: `${given} is ${renumbered[0]}${of(renumbered.length)}: a number given without a unit is converted by a factor no unit sources` });
    } else if (stored) passed.push(key);
    else if (!threw) count.setAside++;
  }
  const also = [count.renumbered ? `, ${count.renumbered} given another number` : "", count.threw ? `, ${count.threw} on which the gate threw` : ""].join("");
  return {
    failures,
    summary: `${keys.size} markers given with no unit: ${count.setAside} set aside, ${passed.length} read without one (dimensionless or same-number), ${count.misread} read in a unit nobody named${also}`,
    metrics: {
      unitless_markers: keys.size,
      unitless_set_aside: count.setAside,
      unitless_passed: passed.length,
      unitless_read_in_marker_unit: count.misread,
      unitless_renumbered: count.renumbered,
      unitless_gate_errors: count.threw,
      unitless_passed_keys: passed.join(", "),
    },
  };
}

const D4: Check = {
  id: "D4",
  group: "data",
  title: "Conversions",
  how: "script",
  run(ctx) {
    const entries = inventoryConversions(ctx.root);
    if (!entries.length) return blocked("D4", CONVERSION_FILES[0]);
    const failures: Failure[] = [];
    for (const e of entries) {
      const k = `${e.file}:${e.line}`;
      if (e.approximation) failures.push({ key: `${k}|approximation`, detail: `approximate conversion on the classification path: ${e.expression} (${e.note || e.source}); must be refused as unit_mismatch` });
      if (!e.source && !e.note) failures.push({ key: `${k}|unsourced`, detail: `no source comment for ${e.expression}` });
      if (!e.tested) failures.push({ key: `${k}|untested`, detail: `no unit test mentions ${e.expression}${e.note ? ` (${e.note})` : ""}` });
    }
    const sourced = entries.filter((e) => e.source || e.note).length;
    const tested = entries.filter((e) => e.tested).length;
    const approximations = entries.filter((e) => e.approximation).length;
    // A result given without a unit, through the app's row gate, for each marker of the seed under test.
    const data = rowsFor(ctx);
    const unitless = data ? probeUnitless(data.rows) : null;
    if (unitless) failures.push(...unitless.failures);
    const summary = `${entries.length} conversion factors: ${sourced} sourced, ${tested} tested, ${approximations} approximations; ${unitless ? unitless.summary : "results given with no unit not probed (no seed)"}`;
    const metrics = {
      factors: entries.length,
      sourced,
      tested,
      approximations,
      inventory: entries.map((e) => `${e.file}:${e.line} ${e.expression}${e.note ? ` [${e.note}]` : ""}`).join("\n"),
      ...(unitless?.metrics ?? {}),
    };
    // As G1: any failure fails D4; otherwise the probe that could not run blocks it.
    if (!unitless && !failures.length) return { id: "D4", status: "blocked", summary, failures: [], blocked_on: `${ctx.seedDir}/biomarker-ranges-en.json`, metrics };
    return result("D4", failures, summary, metrics);
  },
};

// ─── D5 one source of truth ───

/**
 * A production row as D5 compares it. The snapshot has no critical-limit columns and no migration after it adds them,
 * so production's critical_low and critical_high are null; the compile's forward migration adds the columns
 * (compile-sql.js buildSql) and writes the values.
 */
interface ProdRow {
  biomarker_key: string;
  sex: string;
  age_group_en: string;
  unit_en: string;
  normal_low: number | null;
  normal_high: number | null;
  optimal_low: number | null;
  optimal_high: number | null;
  critical_low: number | null;
  critical_high: number | null;
}

export const PRODUCTION_SNAPSHOT = "docs/biomarker-evidence/snapshots/production-biomarker_references-2026-09-25-gate1.json";
/** Migrations applied to production after the gate1 snapshot was taken, in APPLIED.md order. */
export const MIGRATIONS_AFTER_SNAPSHOT = [
  "supabase/migrations/20260925010000_gate1_thresholds_1.sql",
  "supabase/migrations/20260925010100_gate1_thresholds_2.sql",
  "supabase/migrations/20260925012000_nlr_row.sql",
  "supabase/migrations/20260925012100_nlr_name_en.sql",
  "supabase/migrations/20260925013000_in_range_messages_1.sql",
  "supabase/migrations/20260925013100_in_range_messages_2.sql",
  "supabase/migrations/20260925013200_in_range_messages_3.sql",
];

function sqlValue(raw: string): string | number | null {
  const s = raw.trim();
  if (/^null$/i.test(s)) return null;
  if (/^-?\d+(\.\d+)?$/.test(s)) return Number(s);
  if (/^'[\s\S]*'$/.test(s)) return s.slice(1, -1).replace(/''/g, "'");
  if (/^(true|false)$/i.test(s)) return s.toLowerCase();
  return s;
}

/** Split a SQL tuple body on commas outside quotes. */
function splitTuple(body: string): string[] {
  const out: string[] = [];
  let cur = "";
  let q = false;
  for (let i = 0; i < body.length; i++) {
    const ch = body[i];
    if (ch === "'") {
      if (q && body[i + 1] === "'") {
        cur += "''";
        i++;
        continue;
      }
      q = !q;
    }
    if (ch === "," && !q) {
      out.push(cur);
      cur = "";
    } else cur += ch;
  }
  out.push(cur);
  return out;
}

const BOUND_COLS = ["normal_low", "normal_high", "optimal_low", "optimal_high"] as const;
/** The critical limits: columns the compile's forward migration adds and writes (compile-rows.js EXT, DB_EXT_TYPES numeric). */
const CRITICAL_COLS = ["critical_low", "critical_high"] as const;
/**
 * The columns the compile's forward migration adds, each with the exact type it writes (compile-rows.js DB_EXT_TYPES;
 * a test keeps the two equal). D5 reads an ALTER TABLE only when every clause adds one of these with exactly this type
 * and nothing after it, so no clause can carry a default, a constraint, a foreign key (ON DELETE CASCADE could remove
 * rows the file writes), a generated expression or a collation.
 */
export const SIGNOFF_ADD_COLUMNS: Readonly<Record<string, string>> = {
  critical_low: "numeric",
  critical_high: "numeric",
  critical_none_reason: "text",
  marker_class: "text",
  reference_basis: "text",
  reference_source: "text",
  physiological_state: "text",
  method_note: "text",
  explanatory_numbers: "numeric[]",
};

/**
 * The statements of a SQL file: split on semicolons outside single-quoted strings, with `--` comments outside
 * strings removed, each up to the next line feed or carriage return, which is where PostgreSQL ends one (scan.l and
 * psqlscan.l of PostgreSQL 16: newline [\n\r], non_newline [^\n\r], comment ("--"{non_newline}*)); the comment and
 * the character that ends it become one line feed. A text value may hold a semicolon (the NLR insert's notes do), so
 * a plain split on ";" cuts the statement and its insert is never applied.
 */
export function splitSqlStatements(sql: string): string[] {
  const out: string[] = [];
  let cur = "";
  let quoted = false;
  for (let i = 0; i < sql.length; i++) {
    const ch = sql[i];
    if (!quoted && ch === "-" && sql[i + 1] === "-") {
      while (i < sql.length && sql[i] !== "\n" && sql[i] !== "\r") i++;
      cur += "\n";
      continue;
    }
    if (ch === "'") {
      if (quoted && sql[i + 1] === "'") {
        cur += "''";
        i++;
        continue;
      }
      quoted = !quoted;
    }
    if (ch === ";" && !quoted) {
      out.push(cur);
      cur = "";
      continue;
    }
    cur += ch;
  }
  out.push(cur);
  return out.filter((s) => s.trim());
}

/** Apply the bound-changing statements of a migration to the snapshot rows (inserts, deletes, bound updates). */
export function applyMigrationBounds(rows: ProdRow[], sql: string): { rows: ProdRow[]; applied: number } {
  let applied = 0;
  const out = rows.map((r) => ({ ...r }));
  const statements = splitSqlStatements(sql);
  for (const st of statements) {
    const s = st.replace(/\s+/g, " ").trim();
    let m: RegExpMatchArray | null;
    if ((m = s.match(/^insert into public\.biomarker_references \(([^)]+)\) values \((.+)\)(?: on conflict .*)?$/i))) {
      const cols = m[1].split(",").map((c) => c.trim());
      const vals = splitTuple(m[2]).map(sqlValue);
      const rec: Record<string, unknown> = {};
      cols.forEach((c, i) => (rec[c] = vals[i]));
      const exists = out.some((r) => r.biomarker_key === rec.biomarker_key && r.sex === rec.sex && r.age_group_en === rec.age_group_en);
      if (!exists) {
        out.push({
          biomarker_key: String(rec.biomarker_key),
          sex: String(rec.sex),
          age_group_en: String(rec.age_group_en),
          unit_en: String(rec.unit_en ?? ""),
          normal_low: (rec.normal_low as number | null) ?? null,
          normal_high: (rec.normal_high as number | null) ?? null,
          optimal_low: (rec.optimal_low as number | null) ?? null,
          optimal_high: (rec.optimal_high as number | null) ?? null,
          // Production has no critical-limit columns, so no migration applied to it writes one.
          critical_low: null,
          critical_high: null,
        });
        applied++;
      }
    } else if ((m = s.match(/^delete from public\.biomarker_references where biomarker_key = '([^']+)'(?: and sex = '([^']+)')?(?: and age_group_en = '([^']+)')?$/i))) {
      const before = out.length;
      for (let i = out.length - 1; i >= 0; i--) {
        const r = out[i];
        if (r.biomarker_key === m[1] && (!m[2] || r.sex === m[2]) && (!m[3] || r.age_group_en === m[3])) out.splice(i, 1);
      }
      applied += before - out.length;
    } else if ((m = s.match(/^update public\.biomarker_references set (.+?) where biomarker_key = '([^']+)' and sex = '([^']+)' and age_group_en = '([^']+)'/i))) {
      const sets = splitTuple(m[1]).map((p) => p.split("=").map((x) => x.trim()));
      const target = out.find((r) => r.biomarker_key === m![2] && r.sex === m![3] && r.age_group_en === m![4]);
      if (!target) continue;
      for (const [col, val] of sets) {
        if ((BOUND_COLS as readonly string[]).includes(col)) {
          (target as unknown as Record<string, unknown>)[col] = sqlValue(val);
          applied++;
        }
      }
    }
  }
  return { rows: out, applied };
}

// The documented pack changes. docs/signoff/tools/compile.js writes them as a set. In its output directory, next to the
// seed files it compiled: changes.json ({changes: [{row_key, op, field, from, to, reason, evidence_ids, reason_source,
// …}], production_only: [rows kept, not changes]}) and the forward migration migration.sql. With --reconciliation-dir,
// the files D6 reads: diff.json ({rows: [{key, ops, fields, reason, unexplained_fields, source, …}]}) and forward.sql.
// Both change lists key rows by the database key biomarker_key|sex|age_group_en; field "row" is an added or removed
// row, any other field a database column. The change list gives each difference its reason and source; the forward
// migration gives its documented value: production with the forward migration applied is what the seed must hold.
// Every difference between the seed and production, on every column, must be a change the list records with the
// seed's value (checkSourceOfTruth for the bounds, critical limits and unit, which also asks a stated reason and
// source; checkDifferencesListed for every other column), and every change the list records must be one the forward
// migration makes (checkChangeList).

/** One documented change: a row and field with its reason and source; from/to when the list records them. */
export interface DocumentedChange {
  row_key: string;
  op: string;
  field: string;
  reason: string | null;
  source: string | null;
  values: { from: unknown; to: unknown } | null;
}

/** A statement of a forward migration that D5 reads: an upsert (its rows, and the columns it sets on conflict) or a delete. */
export type MigrationOp = { kind: "upsert"; rows: Record<string, unknown>[]; update: string[] } | { kind: "delete"; keys: string[] };

/**
 * A forward migration as D5 reads it. unreadable lists what D5 cannot read, each with the reason: a statement other
 * than the ones it reads, whether or not it names biomarker_references; a statement that undoes the file's writes; a
 * transaction the file opens and does not commit; or a place sqlSplitHazards lists, where PostgreSQL or psql may read
 * the file otherwise than D5 does (parseForwardMigration). One entry is enough for D5 to take no value from the file.
 */
export interface ForwardMigration {
  file: string;
  ops: MigrationOp[];
  unreadable: string[];
}

export interface DocumentedChanges {
  file: string;
  kind: "changes.json" | "reconciliation diff";
  changes: DocumentedChange[];
  /** The forward migration the compile wrote with the change list; null or absent when there is none. */
  migration?: ForwardMigration | null;
}

/**
 * Words that stand for a missing reason or source wherever they appear; compile.js prints a change without a reason as
 * "**unexplained**". The compile's former stock sentence for a removed row, "not in the family's decision final_rows",
 * is one too (decision CEO-11: a removal is explained only by the decision's own record of it); it is matched on the
 * normalised text of isStated, where the apostrophe and the underscore are spaces.
 */
const PLACEHOLDER_ANYWHERE = /\b(?:unexplained|todo|tbd|tbc|fixme|xxx+|placeholder|lorem ipsum)\b|replace with the reason|not in the family.s decision final.rows/i;
/** Words that stand for a missing reason or source when the text begins with them ("None yet", "N/A (see decision)", "unknown source", "To be confirmed"). */
const PLACEHOLDER_START =
  /^(?:n\/a|n\.a|none|nil|null|undefined|unknown|missing|pending|empty|not (?:yet )?(?:known|given|stated|documented|explained|available|applicable)|to be (?:confirmed|determined|decided|defined|added|completed|provided|written)|no (?:reason|source)|see (?:above|below)|same as above|-+|–|—|\?+)(?![\p{L}\p{N}])/iu;

/**
 * A reason or source counts only when it is a text with a word or number of at least two characters that is not a
 * placeholder: "unexplained", TODO, TBD, TBC, FIXME, "xxx", the reasons template text or the compile's former sentence
 * for a removed row anywhere in it, or a text that
 * begins with n/a, none, null, unknown, missing, pending, "not applicable", "to be confirmed", "-" or "?" (and the
 * like in PLACEHOLDER_START), or is "na".
 * A real reason that begins with one of those words ("None of the cohorts …") counts as missing too and must be
 * worded otherwise: the rule errs on the strict side.
 */
export function isStated(text: unknown): boolean {
  if (typeof text !== "string") return false;
  const t = text
    .replace(/[*_`"'()[\]{}<>]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/[.:;,!\s]+$/, "")
    .trim();
  if (!/[\p{L}\p{N}]{2}/u.test(t)) return false;
  if (PLACEHOLDER_ANYWHERE.test(t) || PLACEHOLDER_START.test(t)) return false;
  return !/^n\.?a$/i.test(t);
}

const asText = (v: unknown): string | null => (typeof v === "string" && v.trim() ? v : null);
const isRecord = (v: unknown): v is Record<string, unknown> => !!v && typeof v === "object" && !Array.isArray(v);

/**
 * The change list of compile.js changes.json. A change's source is the documented_source the entry carries when the
 * compile writes one, else its evidence ids, else the document its reason came from (reason_source: the decision, the
 * verify file or the reconciliation reasons), as compile.js builds the reconciliation diff's source from the same
 * entries. Null when the document has no change list.
 */
export function changesFromCompile(doc: unknown): DocumentedChange[] | null {
  if (!isRecord(doc) || !Array.isArray(doc.changes)) return null;
  return doc.changes.filter(isRecord).map((c) => {
    const ev = Array.isArray(c.evidence_ids) ? c.evidence_ids.map((x) => asText(x)).filter((x): x is string => !!x) : [];
    return {
      row_key: String(c.row_key ?? ""),
      op: String(c.op ?? ""),
      field: String(c.field ?? ""),
      reason: asText(c.reason),
      source: asText(c.documented_source) ?? (ev.length ? ev.join(", ") : asText(c.reason_source)),
      values: { from: c.from ?? null, to: c.to ?? null },
    };
  });
}

/**
 * The change list of the reconciliation diff (compile.js diff.json). A row that carries a changes[] list (one entry per
 * field with its op, from, to, reason and source) gives one change per entry with its values; otherwise the row gives
 * one change per listed field, with the row's reason and source and no values. A field in unexplained_fields has no
 * reason either way.
 */
export function changesFromDiff(doc: unknown): DocumentedChange[] | null {
  if (!isRecord(doc) || !Array.isArray(doc.rows)) return null;
  const out: DocumentedChange[] = [];
  for (const r of doc.rows.filter(isRecord)) {
    const ops = Array.isArray(r.ops) ? r.ops.map(String) : [];
    const unexplained = new Set(Array.isArray(r.unexplained_fields) ? r.unexplained_fields.map(String) : []);
    if (Array.isArray(r.changes)) {
      for (const c of r.changes.filter(isRecord)) {
        const field = String(c.field ?? "");
        out.push({ row_key: String(r.key ?? ""), op: String(c.op ?? ""), field, reason: unexplained.has(field) ? null : asText(c.reason), source: asText(c.source), values: { from: c.from ?? null, to: c.to ?? null } });
      }
      continue;
    }
    for (const field of Array.isArray(r.fields) ? r.fields.map(String) : []) {
      const op = field === "row" ? (ops.includes("add") ? "add" : ops.includes("remove") ? "remove" : "") : "modify";
      out.push({ row_key: String(r.key ?? ""), op, field, reason: unexplained.has(field) ? null : asText(r.reason), source: asText(r.source), values: null });
    }
  }
  return out;
}

/** Split a SQL list on commas outside quoted text, parentheses and brackets (array[1, 2] is one item). */
export function splitSqlList(body: string): string[] {
  const out: string[] = [];
  let cur = "";
  let quoted = false;
  let depth = 0;
  for (let i = 0; i < body.length; i++) {
    const ch = body[i];
    if (quoted) {
      cur += ch;
      if (ch === "'") {
        if (body[i + 1] === "'") {
          cur += "'";
          i++;
        } else quoted = false;
      }
      continue;
    }
    if (ch === "'") quoted = true;
    else if (ch === "(" || ch === "[") depth++;
    else if (ch === ")" || ch === "]") depth--;
    else if (ch === "," && depth === 0) {
      out.push(cur.trim());
      cur = "";
      continue;
    }
    cur += ch;
  }
  out.push(cur.trim());
  return out;
}

/** A SQL literal as compile-sql.js lit() writes it: null, a number, a quoted text, true/false, array[…]::numeric[]. Undefined for anything else. */
export function sqlLiteral(raw: string): unknown {
  const s = raw.trim();
  if (/^null$/i.test(s)) return null;
  if (/^'(?:[^']|'')*'$/.test(s)) return s.slice(1, -1).replace(/''/g, "'");
  if (/^(?:true|false)$/i.test(s)) return /^true$/i.test(s);
  const arr = s.match(/^array\s*\[([^[\]]*)\]\s*(?:::\s*[a-z_ ]+\[\])?$/i);
  if (arr) {
    const items = arr[1].trim() ? splitSqlList(arr[1]).map(sqlLiteral) : [];
    return items.some((x) => x === undefined) ? undefined : items;
  }
  if (/^[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[-+]?\d+)?$/i.test(s)) return Number(s);
  return undefined;
}

/**
 * The parenthesised tuples of a VALUES list that starts at index start of s, without their parentheses, and the index
 * after the list: -1 when a tuple is unbalanced or a comma is not followed by another tuple.
 */
function readValuesList(s: string, start: number): { tuples: string[]; end: number } {
  const tuples: string[] = [];
  let i = start;
  const skip = () => {
    while (i < s.length && /\s/.test(s[i])) i++;
  };
  for (;;) {
    skip();
    if (s[i] !== "(") return { tuples, end: tuples.length ? -1 : i };
    const open = i + 1;
    let depth = 0;
    let quoted = false;
    for (; i < s.length; i++) {
      const ch = s[i];
      if (quoted) {
        if (ch === "'") {
          if (s[i + 1] === "'") i++;
          else quoted = false;
        }
        continue;
      }
      if (ch === "'") quoted = true;
      else if (ch === "(" || ch === "[") depth++;
      else if ((ch === ")" || ch === "]") && --depth === 0) break;
    }
    if (i >= s.length) return { tuples, end: -1 };
    tuples.push(s.slice(open, i));
    i++;
    skip();
    if (s[i] !== ",") return { tuples, end: i };
    i++;
  }
}

const KEY_COLS = ["biomarker_key", "sex", "age_group_en"];
/** The columns D5 compares: the four bounds, the two critical limits and the unit (the seed's six bounds, as D2 and G2). */
const COMPARED = [...BOUND_COLS, ...CRITICAL_COLS, "unit_en"] as const;
type ComparedField = (typeof COMPARED)[number];
const isCritical = (c: string): boolean => (CRITICAL_COLS as readonly string[]).includes(c);
/** The compared columns that hold numbers: the four bounds and the two critical limits. */
const isNumericCompared = (c: string): boolean => (BOUND_COLS as readonly string[]).includes(c) || isCritical(c);

/**
 * An unquoted SQL name, [a-z_][a-z0-9_]* in either case, returned in lower case as PostgreSQL folds an unquoted name.
 * Null for anything else: a double-quoted name (which PostgreSQL keeps as written), a qualified name, a subscript or a
 * comment.
 */
const plainName = (raw: string): string | null => {
  const t = raw.trim();
  return /^[a-z_][a-z0-9_]*$/i.test(t) ? t.toLowerCase() : null;
};

/** What a literal read by sqlLiteral is, for an unreadable entry. */
const literalKind = (v: unknown): string =>
  v === null
    ? "null"
    : typeof v === "string"
      ? "a quoted text"
      : typeof v === "boolean"
        ? "a boolean"
        : Array.isArray(v)
          ? "an array"
          : typeof v === "number"
            ? Number.isFinite(v)
              ? "a number"
              : "a number beyond the range of a double"
            : "another value";

/**
 * Why D5 cannot take the value of column c from the literal v of an INSERT, or null when it can. PostgreSQL coerces
 * every VALUES entry to the type of its column, so '15' written to a numeric column stores 15 and 1.50 written to a
 * text column stores '1.50'. D5 takes a bound or critical limit only from a finite number or null, the unit only from
 * a quoted text or null, and a key column only from a quoted text.
 */
function valueWhy(c: string, v: unknown): string | null {
  if (isNumericCompared(c)) return v === null || (typeof v === "number" && Number.isFinite(v)) ? null : `${c} is ${literalKind(v)}, not a finite number or null`;
  if (c === "unit_en") return v === null || typeof v === "string" ? null : `unit_en is ${literalKind(v)}, not a quoted text or null`;
  if (KEY_COLS.includes(c)) return typeof v === "string" ? null : `${c} is ${literalKind(v)}, not a quoted text`;
  return null;
}

/**
 * The places this function lists in a SQL file, where PostgreSQL or psql may read the file otherwise than D5 does.
 * splitSqlStatements knows only single-quoted texts and -- comments (each ending at a line feed or a carriage return,
 * as in PostgreSQL) and cuts at every other semicolon; D5's patterns take \s for white space. Listed outside quoted
 * texts and comments: a block comment; a dollar sign (a dollar-quoted text such as $$…$$ starts with one); a
 * double-quoted name; a colon other than the two of a :: cast (psql puts in place of :name, :'name' and :"name" the
 * value of a variable when one of that name is set, a value from outside the file); a character beyond ASCII
 * (PostgreSQL reads it as a letter of a name, D5's patterns read some, such as a no-break space, as white space); a
 * semicolon inside parentheses; and a semicolon between BEGIN ATOMIC and its END. Listed anywhere, inside quoted texts
 * and comments too: a backslash, which PostgreSQL reads as an escape in an E'' text and in every quoted text when
 * standard_conforming_strings is off; and a control character other than a line feed or a tab, among them a carriage
 * return (PostgreSQL ends a -- comment there and counts it as a line break between quoted texts it joins), a NUL (psql
 * reads no more of its line) and a vertical tab (white space to D5's patterns, not to PostgreSQL). PostgreSQL runs no
 * statement written inside a block comment or a dollar-quoted text, yet the splitter would hand it to the reader as a
 * statement; a quote the splitter reads otherwise could hide a statement that runs. Statements separated by semicolons
 * inside parentheses (a rule's action list, DO ALSO ( command ; command … )) or between BEGIN ATOMIC and END (the body
 * of a LANGUAGE SQL function or procedure) are parts of the one CREATE statement around them: PostgreSQL defines them
 * when it applies the file and runs them only when the rule's event occurs or the routine is called. Inside BEGIN
 * ATOMIC each CASE has its own END, so the END that closes the body is found by counting them. Each kind is listed
 * once, with the line (counted in line feeds) where it first occurs; [] when there is none. D5 refuses what this
 * function lists; what it does not list is not shown to be read alike (parseForwardMigration says what D5 reads).
 */
export function sqlSplitHazards(sql: string): string[] {
  const first = new Map<string, number>();
  let line = 1;
  const note = (what: string) => {
    if (!first.has(what)) first.set(what, line);
  };
  // A control character other than a line feed or a tab (U+0000 to U+001F and U+007F), named for its entry; null for
  // any other character.
  const control = (c: string): string | null => {
    const code = c.charCodeAt(0);
    if ((code >= 0x20 && code !== 0x7f) || c === "\n" || c === "\t") return null;
    return c === "\r" ? "a carriage return" : `a control character (U+${code.toString(16).toUpperCase().padStart(4, "0")})`;
  };
  // A character of an unquoted name, key word or number: a letter, digit, underscore or dollar sign, or any character
  // beyond ASCII, kept in the word as a letter of a name.
  const nameChar = (c: string | undefined): boolean => c !== undefined && (/[a-z0-9_$]/i.test(c) || c.charCodeAt(0) > 127);
  let quoted = false;
  let parens = 0;
  // The BEGIN ATOMIC bodies open at this point, plus the CASE expressions open inside them: each closes with an END.
  let atomic = 0;
  // The last word read; white space and -- comments between two words keep it, anything else clears it.
  let lastWord = "";
  for (let i = 0; i < sql.length; i++) {
    const ch = sql[i];
    const ctl = control(ch);
    if (ctl) note(ctl);
    if (ch === "\n") {
      line++;
      continue;
    }
    if (ch === "\\") note("a backslash");
    if (quoted) {
      if (ch === "'") {
        if (sql[i + 1] === "'") i++;
        else quoted = false;
      }
      continue;
    }
    if (ch === "-" && sql[i + 1] === "-") {
      // The comment ends before a line feed or a carriage return, as PostgreSQL ends it (non_newline [^\n\r]).
      while (i + 1 < sql.length && sql[i + 1] !== "\n" && sql[i + 1] !== "\r") {
        i++;
        if (sql[i] === "\\") note("a backslash");
        const c = control(sql[i]);
        if (c) note(c);
      }
      continue;
    }
    // White space: space, tab, and the carriage return, form feed and vertical tab listed above (a line feed is counted
    // above). A no-break space or any other character beyond ASCII is no white space here but part of a word (nameChar).
    if (/[ \t\r\f\v]/.test(ch)) continue;
    if (ch !== "$" && nameChar(ch)) {
      let j = i;
      while (j < sql.length && nameChar(sql[j])) j++;
      const word = sql.slice(i, j).toLowerCase();
      if (word.includes("$")) note("a dollar sign (dollar-quoted text)");
      // nameChar admits only these ASCII characters, so anything else in the word as written is beyond ASCII (tested
      // before lower-casing: the Kelvin sign U+212A lower-cases to k).
      if (/[^a-z0-9_$]/i.test(sql.slice(i, j))) note("a character beyond ASCII outside quoted texts and comments");
      if (word === "atomic" && lastWord === "begin") atomic++;
      else if (atomic > 0 && word === "case") atomic++;
      else if (atomic > 0 && word === "end") atomic--;
      lastWord = word;
      i = j - 1;
      continue;
    }
    lastWord = "";
    if (ch === "'") quoted = true;
    else if (ch === "/" && sql[i + 1] === "*") note("a block comment");
    else if (ch === "$") note("a dollar sign (dollar-quoted text)");
    else if (ch === '"') note("a double-quoted name");
    else if (ch === ":") {
      if (sql[i + 1] === ":") i++;
      else note("a colon outside a :: cast (psql variable)");
    } else if (ch === "(") parens++;
    else if (ch === ")") parens = Math.max(0, parens - 1);
    else if (ch === ";") {
      if (parens > 0) note("a semicolon inside parentheses");
      else if (atomic > 0) note("a semicolon between BEGIN ATOMIC and END");
    }
  }
  return [...first].map(([what, at]) => `${what} at line ${at}`);
}

/**
 * The statements of a forward migration as compile-sql.js buildSql writes them: ALTER TABLE public.biomarker_references
 * … ADD COLUMN for the sign-off columns; INSERT INTO public.biomarker_references (columns) VALUES (…), … ON CONFLICT
 * (biomarker_key, sex, age_group_en) DO UPDATE SET c = excluded.c, … (or DO NOTHING); and DELETE FROM
 * public.biomarker_references r USING (VALUES …) AS v(biomarker_key, sex, age_group_en) WHERE the three key columns are
 * equal. What D5 reads: values only from a file in which every statement is one of these three forms, under the rules
 * below, or a bare BEGIN, START TRANSACTION or COMMIT, and in which sqlSplitHazards lists nothing. None of these
 * statements can hold another one: a semicolon in them outside a quoted text would end the statement or be listed by
 * sqlSplitHazards. What D5 refuses: every other statement, whether or not it names biomarker_references (among them
 * CREATE FUNCTION, PROCEDURE or RULE, whose body or action list PostgreSQL runs when the routine is called or the
 * rule's event occurs, and CALL, DO, a query and a write to another table), and every place sqlSplitHazards lists. It
 * lists each in unreadable and takes no value from the file. In a file D5 reads, the lexers of PostgreSQL 16 (the
 * server's scan.l, psql's psqlscan.l) take the same characters as splitSqlStatements for comments and quoted texts, and
 * the semicolons where it cuts are the ones that end statements for the server and for psql: none lies inside
 * parentheses or a BEGIN ATOMIC body, and no statement is a CREATE FUNCTION or PROCEDURE, inside which psql keeps a
 * BEGIN … END block together. These rules decide what D5 reads; they are not a proof that PostgreSQL writes what D5
 * reads. D5 does not check what PostgreSQL would reject when the file is applied (an unknown column, a value of the
 * wrong type in a column D5 does not compare, a constraint), nor writes the file does not show: a trigger or rule on the
 * table defined outside the file, or a function defined outside it that a column default or a cast in a statement D5
 * reads calls. Nor does it check how a client other than psql cuts the file into statements, psql run with -S
 * (single-line mode, where a line break ends a statement), or a session whose client encoding is not UTF-8, the
 * encoding in which D5 reads the file.
 * - The file: a place sqlSplitHazards lists is unreadable: outside quoted texts and comments, a block comment, a dollar
 *   sign, a double quote, a colon other than the two of a :: cast, a character beyond ASCII, or a semicolon inside
 *   parentheses or between BEGIN ATOMIC and END; anywhere, a backslash or a control character other than a line feed or
 *   a tab (a carriage return among them).
 * - Transactions: BEGIN, BEGIN WORK, BEGIN TRANSACTION, START TRANSACTION, COMMIT, COMMIT WORK and COMMIT TRANSACTION
 *   are read, with no transaction mode and no AND CHAIN. A BEGIN or START TRANSACTION that no later COMMIT of the file
 *   closes, and a ROLLBACK, ABORT or PREPARE TRANSACTION, which leave writes of the file unapplied, are unreadable. END,
 *   which PostgreSQL also takes as COMMIT, is not read: in a BEGIN ATOMIC body it closes the body.
 * - The table: a statement is read only in one of the three forms above, with the table written
 *   public.biomarker_references (an unqualified name depends on the search path).
 * - ALTER: every clause is "add column [if not exists] <column> <type>" for one of the nine sign-off columns with
 *   exactly the type the compile writes (SIGNOFF_ADD_COLUMNS, compile-rows.js DB_EXT_TYPES) and nothing after the
 *   type, so no key column, bound or unit is added (production has them) and every existing row holds null in an
 *   added column, as production does; a default or any other clause could write a value D5 would not see.
 * - INSERT: every column-list entry is a distinct unquoted name (plainName; a double-quoted name is unreadable, even
 *   where PostgreSQL would take it as the same column). Every value is a literal sqlLiteral reads, and valueWhy
 *   accepts it for its column: PostgreSQL coerces '15' to 15 in a numeric column, which D5 would not see. Every DO
 *   UPDATE SET column is named once and is in the column list: PostgreSQL sets a column the list leaves out to the
 *   excluded row's value, the column's default, not to the row's own value. An INSERT that proposes a key twice is
 *   unreadable (under DO UPDATE PostgreSQL raises a cardinality violation). Production has no critical-limit column,
 *   so an INSERT that writes one before an ALTER of the file has added it cannot run.
 * - DELETE: the VALUES alias differs from the table's alias, its columns are distinct unquoted names, and every VALUES
 *   entry is a quoted text.
 */
export function parseForwardMigration(sql: string, file: string): ForwardMigration {
  const ops: MigrationOp[] = [];
  const unreadable: string[] = sqlSplitHazards(sql).map((h) => `file (${h}): PostgreSQL or psql may read the file otherwise than D5 does`);
  const addedCritical = new Set<string>();
  // The unreadable entry of a BEGIN or START TRANSACTION that no COMMIT has closed yet.
  const transaction: { open: string | null } = { open: null };
  splitSqlStatements(sql).forEach((st, n) => {
    const s = st.trim();
    const entry = (why: string) => `statement ${n + 1} (${why}): ${s.replace(/\s+/g, " ").slice(0, 100)}`;
    const bad = (why: string) => {
      unreadable.push(entry(why));
    };
    if (/^(?:rollback|abort)\b|^prepare\s+transaction\b/i.test(s)) return bad("leaves the writes before it unapplied");
    if (/^(?:begin(?:\s+(?:work|transaction))?|start\s+transaction)$/i.test(s)) {
      transaction.open ??= entry("opens a transaction that no later COMMIT of the file closes, so the file does not commit the writes after it");
      return;
    }
    if (/^commit(?:\s+(?:work|transaction))?$/i.test(s)) {
      transaction.open = null;
      return;
    }
    if (/^create\s+(?:or\s+replace\s+)?(?:function|procedure|rule)\b/i.test(s)) return bad("a CREATE FUNCTION, PROCEDURE or RULE: PostgreSQL runs the statements of its body or action list when the routine is called or the rule's event occurs, not when it applies the file");
    const alter = s.match(/^alter\s+table\s+public\.biomarker_references\s+([\s\S]+)$/i);
    if (alter) {
      const clauses = splitSqlList(alter[1]).map((c) => c.match(/^add\s+column\s+(?:if\s+not\s+exists\s+)?([a-z_][a-z0-9_]*)\s+([\s\S]+)$/i));
      const readable = clauses.every((c) => {
        if (!c) return false;
        const col = c[1].toLowerCase();
        return Object.prototype.hasOwnProperty.call(SIGNOFF_ADD_COLUMNS, col) && SIGNOFF_ADD_COLUMNS[col] === c[2].trim().toLowerCase();
      });
      if (!readable) return bad("an ALTER clause other than ADD COLUMN [IF NOT EXISTS] of a sign-off column with exactly the type the compile writes and nothing after it (no default, constraint, foreign key, generated expression or collation)");
      for (const c of clauses) if (c && isCritical(c[1].toLowerCase())) addedCritical.add(c[1].toLowerCase());
      return;
    }
    let m = s.match(/^insert\s+into\s+public\.biomarker_references\s*\(([^)]*)\)\s*values\s*/i);
    if (m) {
      const named = m[1].split(",").map(plainName);
      const odd = m[1].split(",").find((c, i) => !named[i]);
      if (odd !== undefined) return bad(`the column-list entry ${odd.trim() || "(empty)"} is not an unquoted name`);
      const cols = named as string[];
      if (new Set(cols).size !== cols.length) return bad("the column list names a column twice");
      if (!KEY_COLS.every((c) => cols.includes(c))) return bad("the column list lacks a key column");
      if (cols.some((c) => isCritical(c) && !addedCritical.has(c))) return bad("writes a critical-limit column before the file adds it");
      const { tuples, end } = readValuesList(s, m[0].length);
      const conflict = end < 0 ? null : s.slice(end).trim().match(/^on\s+conflict\s*\(\s*biomarker_key\s*,\s*sex\s*,\s*age_group_en\s*\)\s*do\s+(?:nothing|update\s+set\s+([\s\S]+))$/i);
      if (!conflict || !tuples.length) return bad("not VALUES (…), … ON CONFLICT (biomarker_key, sex, age_group_en) DO NOTHING or DO UPDATE SET");
      const doUpdate = conflict[1] !== undefined;
      const sets = doUpdate ? splitSqlList(conflict[1]).map((x) => x.match(/^([a-z_][a-z0-9_]*)\s*=\s*excluded\.([a-z_][a-z0-9_]*)$/i)) : [];
      if (sets.some((x) => !x || x[1].toLowerCase() !== x[2].toLowerCase())) return bad("a DO UPDATE SET item is not c = excluded.c");
      const update = sets.map((x) => x![1].toLowerCase());
      const unlisted = update.find((c) => !cols.includes(c));
      if (unlisted) return bad(`DO UPDATE SET names ${unlisted}, which the column list leaves out: PostgreSQL would write its default`);
      if (new Set(update).size !== update.length) return bad("DO UPDATE SET names a column twice");
      const rows: Record<string, unknown>[] = [];
      const proposed = new Set<string>();
      for (const t of tuples) {
        const vals = splitSqlList(t).map(sqlLiteral);
        if (vals.length !== cols.length) return bad("a row has another number of values than the column list");
        if (vals.some((v) => v === undefined)) return bad("a value is not a literal D5 reads");
        const rec = Object.fromEntries(cols.map((c, i) => [c, vals[i]]));
        const why = cols.map((c) => valueWhy(c, rec[c])).find((w) => w);
        if (why) return bad(why);
        const k = `${rec.biomarker_key}|${rec.sex}|${rec.age_group_en}`;
        if (proposed.has(k)) return bad(`the statement proposes ${k} twice`);
        proposed.add(k);
        rows.push(rec);
      }
      ops.push({ kind: "upsert", rows, update });
      return;
    }
    m = s.match(/^delete\s+from\s+public\.biomarker_references\s+([a-z_][a-z0-9_]*)\s+using\s*\(\s*values\s*/i);
    if (m) {
      const alias = m[1].toLowerCase();
      const { tuples, end } = readValuesList(s, m[0].length);
      const tail = end < 0 ? null : s.slice(end).trim().match(/^\)\s*as\s+([a-z_][a-z0-9_]*)\s*\(([^)]*)\)\s*where\s+([\s\S]+)$/i);
      if (!tail || !tuples.length) return bad("not DELETE … USING (VALUES (…), …) AS v(…) WHERE …");
      const v = tail[1].toLowerCase();
      const named = tail[2].split(",").map(plainName);
      if (v === alias || named.some((c) => !c) || new Set(named).size !== named.length) return bad("the VALUES alias is the table's alias, or its columns are not distinct unquoted names");
      const vcols = named as string[];
      const conds = tail[3].split(/\s+and\s+/i).map((c) => c.replace(/\s+/g, "").toLowerCase());
      const want = KEY_COLS.map((c) => `${alias}.${c}=${v}.${c}`);
      if (conds.length !== want.length || !want.every((w) => conds.includes(w)) || !KEY_COLS.every((c) => vcols.includes(c))) return bad("the WHERE clause is not the three key columns of the table equal to those of the VALUES list");
      const keys: string[] = [];
      for (const t of tuples) {
        const vals = splitSqlList(t).map(sqlLiteral);
        if (vals.length !== vcols.length || vals.some((x) => typeof x !== "string")) return bad("a VALUES row is not one quoted text per column");
        const rec = Object.fromEntries(vcols.map((c, i) => [c, vals[i]]));
        keys.push(`${rec.biomarker_key}|${rec.sex}|${rec.age_group_en}`);
      }
      ops.push({ kind: "delete", keys });
      return;
    }
    bad(/\bbiomarker_references\b/i.test(s) ? "a statement on biomarker_references that is not one of the three forms D5 reads" : "not one of the three forms D5 reads, nor a bare BEGIN, START TRANSACTION or COMMIT");
  });
  if (transaction.open !== null) unreadable.push(transaction.open);
  return { file, ops, unreadable };
}

/** Production with the forward migration applied, by database key: the rows and compared values the documented pack changes give. */
export function applyForwardMigration(rows: ProdRow[], mig: ForwardMigration): Map<string, ProdRow> {
  const out = new Map(rows.map((r) => [rowKey(r), { ...r }] as const));
  const set = (r: ProdRow, rec: Record<string, unknown>, c: string) => {
    if (c === "unit_en") r.unit_en = rec.unit_en == null ? "" : String(rec.unit_en);
    else if ((BOUND_COLS as readonly string[]).includes(c) || isCritical(c)) {
      const v = rec[c];
      (r as unknown as Record<string, unknown>)[c] = typeof v === "number" && Number.isFinite(v) ? v : null;
    }
  };
  for (const op of mig.ops) {
    if (op.kind === "delete") {
      for (const k of op.keys) out.delete(k);
      continue;
    }
    for (const rec of op.rows) {
      const k = `${rec.biomarker_key}|${rec.sex}|${rec.age_group_en}`;
      const cur = out.get(k);
      if (cur) {
        for (const c of op.update) if (c in rec) set(cur, rec, c);
        continue;
      }
      const r: ProdRow = { biomarker_key: String(rec.biomarker_key), sex: String(rec.sex), age_group_en: String(rec.age_group_en), unit_en: "", normal_low: null, normal_high: null, optimal_low: null, optimal_high: null, critical_low: null, critical_high: null };
      for (const c of COMPARED) set(r, rec, c);
      out.set(k, r);
    }
  }
  return out;
}

/** The folder of the run's work dir that holds the reconciliation set D6 reads (docs/signoff/work/reconciliation/README.md). */
export const RECONCILIATION_DIR = "reconciliation";
/** The parts of the reconciliation set and the pattern of the file name D6 reads each from. */
export const RECONCILIATION_PARTS = { diff: /diff.*\.json$/i, forward: /forward.*\.sql$/i, rollback: /rollback.*\.sql$/i, readers: /reader.*result.*\.json$/i } as const;
export type ReconciliationPart = keyof typeof RECONCILIATION_PARTS;

/**
 * A reconciliation folder as D6 reads it (<work dir>/reconciliation): its entries in sorted order and, for each part,
 * the entry D6 reads, the first whose name matches the part's pattern (undefined when none does). D5 reads the diff
 * and the forward migration of the work dir's folder when no changes.json is next to the seed (loadDocumentedChanges),
 * and G1 holds the parts docs/signoff/tools/compile.js --reconciliation-dir writes to a rerun of the compile, whose
 * folder it reads with this function too (governance.ts compileIdempotency): the three checks pick the same files.
 */
export function reconciliationSet(dir: string): { entries: string[]; picked: Record<ReconciliationPart, string | undefined> } {
  const entries = fs.existsSync(dir) ? fs.readdirSync(dir).sort() : [];
  const picked = {} as Record<ReconciliationPart, string | undefined>;
  for (const part of Object.keys(RECONCILIATION_PARTS) as ReconciliationPart[]) picked[part] = entries.find((f) => RECONCILIATION_PARTS[part].test(f));
  return { entries, picked };
}

/**
 * The documented pack changes that belong to the seed being checked: the changes.json next to it with the
 * migration.sql the compile wrote beside it, else the reconciliation diff D6 reads with the forward migration in the
 * same folder (the first forward*.sql, as D6 finds it: reconciliationSet). A changes.json next to the seed that holds
 * no change list documents nothing; the reconciliation diff is not used in its place.
 */
export function loadDocumentedChanges(ctx: Ctx): DocumentedChanges | null {
  const relOf = (p: string) => path.relative(ctx.root, p).split(path.sep).join("/");
  const readMigration = (file: string | null): ForwardMigration | null => {
    const sql = file ? ctx.load<string>(file) : null;
    return file && typeof sql === "string" ? parseForwardMigration(sql, relOf(file)) : null;
  };
  const next = path.join(ctx.seedDir, "changes.json");
  if (fs.existsSync(next)) return { file: relOf(next), kind: "changes.json", changes: changesFromCompile(ctx.load(next)) ?? [], migration: readMigration(path.join(ctx.seedDir, "migration.sql")) };
  const dir = path.join(ctx.workDir, RECONCILIATION_DIR);
  const { picked } = reconciliationSet(dir);
  const diff = picked.diff;
  if (!diff) return null;
  const forward = picked.forward;
  return { file: relOf(path.join(dir, diff)), kind: "reconciliation diff", changes: changesFromDiff(ctx.load(path.join(dir, diff))) ?? [], migration: readMigration(forward ? path.join(dir, forward) : null) };
}

/** The value of a compared column as the seed, production or a documented change holds it. */
const sameValue = (field: string, a: unknown, b: unknown): boolean => {
  if (field === "unit_en") return normalizeUnit(String(a ?? "")) === normalizeUnit(String(b ?? ""));
  const num = (v: unknown) => (v == null || v === "" ? null : Number(v));
  return num(a) === num(b);
};
const fmtValue = (field: string, v: unknown): string => (v == null ? "null" : field === "unit_en" ? `"${String(v)}"` : String(v));

/** The recorded decision that retires a production-only marker: the decisions file, or null with what is missing. */
export type RetirementLookup = (marker: string, productionRows: ProdRow[]) => { file: string | null; gaps: string[] };

export interface SourceOfTruthOptions {
  /** The documented pack changes of the seed being checked (change list and forward migration), if any. */
  documented?: DocumentedChanges | null;
  /** The recorded decision that retires a production-only marker (retiringDecision). */
  retiredBy?: RetirementLookup;
}

/**
 * D5's comparison of the seed with production plus the documented pack changes, on the four bounds, the two critical
 * limits and the unit (COMPARED; production's critical limits are null, as the snapshot has no such column). A
 * difference between the seed and production is explained only when (1) the change list lists its row and field (op
 * modify; add or remove with field "row" for a row only in the seed or only in production) with a stated reason and a
 * stated source, and, for a changes.json entry, from/to equal to production's and the seed's values; and (2)
 * production with the documented forward migration applied holds the seed's value: the migration writes the field's
 * value, adds the row with the seed's six bounds and unit, or deletes the row. A marker only in the seed needs every
 * row explained as added; a marker only in production needs every row explained as removed and a recorded decision
 * (retiredBy). A seed row that differs from what the forward migration writes is unexplained even where it equals
 * production (a documented change the seed does not carry). The other columns are compared by checkEveryColumn, their
 * differences from production are held to the change list by checkDifferencesListed, and the change list is held to
 * what the forward migration does by checkChangeList; D5 runs all four. The seed's values here are the checks'
 * reading (seed.ts buildRows), which is the value the seeder writes while each bound and critical limit is a number or
 * null; checkSeedNumbers fails any other.
 */
export function checkSourceOfTruth(seedRows: Row[], prod: ProdRow[], opts: SourceOfTruthOptions = {}): { failures: Failure[]; metrics: Record<string, number | string> } {
  const failures: Failure[] = [];
  const doc = opts.documented ?? null;
  const where = doc ? doc.file : "no documented change list (changes.json next to the seed, or the reconciliation diff)";
  const mig = doc?.migration ?? null;
  // The documented values: production with the forward migration applied. Without a forward migration that D5 can
  // read in full, no value is documented and no difference is explained.
  const documentedRows = mig && !mig.unreadable.length ? applyForwardMigration(prod, mig) : null;
  const migFile = mig?.file ?? "";
  const noValues = !doc ? where : !mig ? `no forward migration was written with ${doc.file}, so no value is documented` : `the forward migration ${mig.file} has statements D5 cannot read, so no value is documented`;
  if (mig?.unreadable.length) failures.push({ key: `migration|${mig.file}|unreadable`, detail: `${mig.unreadable.length} statements or places that D5 cannot read, so it takes no value from the file: ${mig.unreadable.join("; ")}` });
  const listed = new Map<string, DocumentedChange[]>();
  for (const c of doc?.changes ?? []) {
    const k = `${c.row_key}#${c.field}`;
    listed.set(k, [...(listed.get(k) ?? []), c]);
  }
  const join = (...why: (string | null)[]): string | null => why.filter((w): w is string => !!w).join("; ") || null;
  /** Why the change list does not document a difference; null when it lists it with a stated reason and source (and this from/to, when it records values). */
  const listWhy = (rk: string, field: string, op: string, seedValue?: unknown, prodValue?: unknown): string | null => {
    const hits = (listed.get(`${rk}#${field}`) ?? []).filter((c) => c.op === op);
    if (!hits.length) return doc ? `not documented in ${where}` : where;
    const stated = hits.filter((c) => isStated(c.reason) && isStated(c.source));
    if (!stated.length) {
      const c = hits[0];
      return `documented in ${where} without ${!isStated(c.reason) ? "a reason" : "a source"}`;
    }
    if (op !== "modify") return null;
    const matching = stated.filter((c) => !c.values || (sameValue(field, c.values.to, seedValue) && sameValue(field, c.values.from, prodValue)));
    if (matching.length) return null;
    const c = stated[0];
    return `documented in ${where} as ${String(c.values?.from ?? "null")} → ${String(c.values?.to ?? "null")}, not this difference`;
  };
  /** Why the documented migration does not give field f of row rk the seed's value; null when it does. */
  const fieldValueWhy = (rk: string, f: ComparedField, seedValue: unknown): string | null => {
    if (!documentedRows) return noValues;
    const d = documentedRows.get(rk);
    if (!d) return `the forward migration ${migFile} deletes this row`;
    return sameValue(f, d[f], seedValue) ? null : `the forward migration ${migFile} writes ${f} ${fmtValue(f, d[f])}`;
  };
  /** Why the documented migration does not add row rk with the seed's six bounds and unit; null when it does. */
  const addedValueWhy = (rk: string, s: Row): string | null => {
    if (!documentedRows) return noValues;
    const d = documentedRows.get(rk);
    if (!d) return `the forward migration ${migFile} does not add this row`;
    const off = COMPARED.filter((f) => !sameValue(f, d[f], s[f])).map((f) => `${f} ${fmtValue(f, d[f])} (seed ${fmtValue(f, s[f])})`);
    return off.length ? `the forward migration ${migFile} writes ${off.join(", ")}` : null;
  };
  /** Why the documented migration does not delete row rk; null when it does. */
  const removedValueWhy = (rk: string): string | null => {
    if (!documentedRows) return noValues;
    return documentedRows.has(rk) ? `the forward migration ${migFile} does not delete this row` : null;
  };
  let explained = 0;
  const seedKeys = new Set(seedRows.map((r) => r.biomarker_key));
  const prodKeys = new Set(prod.map((r) => r.biomarker_key));
  const onlyProd = [...prodKeys].filter((k) => !seedKeys.has(k)).sort();
  const onlySeed = [...seedKeys].filter((k) => !prodKeys.has(k)).sort();
  const prodByKey = new Map(prod.map((r) => [rowKey(r), r] as const));
  const seedByKey = new Map<string, Row>();
  for (const r of seedRows) seedByKey.set(rowKey(r), r); // the seeder keeps the last duplicate
  const byKeyOrder = (a: string, b: string) => (a < b ? -1 : a > b ? 1 : 0);
  // Markers only in production: every row explained as removed, and a recorded decision that retires the marker.
  let onlyProdOpen = 0;
  for (const m of onlyProd) {
    const keys = [...prodByKey.keys()].filter((k) => prodByKey.get(k)!.biomarker_key === m).sort(byKeyOrder);
    const open = keys.map((k) => [k, join(listWhy(k, "row", "remove"), removedValueWhy(k))] as const).filter(([, why]) => why);
    const decision = opts.retiredBy ? opts.retiredBy(m, keys.map((k) => prodByKey.get(k)!)) : { file: null, gaps: ["no decisions file was read"] };
    if (!open.length && decision.file) {
      explained++;
      continue;
    }
    onlyProdOpen++;
    const why = [...(decision.file ? [] : [`no recorded decision retires it (${decision.gaps.join("; ")})`]), ...open.map(([k, w]) => `${k} ${w}`)];
    failures.push({ key: `${m}|only_in_production`, detail: `marker exists in production but not in the seed; it must enter the seed or be retired by a recorded decision: ${why.join("; ")}` });
  }
  // Markers only in the seed: every row explained as added, with the documented values.
  let onlySeedOpen = 0;
  for (const m of onlySeed) {
    const open = [...seedByKey.keys()]
      .filter((k) => seedByKey.get(k)!.biomarker_key === m)
      .sort(byKeyOrder)
      .map((k) => [k, join(listWhy(k, "row", "add"), addedValueWhy(k, seedByKey.get(k)!))] as const)
      .filter(([, why]) => why);
    if (!open.length) {
      explained++;
      continue;
    }
    onlySeedOpen++;
    failures.push({ key: `${m}|only_in_seed`, detail: `marker exists in the seed but not in production plus the applied migrations: ${open.map(([k, w]) => `${k} ${w}`).join("; ")}` });
  }
  let rowDiffs = 0;
  let rowDiffsOpen = 0;
  for (const [k, s] of seedByKey) {
    if (!prodKeys.has(s.biomarker_key)) continue;
    const p = prodByKey.get(k);
    if (!p) {
      rowDiffs++;
      const why = join(listWhy(k, "row", "add"), addedValueWhy(k, s));
      if (!why) explained++;
      else {
        rowDiffsOpen++;
        failures.push({ key: `${k}|row_only_in_seed`, detail: `row (key, sex, age group) has no production counterpart; ${why}` });
      }
      continue;
    }
    const diffs = COMPARED.filter((f) => !sameValue(f, s[f], p[f]));
    if (!diffs.length) continue;
    rowDiffs++;
    const open = diffs.map((f) => ({ f, why: join(listWhy(k, f, "modify", s[f] ?? null, p[f] ?? null), fieldValueWhy(k, f, s[f] ?? null)) })).filter((d) => d.why);
    explained += diffs.length - open.length;
    if (open.length) {
      rowDiffsOpen++;
      const text = (f: ComparedField) => (f === "unit_en" ? `unit seed "${s.unit_en}" vs production "${p.unit_en}"` : `${f} seed ${s[f] ?? "null"} vs production ${p[f] ?? "null"}`);
      failures.push({ key: `${k}|bounds`, detail: open.map((d) => `${text(d.f)} (${d.why})`).join("; ") });
    }
  }
  for (const [k, p] of prodByKey) {
    if (!seedKeys.has(p.biomarker_key) || seedByKey.has(k)) continue;
    rowDiffs++;
    const why = join(listWhy(k, "row", "remove"), removedValueWhy(k));
    if (!why) explained++;
    else {
      rowDiffsOpen++;
      failures.push({ key: `${k}|row_only_in_production`, detail: `production row (key, sex, age group) has no seed counterpart; ${why}` });
    }
  }
  // Documented changes the seed does not carry: where the seed equals production, it must also equal what the
  // forward migration writes. (Differences from production were judged above.)
  let notCarried = 0;
  if (documentedRows) {
    for (const [k, d] of documentedRows) {
      const s = seedByKey.get(k);
      const p = prodByKey.get(k);
      if (s && p) {
        const fields = COMPARED.filter((f) => sameValue(f, s[f], p[f]) && !sameValue(f, d[f], s[f]));
        if (!fields.length) continue;
        notCarried++;
        failures.push({ key: `${k}|documented_migration`, detail: `the seed keeps production's ${fields.map((f) => `${f} ${fmtValue(f, s[f])}`).join(", ")}; the forward migration ${migFile} writes ${fields.map((f) => `${f} ${fmtValue(f, d[f])}`).join(", ")}` });
      } else if (!s && !p) {
        notCarried++;
        failures.push({ key: `${k}|documented_migration`, detail: `the forward migration ${migFile} adds this row; the seed does not hold it` });
      }
    }
    for (const [k, s] of seedByKey) {
      const p = prodByKey.get(k);
      if (!p || documentedRows.has(k) || !COMPARED.every((f) => sameValue(f, s[f], p[f]))) continue;
      notCarried++;
      failures.push({ key: `${k}|documented_migration`, detail: `the forward migration ${migFile} deletes this row; the seed keeps it` });
    }
  }
  return {
    failures,
    metrics: {
      seed_markers: seedKeys.size,
      production_markers: prodKeys.size,
      only_in_production: onlyProd.length,
      only_in_seed: onlySeed.length,
      row_differences: rowDiffs,
      only_in_production_keys: onlyProd.join(","),
      only_in_seed_keys: onlySeed.join(","),
      unexplained_only_in_production: onlyProdOpen,
      unexplained_only_in_seed: onlySeedOpen,
      unexplained_row_differences: rowDiffsOpen,
      documented_changes_not_in_seed: notCarried,
      explained_by_documented_changes: explained,
      documented_changes_file: doc?.file ?? "none",
      documented_changes: doc?.changes.length ?? 0,
      documented_migration_file: mig?.file ?? "none",
      documented_migration_unreadable: mig?.unreadable.length ?? 0,
      compared_fields: COMPARED.join(","),
    },
  };
}

// ─── D5 on every column, and the change list against the forward migration ───
//
// checkSourceOfTruth holds the seed to production plus the documented pack changes on the four bounds, the two
// critical limits and the unit, and asks a listed change with a stated reason and source for each difference from
// production there. checkEveryColumn holds the seed to the same production and the same forward migration on every
// other column both carry; checkDifferencesListed asks a listed change for each difference from production on those
// columns; checkChangeList holds the change list to what the forward migration does. Production on every column is the
// compile's own baseline (compile-baseline.js buildBaseline); productionDisagreements fails where it and the
// production checkSourceOfTruth reads differ. checkSeedNumbers fails a bound or critical limit the checks read
// otherwise than the seeder writes it, so that checkSourceOfTruth compares the values the database would get.

/** A row of public.biomarker_references by column, as docs/signoff/tools/lib/compile-rows.js and compile-baseline.js hold it. */
export type DbRow = Record<string, unknown>;

/** What D5 takes from the compile's own libraries, docs/signoff/tools/lib/compile-rows.js and compile-baseline.js. */
export interface CompileTools {
  /** The table's columns in its order, then the sign-off columns (compile-rows.js DB_COLS and DB_EXT_COLS). */
  columns: readonly string[];
  /** The database row the seeder writes for an English and Spanish seed pair, with the sign-off columns (compile-rows.js dbRowFromPair). */
  dbRowFromPair(pair: { en: RawEn; es: RawEs }): DbRow;
  /** Production on every column: the gate1 snapshot plus every change applied after it (compile-baseline.js buildBaseline). */
  buildBaseline(opts: { snapshot: string; migrationsDir: string }): { rows: DbRow[]; not_reconstructed: { migration: string; reason: string }[]; warnings: string[] };
}

/** The compile's libraries under root, or null when either file is missing. */
export function loadCompileTools(root: string): CompileTools | null {
  const lib = (f: string) => path.join(root, "docs/signoff/tools/lib", f);
  if (!fs.existsSync(lib("compile-rows.js")) || !fs.existsSync(lib("compile-baseline.js"))) return null;
  const req = createRequire(import.meta.url);
  const rows = req(lib("compile-rows.js")) as { DB_COLS: string[]; DB_EXT_COLS: string[]; dbRowFromPair: CompileTools["dbRowFromPair"] };
  const baseline = req(lib("compile-baseline.js")) as { buildBaseline: CompileTools["buildBaseline"] };
  return { columns: [...rows.DB_COLS, ...rows.DB_EXT_COLS], dbRowFromPair: rows.dbRowFromPair, buildBaseline: baseline.buildBaseline };
}

const dbKeyOf = (r: DbRow): string => `${r.biomarker_key}|${r.sex}|${r.age_group_en}`;

/**
 * A value as written, for comparing two values exactly: null and an absent value alike, a text quoted, a number as
 * JSON writes it (an infinite one marked), an array item by item in order, true and false as words.
 */
const canonical = (v: unknown): string =>
  v === undefined || v === null
    ? "null"
    : Array.isArray(v)
      ? `[${v.map(canonical).join(",")}]`
      : typeof v === "number"
        ? Number.isFinite(v)
          ? JSON.stringify(v)
          : `#${String(v)}`
        : typeof v === "string"
          ? JSON.stringify(v)
          : typeof v === "boolean"
            ? String(v)
            : `#${JSON.stringify(v)}`;
const exactSame = (a: unknown, b: unknown): boolean => canonical(a) === canonical(b);
/** A value for a failure detail: null, a quoted text, an array as JSON, anything else as written. */
const fmtCell = (v: unknown): string => (v === undefined || v === null ? "null" : typeof v === "string" || Array.isArray(v) ? JSON.stringify(v) : String(v));
const isComparedField = (c: string): boolean => (COMPARED as readonly string[]).includes(c);
/** The columns checkEveryColumn and checkDifferencesListed compare: every column but the three key columns, the four bounds and the two critical limits. */
const otherColumns = (columns: readonly string[]): string[] => columns.filter((c) => !KEY_COLS.includes(c) && !isNumericCompared(c));
/** Whether two values of column c differ as checkEveryColumn and checkDifferencesListed compare them: as written; the unit only where normalizeUnit finds the same unit, as checkSourceOfTruth compares a unit that differs by normalizeUnit. */
const differsAsWritten = (c: string, a: unknown, b: unknown): boolean => !exactSame(a, b) && (c !== "unit_en" || sameValue(c, a, b));

/** Why no forward migration documents a value: no change list, no forward migration with it, or one D5 cannot read (the texts checkSourceOfTruth gives). */
const noValuesWhy = (doc: DocumentedChanges | null): string =>
  !doc
    ? "no documented change list (changes.json next to the seed, or the reconciliation diff)"
    : !doc.migration
      ? `no forward migration was written with ${doc.file}, so no value is documented`
      : `the forward migration ${doc.migration.file} has statements D5 cannot read, so no value is documented`;

/**
 * The seed's database rows by key: compile-rows.js dbRowFromPair of each English row with the Spanish row at its
 * index (the two files pair rows by index, seed.ts buildRows), the last of duplicate keys kept, as the seeder keeps it.
 */
export function seedDatabaseRows(en: RawEn[], es: RawEs[], dbRowFromPair: CompileTools["dbRowFromPair"]): Map<string, DbRow> {
  const out = new Map<string, DbRow>();
  en.forEach((e, i) => {
    const r = dbRowFromPair({ en: e, es: es[i] ?? {} });
    out.set(dbKeyOf(r), r);
  });
  return out;
}

/** Production by key on every column: each row's value, null where it has none (the sign-off columns, which the table does not have yet). */
export function productionDatabaseRows(rows: DbRow[], columns: readonly string[]): Map<string, DbRow> {
  return new Map(rows.map((r) => [dbKeyOf(r), Object.fromEntries(columns.map((c) => [c, r[c] ?? null]))] as const));
}

/**
 * The value PostgreSQL writes into a column an INSERT leaves out of a row it adds: false for tested_2x_year,
 * is_base_panel and is_genetic (supabase/migrations/20260403000000_full_schema.sql lines 118, 120 and 121, "boolean
 * default false", unchanged by any later migration); null for every other column, the sign-off columns included,
 * which the forward migration adds without a default (parseForwardMigration reads no other ALTER).
 */
export const COLUMN_DEFAULTS: Readonly<Record<string, unknown>> = { tested_2x_year: false, is_base_panel: false, is_genetic: false };

/** Production with a forward migration applied on every column, and what the migration wrote. */
export interface AppliedMigration {
  /** The rows by key after the migration, on every column. */
  rows: Map<string, DbRow>;
  /** For each row the migration wrote and did not delete afterwards, the columns it wrote: an INSERT's column list for a row it added, the DO UPDATE SET columns for a row that existed. */
  written: Map<string, Set<string>>;
  /** The rows a DELETE of the migration removed and no later statement added again. */
  deleted: Set<string>;
}

/**
 * Production with the forward migration's statements applied in order, on every column: an upsert adds a row that
 * does not exist with the columns it lists (COLUMN_DEFAULTS, else null, for the others) and, for a row that exists,
 * sets the DO UPDATE SET columns to the proposed values (DO NOTHING sets none); a DELETE removes the rows it names.
 * The migration must be one D5 reads (parseForwardMigration lists nothing unreadable), so every DO UPDATE SET column
 * is in the INSERT's column list.
 */
export function applyForwardMigrationColumns(production: Map<string, DbRow>, mig: ForwardMigration, columns: readonly string[]): AppliedMigration {
  const rows = new Map<string, DbRow>([...production].map(([k, r]) => [k, { ...r }]));
  const written = new Map<string, Set<string>>();
  const deleted = new Set<string>();
  for (const op of mig.ops) {
    if (op.kind === "delete") {
      for (const k of op.keys) {
        if (!rows.has(k)) continue;
        rows.delete(k);
        written.delete(k);
        deleted.add(k);
      }
      continue;
    }
    for (const rec of op.rows) {
      const k = dbKeyOf(rec);
      const cur = rows.get(k);
      if (cur) {
        if (!op.update.length) continue;
        for (const c of op.update) cur[c] = rec[c];
        written.set(k, new Set([...(written.get(k) ?? []), ...op.update]));
        continue;
      }
      const added: DbRow = Object.fromEntries(columns.map((c) => [c, Object.prototype.hasOwnProperty.call(COLUMN_DEFAULTS, c) ? COLUMN_DEFAULTS[c] : null]));
      for (const [c, v] of Object.entries(rec)) added[c] = v;
      rows.set(k, added);
      written.set(k, new Set(Object.keys(rec)));
      deleted.delete(k);
    }
  }
  return { rows, written, deleted };
}

/**
 * D5 on every column both carry. Each seed row's database row (seedDatabaseRows) is compared with production with
 * the documented forward migration applied on every column (applyForwardMigrationColumns), or with production alone
 * when no forward migration D5 can read documents a value; a row of one side only is left to checkSourceOfTruth,
 * which fails it. Compared: every column but the three key columns and the four bounds and two critical limits, which
 * checkSourceOfTruth compares with the same values (the same while each is a number or null in the seed, which
 * checkSeedNumbers asks); the unit is compared here as written, where checkSourceOfTruth, which compares it through
 * normalizeUnit, finds no difference. Each row with a column that differs fails once, its detail naming each such
 * column with both values.
 */
export function checkEveryColumn(seedDb: Map<string, DbRow>, production: Map<string, DbRow>, documented: DocumentedChanges | null, columns: readonly string[]): { failures: Failure[]; metrics: Record<string, number | string> } {
  const mig = documented?.migration ?? null;
  const readable = mig && !mig.unreadable.length ? mig : null;
  const target = readable ? applyForwardMigrationColumns(production, readable, columns).rows : production;
  const against = readable ? `production plus the forward migration ${readable.file}` : "production";
  const why = readable ? "" : ` (${noValuesWhy(documented)})`;
  const fields = otherColumns(columns);
  const failures: Failure[] = [];
  let compared = 0;
  let differences = 0;
  for (const [k, s] of seedDb) {
    const d = target.get(k);
    if (!d) continue;
    compared++;
    const off = fields.filter((c) => differsAsWritten(c, s[c], d[c]));
    if (!off.length) continue;
    differences += off.length;
    failures.push({ key: `${k}|columns`, detail: `${off.map((c) => `${c} seed ${fmtCell(s[c])} vs ${against} ${fmtCell(d[c])}`).join("; ")}${why}` });
  }
  return { failures, metrics: { every_column_fields: fields.join(","), every_column_rows: compared, column_differences: differences, rows_with_column_differences: failures.length } };
}

/**
 * D5's differences from production against the change list, on the columns checkEveryColumn compares. For each seed
 * row production has, each such column on which the seed's database row (seedDatabaseRows, the last of duplicate keys)
 * differs from production (compile-baseline.js buildBaseline) must be a change the list records for that row and
 * field: op modify, with "to" the seed's value and "from" production's, both compared as written (a text exactly, a
 * list item by item in order; the unit, which is compared here only where normalizeUnit finds the same unit, by its
 * spelling). A change the reconciliation diff lists without values (a row without changes[]) needs only its row and
 * field listed. No reason or source is asked of these columns: compile.js lists their changes with the reason the
 * loop's files give, often none (compiled/B01-r3/changes.json: 83 of 240 changes without one, all outside the bounds
 * and the unit but bun_creatinine_ratio's two optimal bounds). The four bounds, the two critical limits and a unit
 * that differs by normalizeUnit are checkSourceOfTruth's, which asks the same listed change (op modify, "to" the seed's
 * value and "from" production's, compared by value and a unit through normalizeUnit) and a stated reason and source as
 * well, so no difference is stated twice; a row production does not have is checkSourceOfTruth's too (an added row).
 * Without a documented change list no difference is recorded. Each row with a difference the list does not record
 * fails once, its detail naming each such column with the seed's and production's values and why the list does not
 * record it.
 */
export function checkDifferencesListed(seedDb: Map<string, DbRow>, production: Map<string, DbRow>, documented: DocumentedChanges | null, columns: readonly string[]): { failures: Failure[]; metrics: Record<string, number> } {
  const fields = otherColumns(columns);
  const listed = new Map<string, DocumentedChange[]>();
  for (const c of documented?.changes ?? []) listed.set(`${c.row_key}#${c.field}`, [...(listed.get(`${c.row_key}#${c.field}`) ?? []), c]);
  /** Why the change list does not record this difference of row k in column c; null when it does. */
  const unrecordedWhy = (k: string, c: string, seedValue: unknown, prodValue: unknown): string | null => {
    if (!documented) return noValuesWhy(null);
    const hits = listed.get(`${k}#${c}`) ?? [];
    if (!hits.length) return `not listed in ${documented.file}`;
    const modify = hits.filter((x) => x.op === "modify");
    if (!modify.length) return `listed in ${documented.file} with op ${[...new Set(hits.map((x) => `"${x.op}"`))].join(", ")}, not modify`;
    if (modify.some((x) => !x.values || (exactSame(x.values.to, seedValue) && exactSame(x.values.from, prodValue)))) return null;
    return `listed in ${documented.file} as ${modify.map((x) => `${fmtCell(x.values!.from)} → ${fmtCell(x.values!.to)}`).join(", ")}, not this difference`;
  };
  const failures: Failure[] = [];
  let compared = 0;
  let differences = 0;
  let unrecorded = 0;
  for (const [k, s] of seedDb) {
    const p = production.get(k);
    if (!p) continue;
    compared++;
    const open: string[] = [];
    for (const c of fields) {
      if (!differsAsWritten(c, s[c], p[c])) continue;
      differences++;
      const why = unrecordedWhy(k, c, s[c], p[c]);
      if (why) open.push(`${c} seed ${fmtCell(s[c])} vs production ${fmtCell(p[c])} (${why})`);
    }
    if (!open.length) continue;
    unrecorded += open.length;
    failures.push({ key: `${k}|not_listed`, detail: `differences from production that the change list does not record: ${open.join("; ")}` });
  }
  return { failures, metrics: { listed_difference_rows: compared, differences_from_production: differences, differences_not_listed: unrecorded, rows_with_differences_not_listed: failures.length } };
}

/** The English seed's four bounds and two critical limits (compile-rows.js BOUNDS and EXT), the columns checkSourceOfTruth compares. */
const SEED_NUMBER_COLUMNS = ["Normal_Low", "Normal_High", "Optimal_Low", "Optimal_High", "Critical_Low", "Critical_High"] as const;

/**
 * The English seed's bounds and critical limits that are neither a finite JSON number nor null (or absent). The checks
 * read such a value as no value (scripts/signoff/lib/seed.ts buildRows), while the seeder hands the English file's
 * value to the database as written (src/lib/biomarkers/seed-references.ts buildRows), which reads 48 from the text
 * "48", and compile-rows.js dbRowFromPair reads 48 from it too. checkSourceOfTruth compares these columns as the checks
 * read them, so such a seed could pass while the database would get another value than production plus the forward
 * migration. The Spanish file's bounds are not seeded; D2, and D5 itself through checkParity, hold each to the English
 * one as the checks read both, so a Spanish text against an English number fails there. Each row with such a value
 * fails once (rows that share a key, which D1 fails, share the failure), its detail naming each value with its file
 * index.
 */
export function checkSeedNumbers(en: RawEn[], rows: Row[]): Failure[] {
  const byRow = new Map<string, string[]>();
  en.forEach((e, i) => {
    const off = SEED_NUMBER_COLUMNS.filter((c) => e[c] != null && !(typeof e[c] === "number" && Number.isFinite(e[c])));
    if (!off.length) return;
    const k = rowKey(rows[i]);
    byRow.set(k, [...(byRow.get(k) ?? []), ...off.map((c) => `${c} ${JSON.stringify(e[c])} (file index ${i})`)]);
  });
  return [...byRow].map(([k, list]) => ({
    key: `${k}|not_a_number`,
    detail: `bound or critical limit in the English seed that is not a number or null: ${list.join("; ")}. The checks read it as no value (scripts/signoff/lib/seed.ts); the seeder passes it to the database as written (src/lib/biomarkers/seed-references.ts)`,
  }));
}

/** A listed change as a failure detail names it: an added or removed row, or a field with the value the change list gives it. */
const describeChange = (c: DocumentedChange): string =>
  c.field === "row" ? (c.op === "add" ? "row added" : c.op === "remove" ? "row removed" : `row with op "${c.op}"`) : c.values ? `${c.field} to ${fmtCell(c.values.to)}` : c.field;

/** Why the applied forward migration file does not make the listed change c; null when it makes it. */
function changeNotMadeWhy(c: DocumentedChange, applied: AppliedMigration, columns: readonly string[], file: string): string | null {
  const k = c.row_key;
  const row = applied.rows.get(k);
  if (c.field === "row") {
    if (c.op === "add") return row && applied.written.has(k) ? null : row ? `the forward migration ${file} does not upsert this row` : applied.deleted.has(k) ? `the forward migration ${file} deletes this row` : `the forward migration ${file} does not add this row`;
    if (c.op === "remove") return !row && applied.deleted.has(k) ? null : row ? `the forward migration ${file} does not delete this row` : `the forward migration ${file} deletes no such row (it is not in production)`;
    return `op "${c.op}" of a row is neither add nor remove`;
  }
  if (c.op !== "modify") return `op "${c.op}" of field ${c.field} is not modify`;
  if (!columns.includes(c.field)) return `${c.field} is not a column of public.biomarker_references or a sign-off column`;
  if (!row) return applied.deleted.has(k) ? `the forward migration ${file} deletes this row` : `the forward migration ${file} does not add this row and production has none`;
  if (!applied.written.get(k)?.has(c.field)) return `the forward migration ${file} does not write ${c.field}, which stays ${fmtCell(row[c.field])}`;
  // The reconciliation diff lists a row's fields without values: the field is written, which is all it says.
  if (!c.values) return null;
  const made = isComparedField(c.field) ? sameValue(c.field, row[c.field], c.values.to) : exactSame(row[c.field], c.values.to);
  return made ? null : `the forward migration ${file} writes ${c.field} ${fmtCell(row[c.field])}`;
}

/**
 * D5's change list against the forward migration: every listed change must be what the migration does. A row "add"
 * is upserted (added, or written by DO UPDATE SET) and still there at the end; a row "remove" is deleted; a field
 * "modify" is written by the migration and holds the change's "to" value at the end, compared with sameValue for the
 * four bounds, the two critical limits and the unit and exactly otherwise. A change the reconciliation diff lists
 * without values needs its row written, or deleted, as its op says, and a modified field written. Any other op fails,
 * and so does every listed change when no forward migration D5 can read was written with the list. Each row with a
 * listed change the migration does not make fails once, its detail naming each such change by field.
 */
export function checkChangeList(documented: DocumentedChanges | null, production: Map<string, DbRow>, columns: readonly string[]): { failures: Failure[]; metrics: Record<string, number> } {
  if (!documented) return { failures: [], metrics: { listed_changes: 0, listed_changes_not_made: 0, rows_with_listed_changes_not_made: 0 } };
  const mig = documented.migration ?? null;
  const readable = mig && !mig.unreadable.length ? mig : null;
  const applied = readable ? applyForwardMigrationColumns(production, readable, columns) : null;
  const byRow = new Map<string, string[]>();
  let notMade = 0;
  for (const c of documented.changes) {
    const why = applied ? changeNotMadeWhy(c, applied, columns, readable!.file) : noValuesWhy(documented);
    if (!why) continue;
    notMade++;
    byRow.set(c.row_key, [...(byRow.get(c.row_key) ?? []), `${describeChange(c)} (${why})`]);
  }
  const failures = [...byRow].map(([k, list]) => ({ key: `${k}|change_list`, detail: `${documented.file} lists changes the forward migration does not make: ${list.join("; ")}` }));
  return { failures, metrics: { listed_changes: documented.changes.length, listed_changes_not_made: notMade, rows_with_listed_changes_not_made: failures.length } };
}

/**
 * Where D5's two readings of production differ, on the rows, the four bounds or the unit: the rows checkSourceOfTruth
 * reads (the gate1 snapshot with the migration files applied after it replayed by applyMigrationBounds) and the rows
 * checkEveryColumn and checkChangeList read (compile-baseline.js buildBaseline). Neither has a critical limit.
 */
export function productionDisagreements(prod: ProdRow[], production: Map<string, DbRow>): Failure[] {
  const failures: Failure[] = [];
  const replayed = new Map(prod.map((r) => [rowKey(r), r] as const));
  for (const [k, p] of replayed) {
    const b = production.get(k);
    if (!b) {
      failures.push({ key: `production|${k}|baseline`, detail: "row in the snapshot with the applied migration files replayed (applyMigrationBounds), not in compile-baseline.js buildBaseline" });
      continue;
    }
    const off = [...BOUND_COLS, "unit_en"].filter((c) => !exactSame((p as unknown as DbRow)[c], b[c]));
    if (off.length) failures.push({ key: `production|${k}|baseline`, detail: off.map((c) => `${c} ${fmtCell((p as unknown as DbRow)[c])} in the replayed migration files vs ${fmtCell(b[c])} in compile-baseline.js buildBaseline`).join("; ") });
  }
  for (const k of production.keys()) if (!replayed.has(k)) failures.push({ key: `production|${k}|baseline`, detail: "row in compile-baseline.js buildBaseline, not in the snapshot with the applied migration files replayed (applyMigrationBounds)" });
  return failures;
}

/** A decisions file as D5 reads it for a retirement record (decision.schema.json final_rows and changes). */
export interface RetirementDecision {
  final_rows?: { marker_key?: unknown }[];
  changes?: { row_key?: unknown; field?: unknown; to?: unknown; reason?: unknown }[];
}

/**
 * What a decisions file lacks to retire a production-only marker; [] when it retires it. The record must be explicit
 * and valid: the file validates with docs/signoff/tools/validate.js (validationErrors empty), carries no final row of
 * the marker, and its changes[] retire every production row of the marker by the row's key
 * (marker_key|sex|age_group|physiological_state, the key G2 traces a row by), with field "row", to null and a stated
 * reason. A marker merely left out of a decisions file is no record. (validate.js requires a final row for every key
 * of the family, row-checks.js checkFamilyKeys, so a family's own key cannot meet both conditions today.)
 */
export function retirementGaps(marker: string, productionRows: Pick<ProdRow, "biomarker_key" | "sex" | "age_group_en">[], file: string, doc: RetirementDecision | null, validationErrors: string[]): string[] {
  if (!doc) return [`${file} is missing or not valid JSON`];
  const gaps: string[] = [];
  if (validationErrors.length) gaps.push(`${file} does not validate (${validationErrors.length} errors; first: ${validationErrors[0]})`);
  if ((doc.final_rows ?? []).some((r) => r?.marker_key === marker)) gaps.push(`${file} keeps final rows of ${marker}`);
  const changes = Array.isArray(doc.changes) ? doc.changes : [];
  for (const p of productionRows) {
    const key = rowTraceKey(p);
    if (!changes.some((c) => c?.row_key === key && c.field === "row" && c.to === null && isStated(c.reason))) gaps.push(`no changes[] entry of ${file} retires ${key} (field "row", to null, a stated reason)`);
  }
  return gaps;
}

/**
 * The recorded decision that retires a production-only marker: the decisions file of the marker's family
 * (families.json), when retirementGaps finds nothing missing. validate(file) returns the file's validation errors;
 * by default docs/signoff/tools/validate.js decision, as G2 runs it.
 */
export function retiringDecision(ctx: Ctx, validate?: (file: string) => string[]): RetirementLookup {
  const familiesFile = path.join(ctx.workDir, "families.json");
  const fam = ctx.load<{ families?: Record<string, { keys?: string[] }> }>(familiesFile);
  const relOf = (p: string) => path.relative(ctx.root, p).split(path.sep).join("/");
  let check = validate;
  const errorsOf = (file: string): string[] => {
    if (!check) {
      const req = createRequire(import.meta.url);
      const validator = req(path.join(ctx.root, "docs/signoff/tools/validate.js")) as { validateFile(kind: string, file: string, opts?: Record<string, unknown>): { errors: string[] } };
      check = (f) => validator.validateFile("decision", f, { workDir: ctx.workDir, families: familiesFile }).errors;
    }
    return check(file);
  };
  return (marker, productionRows) => {
    const id = Object.entries(fam?.families ?? {}).find(([, f]) => (f.keys ?? []).includes(marker))?.[0];
    if (!id) return { file: null, gaps: [`${marker} is in no family of ${relOf(familiesFile)}`] };
    const file = path.join(ctx.workDir, "decisions", `${id}.json`);
    if (!fs.existsSync(file)) return { file: null, gaps: [`no ${relOf(file)}`] };
    const gaps = retirementGaps(marker, productionRows, relOf(file), ctx.load<RetirementDecision>(file), errorsOf(file));
    return { file: gaps.length ? null : relOf(file), gaps };
  };
}

const D5: Check = {
  id: "D5",
  group: "data",
  title: "One source of truth",
  how: "script",
  run(ctx) {
    const seed = loadSeed(ctx.seedDir);
    if (!seed) return blocked("D5", `${ctx.seedDir}/biomarker-ranges-en.json`);
    const snapshot = ctx.load<ProdRow[]>(PRODUCTION_SNAPSHOT);
    if (!snapshot) return blocked("D5", PRODUCTION_SNAPSHOT);
    // The snapshot has no critical-limit columns: production's critical limits are null.
    let prod: ProdRow[] = snapshot.map((r) => ({ biomarker_key: r.biomarker_key, sex: r.sex, age_group_en: r.age_group_en, unit_en: r.unit_en, normal_low: r.normal_low, normal_high: r.normal_high, optimal_low: r.optimal_low, optimal_high: r.optimal_high, critical_low: null, critical_high: null }));
    let applied = 0;
    const missing: string[] = [];
    for (const mig of MIGRATIONS_AFTER_SNAPSHOT) {
      const sql = ctx.load<string>(mig);
      if (!sql) {
        missing.push(mig);
        continue;
      }
      const r = applyMigrationBounds(prod, sql);
      prod = r.rows;
      applied += r.applied;
    }
    if (missing.length) return blocked("D5", missing.join(", "));
    // Production on every column, as the compile builds it, for the columns checkSourceOfTruth does not compare.
    const tools = loadCompileTools(ctx.root);
    if (!tools) return blocked("D5", "docs/signoff/tools/lib/compile-rows.js and compile-baseline.js");
    const baseline = tools.buildBaseline({ snapshot: path.resolve(ctx.root, PRODUCTION_SNAPSHOT), migrationsDir: path.resolve(ctx.root, "supabase/migrations") });
    const production = productionDatabaseRows(baseline.rows, tools.columns);
    const baselineFailures: Failure[] = [...productionDisagreements(prod, production)];
    const baselineProblems = [...baseline.not_reconstructed.map((n) => `${n.migration}: ${n.reason}`), ...baseline.warnings];
    if (baselineProblems.length) baselineFailures.push({ key: "production|baseline", detail: `compile-baseline.js buildBaseline does not reconstruct production on every column: ${baselineProblems.join("; ")}` });
    const parity = checkParity(seed.rows, seed.enCount, seed.esCount).filter((f) => /\|(normal|optimal|critical)_(low|high)$|\|unit$|_count$/.test(f.key));
    const documented = loadDocumentedChanges(ctx);
    const { failures, metrics } = checkSourceOfTruth(seed.rows, prod, { documented, retiredBy: retiringDecision(ctx) });
    const seedDb = seedDatabaseRows(seed.en, seed.es, tools.dbRowFromPair);
    const columns = checkEveryColumn(seedDb, production, documented, tools.columns);
    const unlisted = checkDifferencesListed(seedDb, production, documented, tools.columns);
    const listed = checkChangeList(documented, production, tools.columns);
    const numbers = checkSeedNumbers(seed.en, seed.rows);
    const all = [...failures, ...columns.failures, ...unlisted.failures, ...listed.failures, ...numbers, ...baselineFailures, ...parity.map((f) => ({ key: `es|${f.key}`, detail: `Spanish seed differs from English: ${f.detail}` }))];
    return result(
      "D5",
      all,
      `${all.length} unexplained differences: ${metrics.unexplained_only_in_production} of ${metrics.only_in_production} markers only in production, ${metrics.unexplained_only_in_seed} of ${metrics.only_in_seed} only in the seed, ${metrics.unexplained_row_differences} of ${metrics.row_differences} row differences, ${metrics.documented_changes_not_in_seed} seed rows that do not carry a documented change, ${parity.length} EN/ES bound differences, ${columns.metrics.rows_with_column_differences} of ${columns.metrics.every_column_rows} rows that differ on the other columns, ${unlisted.metrics.differences_not_listed} of ${unlisted.metrics.differences_from_production} differences from production on the other columns that the change list does not record, ${listed.metrics.listed_changes_not_made} of ${listed.metrics.listed_changes} listed changes the forward migration does not make, ${numbers.length} seed rows with a bound or critical limit that is not a number, ${baselineFailures.length} production baseline problems; ${metrics.explained_by_documented_changes} differences explained by ${metrics.documented_changes_file} with the values of ${metrics.documented_migration_file}`,
      {
        ...metrics,
        ...columns.metrics,
        ...unlisted.metrics,
        ...listed.metrics,
        rows_with_bounds_not_numbers: numbers.length,
        snapshot_rows: snapshot.length,
        production_rows_after_migrations: prod.length,
        production_baseline_rows: production.size,
        production_baseline_problems: baselineFailures.length,
        migration_bound_changes_applied: applied,
        en_es_bound_differences: parity.length,
      },
    );
  },
};

// ─── D6 production reconciliation ───

const D6: Check = {
  id: "D6",
  group: "data",
  title: "Production reconciliation",
  how: "script",
  run(ctx) {
    const dir = path.join(ctx.workDir, RECONCILIATION_DIR);
    if (!fs.existsSync(dir)) return blocked("D6", `${path.relative(ctx.root, dir)}/ (diff, forward migration, rollback and reader tests)`);
    const { entries: files, picked: need } = reconciliationSet(dir);
    const failures: Failure[] = [];
    for (const [k, v] of Object.entries(need)) if (!v) failures.push({ key: `missing_${k}`, detail: `no ${k} file under ${path.relative(ctx.root, dir)}/` });
    if (need.diff) {
      const diff = ctx.load<{ rows?: { key: string; reason?: string; source?: string }[] }>(path.join(dir, need.diff));
      for (const row of diff?.rows ?? []) {
        if (!row.reason || !row.source) failures.push({ key: `${row.key}|unexplained`, detail: `changed row without ${!row.reason ? "a reason" : "a source"}` });
      }
    }
    if (need.readers) {
      const r = ctx.load<{ passed?: boolean; failed?: number }>(path.join(dir, need.readers));
      if (!r?.passed) failures.push({ key: "reader_tests", detail: `reader tests not green (${r?.failed ?? "unknown"} failed)` });
    }
    return result("D6", failures, `${failures.length} problems in the reconciliation set (${files.length} files)`, { files: files.length });
  },
};

export const checks: Check[] = [D1, D2, D3, D4, D5, D6];
export type { Ctx };
