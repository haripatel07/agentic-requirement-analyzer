# Replacement report pages

Source for the report pages that were rewritten and merged into the submitted PDF
(PDF pages 13-15, 17-19, 21-24). Each `pages_*.tex` page was matched to the original
line positions with `compare_pages.py`.

Build (needs a LaTeX engine, e.g. tectonic):

    ln -s ../assets assets
    tectonic -X compile pages_a.tex   # likewise b, c, d, e

`metrics.tex` holds the Table 5.1 values measured with `openai/gpt-oss-120b` on Groq.
