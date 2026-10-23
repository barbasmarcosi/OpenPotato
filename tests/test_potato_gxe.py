"""G × E analytical properties using SYNTHETIC matrices (never scientific observations)."""
import csv
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from scripts.potato_gxe import read_matrix, analyze, filehash

SCHEMA=["rownames","yield","gen","variety","env","loc","year"]
GENS=[("G1","A"),("G2","B"),("G3","C"),("G4","D"),
      ("G5","E"),("G6","F"),("G7","Katahdin"),("G8","Sebago")]
ENVS=[("E1","NB","65"),("E2","NB","66"),("E3","NS","65"),
      ("E4","NS","66"),("E5","PEI","65"),("E6","PEI","66")]


def fixture(path,modify=None):
    rows=[]
    for k,(gen,variety) in enumerate(GENS):
        for j,(env,loc,year) in enumerate(ENVS):
            # Nonparallel G×E pattern; data are deliberately invented for tests.
            value=Decimal(10+k+j)+Decimal((k*j)%7)/10
            rows.append([len(rows)+1,str(value),gen,variety,env,loc,year])
    if modify: modify(rows)
    with Path(path).open("w",newline="") as output:
        writer=csv.writer(output);writer.writerow(SCHEMA);writer.writerows(rows)


class TestMultiEnvironment(unittest.TestCase):
    def test_all_cells_balanced_and_decomposition_identity(self):
        with tempfile.TemporaryDirectory() as t:
            src=Path(t)/"synthetic.csv";fixture(src)
            matrix, gens,envs=read_matrix(src)
            self.assertEqual(len(matrix),48)
            self.assertEqual(len(gens),8)
            self.assertEqual(len(envs),6)
            result=analyze(src,Path(t)/"out",pinned_sha256=filehash(src))
            components=sum(Decimal(result[f"{k}_sum_squares"]) for k in
                           ("genotype","environment","interaction"))
            self.assertLess(abs(components-Decimal(result["total_sum_squares"])), Decimal("1e-20"))
            self.assertEqual(result["genotypes"],8)
            self.assertTrue(result["no_residual_variance_estimate"])

    def test_incomplete_grid_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"s.csv";fixture(p,lambda rows:rows.pop())
            with self.assertRaisesRegex(ValueError,"48"):
                read_matrix(p)

    def test_same_genotype_environment_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"s.csv"
            def change(rows):
                rows[3][3]="E1"; rows[3][4]="NB"; rows[3][5]="65"
            # Explicitly inject duplicate env identity, with matching metadata.
            fixture(p,lambda rows:(rows[3].__setitem__(4,"E1"),
                                    rows[3].__setitem__(5,"NB"),
                                    rows[3].__setitem__(6,"65")))
            with self.assertRaisesRegex(ValueError,"Duplicated"):
                read_matrix(p)

    def test_identity_conflict_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"s.csv"
            fixture(p,lambda rows:rows[2].__setitem__(3,"impostor"))
            with self.assertRaisesRegex(ValueError,"Contradictory"):
                read_matrix(p)

    def test_nonnumeric_or_missing_does_not_become_zero(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"s.csv";fixture(p,lambda rows:rows[4].__setitem__(1,""))
            with self.assertRaisesRegex(ValueError,"numeric"):
                read_matrix(p)

    def test_source_checksum_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"s.csv";fixture(p)
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                analyze(p,Path(t)/"out",pinned_sha256="0"*64)

    def test_no_fabricated_individual_replicates_or_minerals(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"s.csv";fixture(p)
            report=analyze(p,Path(t)/"out",pinned_sha256=filehash(p))
            self.assertIn("NO Fe/Zn",report["trait"])
            self.assertTrue(report["no_residual_variance_estimate"])
            text=(Path(t)/"out"/"gxE_report.md").read_text()
            self.assertIn("no permite decir nada sobre G×E de hierro y zinc",text)
            self.assertIn("no se calculan valores p",text)


if __name__=="__main__":
    unittest.main()
