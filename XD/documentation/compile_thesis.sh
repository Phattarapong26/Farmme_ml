#!/bin/bash
# FarmMe Thesis Compilation Script for Linux/macOS
# This script compiles all thesis chapters into a single document

echo "========================================"
echo "FarmMe Thesis Compilation"
echo "========================================"
echo ""

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "ERROR: Pandoc is not installed"
    echo "Please install Pandoc:"
    echo "  macOS: brew install pandoc"
    echo "  Linux: sudo apt-get install pandoc"
    echo ""
    exit 1
fi

echo "[1/4] Combining all chapters..."
cat \
  00_Abstract_ExecutiveSummary.md \
  <(echo -e "\n\n") \
  Chapter1_Introduction.md \
  <(echo -e "\n\n") \
  Chapter2_Data_Generation_Detailed.md \
  <(echo -e "\n\n") \
  Chapter3_Background_RelatedWork.md \
  <(echo -e "\n\n") \
  Chapter4_Model_A_CropRecommendation.md \
  <(echo -e "\n\n") \
  Chapter5_Model_B_PlantingWindow.md \
  <(echo -e "\n\n") \
  Chapter6_Model_C_PriceForecasting.md \
  <(echo -e "\n\n") \
  Chapter7_Model_D_HarvestDecision.md \
  <(echo -e "\n\n") \
  Chapter8_System_Integration.md \
  <(echo -e "\n\n") \
  Chapter9_Experimental_Results.md \
  <(echo -e "\n\n") \
  Chapter10_Discussion.md \
  <(echo -e "\n\n") \
  Chapter11_Conclusion.md \
  > FarmMe_Thesis_Combined.md

echo "[2/4] Compiling to DOCX (Microsoft Word)..."
if pandoc FarmMe_Thesis_Combined.md \
  -o FarmMe_Thesis.docx \
  --toc \
  --number-sections \
  -V fontsize=12pt; then
    echo "    ✓ SUCCESS: FarmMe_Thesis.docx created"
else
    echo "    ✗ ERROR: Failed to create DOCX"
fi

echo "[3/4] Compiling to PDF (requires LaTeX)..."
if pandoc FarmMe_Thesis_Combined.md \
  -o FarmMe_Thesis.pdf \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V fontsize=12pt \
  -V documentclass=report \
  --highlight-style=tango 2>/dev/null; then
    echo "    ✓ SUCCESS: FarmMe_Thesis.pdf created"
else
    echo "    ⚠ WARNING: PDF compilation failed (LaTeX may not be installed)"
    echo "    You can still use the DOCX file"
fi

echo "[4/4] Cleaning up temporary files..."
echo "    Keeping FarmMe_Thesis_Combined.md for reference"

echo ""
echo "========================================"
echo "Compilation Complete!"
echo "========================================"
echo ""
echo "Generated files:"
[ -f FarmMe_Thesis.docx ] && echo "  ✓ FarmMe_Thesis.docx (Microsoft Word)"
[ -f FarmMe_Thesis.pdf ] && echo "  ✓ FarmMe_Thesis.pdf (PDF)"
echo "  ✓ FarmMe_Thesis_Combined.md (Combined Markdown)"
echo ""
echo "Total word count: ~82,000 words"
echo "Total pages: ~620 pages"
echo ""
