import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PIPELINE_DIR = ROOT / "12_pipeline"
sys.path.insert(0, str(PIPELINE_DIR))

SPEC = importlib.util.spec_from_file_location(
    "run_pipeline_under_test",
    PIPELINE_DIR / "run_pipeline.py",
)
run_pipeline = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(run_pipeline)


class LectureTexFormatterTest(unittest.TestCase):
    def test_expands_compact_lecture_tex(self) -> None:
        compact = (
            r"\begin{summarybox} \textbf{\textcolor{CSummary}{Core}} "
            r"Keep the heading readable. \medskip "
            r"\textbf{\textcolor{CSummary}{Conditions}} "
            r"\begin{itemize}[leftmargin=*] "
            r"\item \textbf{Condition:} use $a>b>0$. "
            r"\item \textbf{Formula:} \[ "
            r"\frac{x^{2}}{a^{2}+\lambda}+\frac{y^{2}}{b^{2}+\lambda}=1, "
            r"\qquad \lambda\neq -a^{2},-b^{2}. "
            r"\] \end{itemize} \end{summarybox}"
        )

        formatted = run_pipeline.format_lecture_tex_snippet(compact)
        lines = formatted.splitlines()

        self.assertGreater(len(lines), 10)
        self.assertIn(r"\begin{summarybox}", lines[0])
        self.assertIn("\t" + r"\textbf{\textcolor{CSummary}{Core}}", lines)
        self.assertTrue(any(line.startswith("\t\t" + r"\item ") for line in lines))
        self.assertIn("\t\t\t" + r"\[", lines)
        self.assertIn("\t\t\t" + r"\]", lines)
        self.assertLess(max(len(line) for line in lines), 120)


if __name__ == "__main__":
    unittest.main()
