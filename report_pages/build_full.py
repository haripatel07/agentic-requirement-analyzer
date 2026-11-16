"""Assemble report_full.tex: report.tex with updated chapters 3-6 and natural spacing.

Only used to regenerate the TOC/LoF and pages after chapter 1; front matter and
chapter 1 pages are taken from the original submitted PDF.
"""
import re, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
src = (root / "report.tex").read_text()
P = lambda n: (root / "report_pages" / n).read_text()

def body(name, start, end=r"\end{document}"):
    s = P(name)
    s = s[s.index(start):s.index(end)]
    s = re.sub(r"\\vspace\{[^}]*\}(\\enlargethispage\{[^}]*\})?\n", "", s)
    s = re.sub(r"\\enlargethispage\{[^}]*\}\n", "", s)
    s = re.sub(r"\\setcounter\{[^}]*\}(\\setcounter\{[^}]*\})*\n", "", s)
    s = re.sub(r"\\setcounter\{[^}]*\}\n", "", s)
    s = re.sub(r"^\\(pre|post)\s*\n", "", s, flags=re.M)
    s = re.sub(r"^\\setcounter\{.*\n", "", s, flags=re.M)
    s = re.sub(r"^\\clearpage\n", "", s, flags=re.M)
    s = re.sub(r"^%.*\n", "", s, flags=re.M)
    return s.strip() + "\n\n"

def cut(text, a, b):
    i = text.index(a); j = text.index(b, i)
    return text[:i], text[i:j], text[j:]

# front matter stub: keep preamble, replace everything up to \tableofcontents
pre, _, rest = cut(src, r"\begin{document}", r"\tableofcontents")
pre += "\\input{metrics.tex}\n"
front = r"""\begin{document}
\pagestyle{fancy}
\pagenumbering{roman}
\setcounter{page}{6}
\addtocontents{toc}{\protect\contentsline {chapter}{Company / Organization Certificate}{ii}{}}
\addtocontents{toc}{\protect\contentsline {chapter}{Declaration by the Candidate}{iii}{}}
\addtocontents{toc}{\protect\contentsline {chapter}{Acknowledgement}{iv}{}}
\addtocontents{toc}{\protect\contentsline {chapter}{Abstract}{v}{}}
"""
doc = pre + front + rest

# chapter 1: add 1.6 Internship Timeline (present in the submitted PDF, missing from report.tex)
timeline = r"""\section{Internship Timeline}
The four-week internship followed the same progressive order reflected in this
report: requirement understanding first, followed by architecture,
implementation, integration and testing.

\begin{table}[H]
\centering
\caption{Week-by-Week Internship Timeline}
\label{tab:timeline}
\begin{tabularx}{\textwidth}{|p{2.2cm}|X|}
\hline
\textbf{Week} & \textbf{Work Completed} \\
\hline
Week 1 & Studied the problem domain, finalized project objectives, prepared sample requirement documents and established the backend/frontend development environment. \\
\hline
Week 2 & Implemented document parsing, requirement extraction and functional/non-functional classification with structured JSON contracts. \\
\hline
Week 3 & Added user-story generation, Given/When/Then acceptance criteria, Sentence-Transformers embeddings and FAISS-based ambiguity detection. \\
\hline
Week 4 & Integrated FastAPI endpoints, React report rendering, SQLite run persistence, automated tests, execution verification and technical documentation. \\
\hline
\end{tabularx}
\end{table}

"""
i = doc.index("% ==================== CHAPTER 2")
doc = doc[:i] + timeline + doc[i:]

# chapter 2: technology stack row
doc = doc.replace("Orchestration & Sequential pipeline with LangGraph-compatible design \\\\",
                  "Orchestration & LangGraph \\texttt{StateGraph} (six nodes, linear edges) \\\\")
doc = doc.replace("Language Model & Groq API (llama-3.3-70b-versatile) \\\\",
                  "Language Model & Groq API (llama-3.3-70b-versatile; openai/gpt-oss-120b for the final test runs) \\\\")

# chapter 3
a, _, c = cut(doc, r"\chapter{SYSTEM ARCHITECTURE}", r"% ==================== CHAPTER 4")
ch3 = "\\chapter{SYSTEM ARCHITECTURE}\n\n" + body("pages_a.tex", r"\section{Pipeline Overview}") + "\\FloatBarrier\n\n"
doc = a + ch3 + c

# chapter 4: keep 4.1-4.3 from report.tex, new 4.4-4.8, fig 4.1
a, old4, c = cut(doc, r"\chapter{IMPLEMENTATION}", r"% ==================== CHAPTER 5")
keep = old4[:old4.index(r"\section{Risk and Ambiguity Detection Agent}")]
ch4 = keep + body("pages_b.tex", r"\section{Risk and Ambiguity Detection Agent}") + body("pages_e.tex", r"\begin{figure}") + "\\FloatBarrier\n\n"
doc = a + ch4 + c

# chapter 5
a, old5, c = cut(doc, r"\chapter{RESULTS AND TESTING}", r"% ==================== CHAPTER 6")
keep = old5[:old5.index(r"\section{Observations}")]
new = body("pages_c.tex", r"\begin{table}[H]")
new = new.replace("(Section 4.5)", "(Section~\\ref{sec:review})")
doc = a + keep + new + "\\FloatBarrier\n\n" + c

# chapter 6 + references
a, _, c = cut(doc, r"\chapter{CONCLUSION AND FUTURE SCOPE}", r"% ==================== REFERENCES")
doc = a + "\\chapter{CONCLUSION AND FUTURE SCOPE}\n\n" + body("pages_d.tex", r"\section{Conclusion}") + c
refs_new = r"""\item React Documentation, \url{https://react.dev/}
\item Tailwind CSS Documentation, \url{https://tailwindcss.com/docs}
\item SQLite Documentation, \url{https://www.sqlite.org/docs.html}
\item Pydantic Documentation, \url{https://docs.pydantic.dev/}
\item OpenAPI Specification, \url{https://spec.openapis.org/oas/latest.html}
\item Python Documentation, \url{https://docs.python.org/3/}
\item OWASP File Upload Cheat Sheet, \url{https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html}
\item OWASP API Security Top 10, \url{https://owasp.org/API-Security/}
\item NIST AI Risk Management Framework, \url{https://www.nist.gov/itl/ai-risk-management-framework}
"""
doc = doc.replace("\\end{enumerate}\n\n\\end{document}", refs_new + "\\end{enumerate}\n\n\\end{document}")
doc = doc.replace(r"\section{Technical Code Review Findings}", r"\section{Technical Code Review Findings}\label{sec:review}")
(root / "report_pages" / "report_full.tex").write_text(doc)
print("ok", len(doc))
