"""M1-11 unit tests: entirely synthetic fixture; not CIP measurements."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.cip_peru_selected import MAPPING
from scripts.cip_peru_table12 import run, checksum, FIELDS

CONTROLS = ["Ccompis", "CIP380389.1", "CIP391691.96", "CIP720064"]
CLONES = [f"CIP{312500+i:06d}.001" for i in range(30)]


def generate(folder, mutate_raw=None, mutate_subset=None):
    root = Path(folder)
    cols = ["ORD", "INSTN", "BREEDERCODE"]
    for _, count, mean, sd, mi, ma, _ in MAPPING:
        cols += [count, mean, sd, mi, ma]
    source = []
    for number, accession in enumerate(CLONES + CONTROLS, 1):
        row = {"ORD": f"{number}.0", "INSTN": accession,
               "BREEDERCODE": "TEST-" + accession}
        for trait, n, m, sd, low, high, unit in MAPPING:
            row.update({n: "10", m: "20.4" if trait == "iron" else "12.2",
                        sd: "2.1", low: "10.0", high: "30.0"})
        source.append(row)
    # Four truly blank lines in the authentic structural positions.
    for kind in ("blank", "Prom", "Max", "Min", "blank", "blank", "blank"):
        row = dict.fromkeys(cols, "")
        if kind != "blank":
            row["nFEDW"] = row["nZNDW"] = kind
        source.append(row)
    if mutate_raw:
        mutate_raw(source)
    tsv = root / "table12_synthetic.tsv"
    with tsv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=cols, delimiter="\t")
        writer.writeheader()
        writer.writerows(source)
    subset = []
    for row in source:
        if row["INSTN"] not in set(CLONES[:12] + CONTROLS[-2:]):
            continue
        for trait, count, mean, sd, mi, ma, unit in MAPPING:
            subset.append({
                "accession": row["INSTN"], "breeder_code": row["BREEDERCODE"],
                "nutrient": trait, "unit": unit,
                "reported_n": row[count], "published_mean": row[mean],
                "published_sd": row[sd], "published_min": row[mi],
                "published_max": row[ma], "source_doi": "10.21223/N11QJS",
                "data_level": "published_multi_location_aggregate"
            })
    if mutate_subset:
        mutate_subset(subset)
    headers = [
        "accession", "breeder_code", "nutrient", "unit", "reported_n",
        "published_mean", "published_sd", "published_min", "published_max",
        "source_doi", "data_level"
    ]
    csvpath = root / "subset.csv"
    with csvpath.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(subset)
    manifest = root / "subset_manifest.json"
    manifest.write_text(json.dumps({
        "source_doi": "10.21223/N11QJS", "file_id": 6979,
        "accessions": 14, "nutrient_rows": 28,
        "derived_csv_sha256": checksum(csvpath)
    }), encoding="utf-8")
    return tsv, csvpath, manifest


class PeruTable12Tests(unittest.TestCase):
    def test_real_structure_synthetic_statistics_and_overlap_not_new_replicates(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, subset, meta = generate(td)
            output = Path(td) / "normalized"
            report = run(tsv, output, subset, meta, checksum(tsv))
            self.assertEqual(report["materials"], 34)
            self.assertEqual(report["evaluated_clones"], 30)
            self.assertEqual(report["controls"], 4)
            self.assertEqual(report["mineral_summary_rows"], 68)
            self.assertEqual(report["statistics_overlapping_table16"], 28)
            self.assertEqual(report["materials_overlapping_table16"], 14)
            self.assertEqual(report["materials_not_in_table16"], 20)
            self.assertEqual(report["excluded_nonmaterial_rows"], 7)
            with (output / "peru_table12_fe_zn_summaries.csv").open() as stream:
                records = list(csv.DictReader(stream))
            self.assertEqual(list(records[0].keys()), FIELDS)
            self.assertEqual(sum(r["also_in_table16_same_statistic"] == "true" for r in records), 28)
            self.assertEqual(sum(r["material_role"] == "commercial_control" for r in records), 8)
            self.assertTrue(all(r["data_level"] == "published_program_aggregate_not_plot" for r in records))
            with (output / "peru_table12_nonmaterials.csv").open() as stream:
                excluded = list(csv.DictReader(stream))
            self.assertEqual([int(x["source_tsv_line"]) for x in excluded], list(range(36, 43)))
            self.assertEqual(sum(x["row_type"] == "global_summary_not_genotype" for x in excluded), 3)

    def test_source_hash_mismatch_refused(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, subset, meta = generate(td)
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                run(tsv, Path(td) / "out", subset, meta)

    def test_duplicate_material_id_refused_even_if_source_hash_updated(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, subset, meta = generate(td, mutate_raw=lambda rows:
                                         rows[20].__setitem__("INSTN", rows[21]["INSTN"]))
            with self.assertRaisesRegex(ValueError, "repeated"):
                run(tsv, Path(td) / "out", subset, meta, checksum(tsv))

    def test_footer_label_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, subset, meta = generate(td, mutate_raw=lambda rows:
                                         rows[35].__setitem__("nZNDW", "Mean"))
            with self.assertRaisesRegex(ValueError, "summary labels"):
                run(tsv, Path(td) / "out", subset, meta, checksum(tsv))

    def test_summary_conflict_refused_even_with_resigned_test_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, subset, meta = generate(td, mutate_subset=lambda rows:
                                         rows[0].__setitem__("published_mean", "19.1"))
            with self.assertRaisesRegex(ValueError, "discordant"):
                run(tsv, Path(td) / "out", subset, meta, checksum(tsv))

    def test_noninteger_reported_n_refused(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, subset, meta = generate(td, mutate_raw=lambda rows:
                                         rows[24].__setitem__("nZNDW", "8.5"))
            with self.assertRaisesRegex(ValueError, "reasonable integer"):
                run(tsv, Path(td) / "out", subset, meta, checksum(tsv))

    def test_no_missing_aggregate_imputation(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, subset, meta = generate(td, mutate_raw=lambda rows:
                                         rows[24].__setitem__("MeanZNDW", ""))
            with self.assertRaisesRegex(ValueError, "missing"):
                run(tsv, Path(td) / "out", subset, meta, checksum(tsv))


if __name__ == "__main__":
    unittest.main()
