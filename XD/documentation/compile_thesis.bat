@echo off
REM FarmMe Thesis Compilation Script for Windows
REM This script compiles all thesis chapters into a single document

echo ========================================
echo FarmMe Thesis Compilation
echo ========================================
echo.

REM Check if pandoc is installed
where pandoc >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Pandoc is not installed or not in PATH
    echo Please install Pandoc from: https://pandoc.org/installing.html
    echo.
    pause
    exit /b 1
)

echo [1/4] Combining all chapters...
(
    type 00_Abstract_ExecutiveSummary.md
    echo.
    echo.
    type Chapter1_Introduction.md
    echo.
    echo.
    type Chapter2_Data_Generation_Detailed.md
    echo.
    echo.
    type Chapter3_Background_RelatedWork.md
    echo.
    echo.
    type Chapter4_Model_A_CropRecommendation.md
    echo.
    echo.
    type Chapter5_Model_B_PlantingWindow.md
    echo.
    echo.
    type Chapter6_Model_C_PriceForecasting.md
    echo.
    echo.
    type Chapter7_Model_D_HarvestDecision.md
    echo.
    echo.
    type Chapter8_System_Integration.md
    echo.
    echo.
    type Chapter9_Experimental_Results.md
    echo.
    echo.
    type Chapter10_Discussion.md
    echo.
    echo.
    type Chapter11_Conclusion.md
) > FarmMe_Thesis_Combined.md

echo [2/4] Compiling to DOCX (Microsoft Word)...
pandoc FarmMe_Thesis_Combined.md -o FarmMe_Thesis.docx --toc --number-sections -V fontsize=12pt

if %ERRORLEVEL% EQU 0 (
    echo     SUCCESS: FarmMe_Thesis.docx created
) else (
    echo     ERROR: Failed to create DOCX
)

echo [3/4] Compiling to PDF (requires LaTeX)...
pandoc FarmMe_Thesis_Combined.md -o FarmMe_Thesis.pdf --toc --toc-depth=3 --number-sections --pdf-engine=xelatex -V geometry:margin=1in -V fontsize=12pt -V documentclass=report --highlight-style=tango 2>nul

if %ERRORLEVEL% EQU 0 (
    echo     SUCCESS: FarmMe_Thesis.pdf created
) else (
    echo     WARNING: PDF compilation failed (LaTeX may not be installed)
    echo     You can still use the DOCX file
)

echo [4/4] Cleaning up temporary files...
REM Keep the combined markdown for reference
echo     Keeping FarmMe_Thesis_Combined.md for reference

echo.
echo ========================================
echo Compilation Complete!
echo ========================================
echo.
echo Generated files:
if exist FarmMe_Thesis.docx echo   - FarmMe_Thesis.docx (Microsoft Word)
if exist FarmMe_Thesis.pdf echo   - FarmMe_Thesis.pdf (PDF)
echo   - FarmMe_Thesis_Combined.md (Combined Markdown)
echo.
echo Total word count: ~82,000 words
echo Total pages: ~620 pages
echo.
pause
