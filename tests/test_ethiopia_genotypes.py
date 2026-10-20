"""Offline validity tests using synthetic (NEVER scientific) Table-2-shaped JATS."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from scripts.ethiopia_genotypes import execute, read_rows, sha256


def synthetic_xml(path: Path, *, wrong_doi=False, lost_row=False, duplicate=False):
    root=ET.Element("article")
    ET.SubElement(root,"article-id",{"pub-id-type":"doi"}).text=(
        "10.9999/fake" if wrong_doi else "10.3390/plants12142625")
    wrap=ET.SubElement(root,"table-wrap",{"id":"plants-12-02625-t002"})
    table=ET.SubElement(wrap,"table")
    head=ET.SubElement(table,"tr")
    for value in ("Genotypes","AvTN","AvTW","TY","DMC","SG","STC","Fe","Zn"):
        ET.SubElement(head,"th").text=value
    names=[f"CIP{111111+i:06d}.001" for i in range(42)]
    names+=["Gudanie","CIP312767.014","CIP312735.062"]
    if lost_row: names.pop(0)
    if duplicate: names[0]=names[1]
    for i,name in enumerate(names):
        tr=ET.SubElement(table,"tr")
        for j,val in enumerate((
            name,"8","25","1.50" if name!="Gudanie" else "1.91",
            "25","1.1","19",
            "26.07" if name=="CIP312767.014" else "14.68" if name=="Gudanie" else "19",
            "19.14" if name=="CIP312767.014" else "10.22" if name=="Gudanie" else "13",
        )):
            if name=="CIP312735.062" and j==3: val="2.26"
            cell=ET.SubElement(tr,"td")
            cell.text=val
            if j and j in (3,7,8):
                ET.SubElement(cell,"sup").text="ab"
    for label in ("Range","Mean"):
        tr=ET.SubElement(table,"tr")
        ET.SubElement(tr,"td").text=label
        for k in range(8): ET.SubElement(tr,"td").text="1"
    path.write_bytes(ET.tostring(root,encoding="utf-8"))


class GenotypeXMLTests(unittest.TestCase):
    def test_parsing_real_anchor_values_and_pareto(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"synthetic.xml"
            synthetic_xml(p)
            result=execute(p,Path(directory)/"out",expected_sha=sha256(p))
            self.assertEqual(result["genotypes"],45)
            with (Path(directory)/"out"/"genotype_trial_holetta_2019.csv").open() as f:
                rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),45)
            self.assertIn("true",{r["pareto_yield_iron_zinc"] for r in rows})
            self.assertEqual(next(r for r in rows if r["genotype"]=="Gudanie")["iron_mg_kg_dry"],"14.68")
            self.assertIn("single-site", result["design"])

    def test_does_not_accept_modified_source(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"synthetic.xml";synthetic_xml(p)
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                read_rows(p)

    def test_cannot_switch_article(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"synthetic.xml";synthetic_xml(p,wrong_doi=True)
            with self.assertRaisesRegex(ValueError,"DOI"):
                read_rows(p,expected_sha=sha256(p))

    def test_incomplete_genotype_table_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"synthetic.xml";synthetic_xml(p,lost_row=True)
            with self.assertRaisesRegex(ValueError,"45 unique"):
                read_rows(p,expected_sha=sha256(p))

    def test_duplicate_genotype_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"synthetic.xml";synthetic_xml(p,duplicate=True)
            with self.assertRaisesRegex(ValueError,"45 unique"):
                read_rows(p,expected_sha=sha256(p))

    def test_dimension_conversion(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"synthetic.xml";synthetic_xml(p)
            rows=read_rows(p,expected_sha=sha256(p))
            gudanie=next(r for r in rows if r["genotype"]=="Gudanie")
            from decimal import Decimal
            # 1.91kg fresh/m² × 25% DM × 14.68 mg/kg(DM) × 10 = g/ha
            expected=Decimal("1.91")*Decimal("0.25")*Decimal("14.68")*Decimal("10")
            self.assertEqual(Decimal(gudanie["iron_g_ha_theoretical"]),expected)


if __name__=="__main__":
    unittest.main()
