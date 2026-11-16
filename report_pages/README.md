# Replacement report pages

Source for the report pages that were rewritten and merged into the submitted PDF
(PDF pages 13-15, 17-19, 21-24). Each `pages_*.tex` page was matched to the original
line positions with `compare_pages.py`.

Build (needs a LaTeX engine, e.g. tectonic):

    ln -s ../assets assets
    tectonic -X compile pages_a.tex   # likewise b, c, d, e

`metrics.tex` holds the Table 5.1 values measured with `openai/gpt-oss-120b` on Groq.

## Full-body build

`build_full.py` assembles `report_full.tex` (natural spacing, regenerated TOC/List of Figures).
The submitted PDF uses its original pages 1-6 and 10-11 plus pages 1-3 and 6-18 of this build.
