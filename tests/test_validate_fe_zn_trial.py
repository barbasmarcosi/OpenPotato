"""Synthetic admissions only; NO real CIP genotype × environment data claimed."""
import csv
import tempfile
import unittest
from pathlib import Path
from scripts.validate_fe_zn_trial import FIELDS,inspect


def write(path, mutation=None):
    rows=[]
    for location in ("CIP-L1","CIP-L2"):
        for gen in ("CLONE-001","CLONE-002","CLONE-003"):
            for block in ("B1","B2"):
                for trait in ("iron","zinc","tuber_yield"):
                    rows.append({
                        "trial_id":"SYNTHETIC-NOT-SCIENCE",
                        "genotype_id":gen,
                        "location_id":location,
                        "season_id":"2019",
                        "block_id":block,
                        "plot_id":f"{location}_{gen}_{block}",
                        "trait":trait,
                        "value":"20.0" if trait!="tuber_yield" else "5.0",
                        "unit":"mg/kg_dry" if trait!="tuber_yield" else "kg/plot_fresh",
                        "processing":"raw",
                        "tissue":"peeled_flesh" if trait!="tuber_yield" else "whole_tuber",
                        "plot_area_m2":"2.5",
                        "source_id":"SYNTHETIC-SOURCE",
                    })
    if mutation:mutation(rows)
    with open(path,"w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=sorted(FIELDS));writer.writeheader();writer.writerows(rows)


class QualityGate(unittest.TestCase):
    def test_valid_paired_plot_data_only_signals_review(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"synthetic.csv";write(p)
            report=inspect(p)
            self.assertEqual(report["environments"],2)
            self.assertEqual(report["genotypes"],3)
            self.assertEqual(report["biological_plots"],12)
            self.assertEqual(report["numeric_observations"],36)
            self.assertTrue(report["no_statistical_model_fitted"])

    def test_rejects_unpaired_chemistry(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"synthetic.csv";write(p,lambda rows:rows.pop())
            with self.assertRaisesRegex(ValueError,"Incomplete paired"):
                inspect(p)

    def test_rejects_misrepresented_fresh_dry(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"synthetic.csv";write(p,lambda rows:rows[0].__setitem__("unit","mg/kg_fresh"))
            with self.assertRaisesRegex(ValueError,"units/basis"):
                inspect(p)

    def test_rejects_missing_replicate(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"synthetic.csv"
            def omit(rows):
                rows[:]=[r for r in rows if not (r["location_id"]=="CIP-L1" and
                             r["genotype_id"]=="CLONE-001" and r["block_id"]=="B2")]
            write(p,omit)
            with self.assertRaisesRegex(ValueError,"biological plot replicates"):
                inspect(p)

    def test_rejects_pseudoreplicated_duplicate(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"synthetic.csv";write(p,lambda rows:rows.append(rows[0].copy()))
            with self.assertRaisesRegex(ValueError,"Duplicate plot-trait"):
                inspect(p)

    def test_rejects_one_location(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"synthetic.csv"
            write(p,lambda rows:rows.__setitem__(slice(None),
                [r for r in rows if r["location_id"]=="CIP-L1"]))
            with self.assertRaisesRegex(ValueError,"distinct locations"):
                inspect(p)

    def test_rejects_changed_plot_area_within_same_plot(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"synthetic.csv"
            write(p,lambda rows:rows[0].__setitem__("plot_area_m2","5"))
            with self.assertRaisesRegex(ValueError,"Inconsistent plot area"):
                inspect(p)

    def test_same_physical_plot_cannot_belong_to_two_genotypes(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"synthetic.csv"
            def collide(rows):
                plot=rows[0]["plot_id"]  # CLONE-001 block B1, environment L1
                for row in rows[6:9]:   # CLONE-002 block B1, same environment
                    row["plot_id"]=plot
            write(p,collide)
            with self.assertRaisesRegex(ValueError,"Physical plot assigned to different genotypes"):
                inspect(p)

    def test_malformed_extra_column_rejected_before_plot_analysis(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"synthetic.csv"
            write(p)
            with p.open("a", encoding="utf-8") as stream:
                stream.write(",".join(["INVALID"]*(len(FIELDS)+1))+"\\n")
            with self.assertRaisesRegex(ValueError,"Malformed CSV row"):
                inspect(p)

    def test_malformed_missing_column_rejected_before_plot_analysis(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"synthetic.csv"
            write(p)
            with p.open("a", encoding="utf-8") as stream:
                stream.write("TRUNCATED_RECORD\\n")
            with self.assertRaisesRegex(ValueError,"Malformed CSV row"):
                inspect(p)

if __name__=="__main__":
    unittest.main()
