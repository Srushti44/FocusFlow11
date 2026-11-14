# ACLI Educational Text Complexity Dataset (v1.0.0)

## 1. Overview & Provenance
- **Dataset Version**: `1.0.0`
- **Domain**: Multidisciplinary Educational & Informational Texts (Cognitive Psychology, Computer Science, Biology, Environmental Science, History, Economics, and Classical Literature).
- **Sources**: Open Educational Resources (OER Commons, Wikimedia Foundation / Wikipedia Educational, Project Gutenberg, and CC BY-SA 4.0 Open Textbook Library).
- **License**: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) / Public Domain.
- **Granularity**: Paragraph-level units (50 to 140 words per unit, reflecting realistic educational prose).

## 2. Label Definitions & Rubric
The Adaptive Cognitive Load Index (ACLI) 4-class taxonomy models structural and lexical readability:

| Class | Target Grade Band | Typical Sentence Length | Syllables / Word | Syntactic Structure | Example Focus |
|---|---|---|---|---|---|
| **Easy** | Grades 4–6 (Primary) | 8–14 words | 1.1–1.3 | Coordinate clauses, active voice, everyday vocabulary | Foundational nature stories, simple instructional texts |
| **Medium** | Grades 7–9 (Middle School) | 14–20 words | 1.3–1.5 | Introductory subordinate clauses, expository phrasing | General science explanations, standard encyclopedic prose |
| **Hard** | Grades 10–12 (High School/Intro College) | 20–28 words | 1.5–1.8 | Multiple dependent clauses, domain terminology | Textbook chapters, analytical journalism, historical analysis |
| **Very Hard** | University / Graduate / Academic | 28+ words | 1.8–2.3+ | Dense nominalizations, recursive embedding, high jargon | Peer-reviewed journals, theoretical philosophy, legal/cognitive treatises |

## 3. Data Leakage Prevention Strategy
Paragraphs are tagged with a unique `document_id`. The dataset validation and training splitters strictly perform **Group-based Stratified Document Splitting** (`GroupShuffleSplit` / `GroupKFold` by `document_id`). Paragraphs originating from the same article or book chapter never cross between training, validation, or test sets.

## 4. Known Limitations
1. **Linguistic Scope**: English-only educational text.
2. **Construct Validity**: The model measures *text-level linguistic complexity* (syntax, vocabulary, clause density). It does **not** measure a human learner's internal cognitive state, real-time working memory, or attention span, and must never be used for medical or cognitive diagnosis.
3. **Domain Variance**: High jargon density in specialized domains (e.g. quantum mechanics) can produce high difficulty ratings despite short sentence lengths.
