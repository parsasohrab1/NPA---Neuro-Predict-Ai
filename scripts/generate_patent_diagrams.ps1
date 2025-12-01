# PowerShell Script to Generate Patent-Quality Diagrams
# این اسکریپت دیاگرام‌های Mermaid را به فرمت‌های مناسب تبدیل می‌کند

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Patent Diagrams Generator" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$OutputDir = "docs\PATENT_DRAWINGS\exports"
$SourceDir = "docs\PATENT_DRAWINGS"

# Create output directories
$null = New-Item -ItemType Directory -Force -Path "$OutputDir\svg"
$null = New-Item -ItemType Directory -Force -Path "$OutputDir\png"
$null = New-Item -ItemType Directory -Force -Path "$OutputDir\pdf"

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Check if mermaid-cli is installed
try {
    $mmdcVersion = mmdc --version 2>&1
    Write-Host "✅ Mermaid CLI found" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Mermaid CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g @mermaid-js/mermaid-cli
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Mermaid CLI" -ForegroundColor Red
        Write-Host "   Please install manually: npm install -g @mermaid-js/mermaid-cli" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""

# Function to extract Mermaid code from markdown
function Extract-MermaidCode {
    param (
        [string]$FilePath
    )
    
    $content = Get-Content $FilePath -Raw
    $pattern = '(?s)```mermaid(.*?)```'
    $matches = [regex]::Matches($content, $pattern)
    
    if ($matches.Count -gt 0) {
        return $matches[0].Groups[1].Value.Trim()
    }
    
    return $null
}

# Function to convert Mermaid file
function Convert-MermaidDiagram {
    param (
        [string]$InputFile,
        [string]$FigureName
    )
    
    if (-not (Test-Path $InputFile)) {
        Write-Host "⚠️  File not found: $InputFile" -ForegroundColor Yellow
        return
    }
    
    Write-Host "📊 Processing: $FigureName" -ForegroundColor Cyan
    
    # Extract Mermaid code
    $mermaidCode = Extract-MermaidCode -FilePath $InputFile
    
    if ([string]::IsNullOrWhiteSpace($mermaidCode)) {
        Write-Host "   ⚠️  No Mermaid code found" -ForegroundColor Yellow
        return
    }
    
    # Save to temporary file
    $tempFile = "$env:TEMP\$FigureName.mmd"
    $mermaidCode | Out-File -FilePath $tempFile -Encoding UTF8
    
    # Convert to SVG
    Write-Host "   → Converting to SVG..." -ForegroundColor Gray
    mmdc -i $tempFile `
         -o "$OutputDir\svg\$FigureName.svg" `
         -b white `
         -w 2400 `
         -H 1800 `
         -s 2
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ SVG generated" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Failed to generate SVG" -ForegroundColor Red
    }
    
    # Convert to PNG
    Write-Host "   → Converting to PNG (High Resolution)..." -ForegroundColor Gray
    mmdc -i $tempFile `
         -o "$OutputDir\png\$FigureName.png" `
         -b white `
         -w 3600 `
         -H 2700 `
         -s 3
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ PNG generated" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Failed to generate PNG" -ForegroundColor Red
    }
    
    # Cleanup
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    
    Write-Host ""
}

# Process all figure files
Write-Host "🔄 Processing Patent Diagram Files..." -ForegroundColor Yellow
Write-Host ""

# Figure 1: System Architecture
$fig1 = "$SourceDir\Figure_1_System_Architecture.md"
if (Test-Path $fig1) {
    Convert-MermaidDiagram -InputFile $fig1 -FigureName "Figure_1_System_Architecture"
}

# Figure 2: Neural Network Architecture
$fig2 = "$SourceDir\Figure_2_Neural_Network_Architecture.md"
if (Test-Path $fig2) {
    Convert-MermaidDiagram -InputFile $fig2 -FigureName "Figure_2_Neural_Network"
}

# Figure 3: Data Fusion System
$fig3 = "$SourceDir\Figure_3_Data_Fusion_System.md"
if (Test-Path $fig3) {
    Convert-MermaidDiagram -InputFile $fig3 -FigureName "Figure_3_Data_Fusion"
}

# Figure 4: Clinical Workflow
$fig4 = "$SourceDir\Figure_4_Clinical_Workflow.md"
if (Test-Path $fig4) {
    Convert-MermaidDiagram -InputFile $fig4 -FigureName "Figure_4_Clinical_Workflow"
}

Write-Host "=====================================" -ForegroundColor Green
Write-Host "  ✅ Generation Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Output Directory: $OutputDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Generated Files:" -ForegroundColor Yellow
Write-Host "  - SVG files: $OutputDir\svg\" -ForegroundColor White
Write-Host "  - PNG files: $OutputDir\png\" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Import SVG/PNG files to Illustrator/Inkscape" -ForegroundColor White
Write-Host "  2. Add Reference Numerals (100, 110, 120, etc.)" -ForegroundColor White
Write-Host "  3. Enhance and finalize according to USPTO standards" -ForegroundColor White
Write-Host "  4. Export to TIFF/PDF (600 DPI) for Patent submission" -ForegroundColor White
Write-Host ""

