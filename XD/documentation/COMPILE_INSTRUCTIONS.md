# Thesis Compilation Instructions

## 📋 Overview

This guide explains how to compile the complete FarmMe thesis from individual Markdown chapters into a single, formatted document suitable for MIT submission.

---

## 🎯 Compilation Options

### Option 1: Pandoc (Recommended for PDF)

**Requirements:**
- Pandoc 2.19+
- LaTeX distribution (TeX Live or MiKTeX)
- Python 3.8+ (for preprocessing)

**Steps:**

1. **Install Pandoc**
```bash
# Windows (using Chocolatey)
choco install pandoc

# macOS (using Homebrew)
brew install pandoc

# Linux (Ubuntu/Debian)
sudo apt-get install pandoc
```

2. **Install LaTeX**
```bash
# Windows
choco install miktex

# macOS
brew install --cask mactex

# Linux
sudo apt-get install texlive-full
```

3. **Compile to PDF**
```bash
cd documentation

pandoc \
  00_Abstract_ExecutiveSummary.md \
  00_Table_of_Contents.md \
  Chapter1_Introduction.md \
  Chapter2_Data_Generation_Detailed.md \
  Chapter3_Background_RelatedWork.md \
  Chapter4_Model_A_CropRecommendation.md \
  Chapter5_Model_B_PlantingWindow.md \
  Chapter6_Model_C_PriceForecasting.md \
  Chapter7_Model_D_HarvestDecision.md \
  Chapter8_System_Integration.md \
  Chapter9_Experimental_Results.md \
  Chapter10_Discussion.md \
  Chapter11_Conclusion.md \
  -o FarmMe_Thesis.pdf \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V fontsize=12pt \
  -V documentclass=report \
  --highlight-style=tango
```

---

### Option 2: Microsoft Word (Easiest)

**Requirements:**
- Microsoft Word 2016+
- Pandoc (optional, for better formatting)

**Method A: Direct Pandoc Conversion**
```bash
cd documentation

pandoc \
  00_Abstract_ExecutiveSummary.md \
  Chapter1_Introduction.md \
  Chapter2_Data_Generation_Detailed.md \
  Chapter3_Background_RelatedWork.md \
  Chapter4_Model_A_CropRecommendation.md \
  Chapter5_Model_B_PlantingWindow.md \
  Chapter6_Model_C_PriceForecasting.md \
  Chapter7_Model_D_HarvestDecision.md \
  Chapter8_System_Integration.md \
  Chapter9_Experimental_Results.md \
  Chapter10_Discussion.md \
  Chapter11_Conclusion.md \
  -o FarmMe_Thesis.docx \
  --toc \
  --number-sections \
  --reference-doc=mit_thesis_template.docx
```

**Method B: Manual Copy-Paste**
1. Open each chapter in a Markdown viewer
2. Copy content to Word document
3. Apply MIT thesis template formatting
4. Add page numbers and headers
5. Generate table of contents

---

### Option 3: LaTeX (Most Professional)

**Requirements:**
- LaTeX distribution
- MIT thesis LaTeX template

**Steps:**

1. **Download MIT Thesis Template**
```bash
# Clone MIT thesis template
git clone https://github.com/mit-thesis/mit-thesis-template.git
cd mit-thesis-template
```

2. **Convert Markdown to LaTeX**
```bash
cd ../documentation

# Convert each chapter
for file in Chapter*.md; do
  pandoc "$file" -o "${file%.md}.tex" --standalone
done
```

3. **Integrate into MIT Template**
- Copy generated .tex files to template directory
- Update main.tex to include chapters
- Compile with pdflatex or xelatex

4. **Compile**
```bash
cd mit-thesis-template
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

---

## 📐 Formatting Guidelines

### MIT Thesis Requirements

**Page Layout:**
- Margins: 1 inch on all sides
- Font: 12pt, Times New Roman or similar
- Line spacing: Double-spaced (except for tables, figures, and code)
- Page numbers: Bottom center, starting from introduction

**Front Matter:**
1. Title page (no page number)
2. Abstract (page ii)
3. Acknowledgments (page iii)
4. Table of Contents (page iv)
5. List of Figures (page v)
6. List of Tables (page vi)

**Main Content:**
- Chapters numbered 1, 2, 3, etc.
- Sections numbered 1.1, 1.2, etc.
- Subsections numbered 1.1.1, 1.1.2, etc.

**Back Matter:**
- Appendices (A, B, C, etc.)
- Bibliography
- Index (optional)

---

## 🎨 Custom Styling

### Create Custom Pandoc Template

**File: `mit_thesis_template.tex`**

```latex
\documentclass[12pt,oneside]{report}

% Packages
\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}
\usepackage{setspace}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{xcolor}

% Double spacing
\doublespacing

% Code highlighting
\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  frame=single,
  numbers=left,
  numberstyle=\tiny,
  backgroundcolor=\color{gray!10}
}

% Title page
\title{FarmMe: An Integrated Machine Learning System for Agricultural Decision Support}
\author{Your Name}
\date{November 2025}

\begin{document}

% Front matter
\maketitle
\pagenumbering{roman}
\tableofcontents
\listoffigures
\listoftables

% Main content
\pagenumbering{arabic}
$body$

\end{document}
```

**Usage:**
```bash
pandoc chapters.md -o thesis.pdf --template=mit_thesis_template.tex
```

---

## 🖼️ Adding Figures and Tables

### Figure Placement

**In Markdown:**
```markdown
![Figure Caption](../outputs/figures/model_a_performance.png){width=80%}
```

**In LaTeX:**
```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\textwidth]{../outputs/figures/model_a_performance.png}
  \caption{Model A Performance Comparison}
  \label{fig:model_a_performance}
\end{figure}
```

### Table Formatting

**In Markdown:**
```markdown
| Model | R² | MAE | RMSE |
|-------|-----|-----|------|
| Model A | 0.9944 | 2.15 | 3.42 |
| Baseline | 0.3512 | 7.89 | 12.34 |
```

---

## 🔧 Troubleshooting

### Common Issues

**Issue 1: Pandoc not found**
```bash
# Verify installation
pandoc --version

# Add to PATH if needed (Windows)
setx PATH "%PATH%;C:\Program Files\Pandoc"
```

**Issue 2: LaTeX compilation errors**
```bash
# Install missing packages
tlmgr install <package-name>

# Or install full distribution
sudo apt-get install texlive-full
```

**Issue 3: Unicode characters not rendering**
```bash
# Use XeLaTeX instead of pdflatex
pandoc input.md -o output.pdf --pdf-engine=xelatex
```

**Issue 4: Code blocks not formatted correctly**
```bash
# Add syntax highlighting
pandoc input.md -o output.pdf --highlight-style=tango
```

---

## 📦 Pre-compiled Versions

### Quick Compilation Script

**File: `compile_thesis.sh`** (Linux/macOS)
```bash
#!/bin/bash

echo "Compiling FarmMe Thesis..."

# Combine all chapters
cat \
  00_Abstract_ExecutiveSummary.md \
  Chapter1_Introduction.md \
  Chapter2_Data_Generation_Detailed.md \
  Chapter3_Background_RelatedWork.md \
  Chapter4_Model_A_CropRecommendation.md \
  Chapter5_Model_B_PlantingWindow.md \
  Chapter6_Model_C_PriceForecasting.md \
  Chapter7_Model_D_HarvestDecision.md \
  Chapter8_System_Integration.md \
  Chapter9_Experimental_Results.md \
  Chapter10_Discussion.md \
  Chapter11_Conclusion.md \
  > FarmMe_Thesis_Combined.md

# Compile to PDF
pandoc FarmMe_Thesis_Combined.md \
  -o FarmMe_Thesis.pdf \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V fontsize=12pt \
  -V documentclass=report \
  --highlight-style=tango

# Compile to DOCX
pandoc FarmMe_Thesis_Combined.md \
  -o FarmMe_Thesis.docx \
  --toc \
  --number-sections

echo "Compilation complete!"
echo "PDF: FarmMe_Thesis.pdf"
echo "DOCX: FarmMe_Thesis.docx"
```

**File: `compile_thesis.bat`** (Windows)
```batch
@echo off
echo Compiling FarmMe Thesis...

REM Combine all chapters
type ^
  00_Abstract_ExecutiveSummary.md ^
  Chapter1_Introduction.md ^
  Chapter2_Data_Generation_Detailed.md ^
  Chapter3_Background_RelatedWork.md ^
  Chapter4_Model_A_CropRecommendation.md ^
  Chapter5_Model_B_PlantingWindow.md ^
  Chapter6_Model_C_PriceForecasting.md ^
  Chapter7_Model_D_HarvestDecision.md ^
  Chapter8_System_Integration.md ^
  Chapter9_Experimental_Results.md ^
  Chapter10_Discussion.md ^
  Chapter11_Conclusion.md ^
  > FarmMe_Thesis_Combined.md

REM Compile to PDF
pandoc FarmMe_Thesis_Combined.md ^
  -o FarmMe_Thesis.pdf ^
  --toc ^
  --toc-depth=3 ^
  --number-sections ^
  --pdf-engine=xelatex ^
  -V geometry:margin=1in ^
  -V fontsize=12pt ^
  -V documentclass=report ^
  --highlight-style=tango

REM Compile to DOCX
pandoc FarmMe_Thesis_Combined.md ^
  -o FarmMe_Thesis.docx ^
  --toc ^
  --number-sections

echo Compilation complete!
echo PDF: FarmMe_Thesis.pdf
echo DOCX: FarmMe_Thesis.docx
pause
```

**Usage:**
```bash
# Linux/macOS
chmod +x compile_thesis.sh
./compile_thesis.sh

# Windows
compile_thesis.bat
```

---

## ✅ Final Checklist

Before submission, verify:

- [ ] All chapters included in correct order
- [ ] Page numbers correct (roman for front matter, arabic for main content)
- [ ] Table of contents matches chapter structure
- [ ] All figures have captions and are referenced in text
- [ ] All tables have captions and are referenced in text
- [ ] All citations formatted correctly
- [ ] Bibliography complete
- [ ] Appendices included
- [ ] No orphaned headings (heading at bottom of page)
- [ ] No widowed lines (single line at top of page)
- [ ] Consistent formatting throughout
- [ ] Spell check completed
- [ ] Grammar check completed
- [ ] MIT formatting requirements met

---

## 📚 Additional Resources

### MIT Thesis Guidelines
- https://libraries.mit.edu/distinctive-collections/thesis-specs/

### Pandoc Documentation
- https://pandoc.org/MANUAL.html

### LaTeX Resources
- https://www.overleaf.com/learn

### Markdown Guide
- https://www.markdownguide.org/

---

**Last Updated**: November 2025  
**Version**: 1.0
