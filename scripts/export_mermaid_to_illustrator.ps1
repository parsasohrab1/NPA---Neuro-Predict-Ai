# اسکریپت تبدیل Mermaid به فرمت‌های قابل استفاده در Illustrator
# Export Mermaid Diagrams to Illustrator-Compatible Formats

param(
    [string]$FigureName = "",
    [switch]$All = $false,
    [string]$OutputFormat = "svg",  # svg, png, pdf, all
    [int]$DPI = 600,
    [int]$Width = 2400,
    [int]$Height = 1800
)

Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "  🎨 Mermaid to Illustrator Export Tool" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

# Configuration
$SourceDir = Join-Path $PSScriptRoot "..\docs\PATENT_DRAWINGS"
$OutputBaseDir = Join-Path $PSScriptRoot "..\docs\PATENT_DRAWINGS\exports"
$TempDir = Join-Path $env:TEMP "mermaid_exports"

# Create output directories
$outputDirs = @("svg", "png", "pdf", "illustrator")
foreach ($dir in $outputDirs) {
    $path = Join-Path $OutputBaseDir $dir
    New-Item -ItemType Directory -Force -Path $path | Out-Null
}

New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

Write-Host "📁 Output Directory: $OutputBaseDir" -ForegroundColor Gray
Write-Host ""

# Check if Mermaid CLI is installed
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

# Function to extract Mermaid code from markdown
function Extract-MermaidCode {
    param ([string]$FilePath)
    
    $content = Get-Content $FilePath -Raw -Encoding UTF8
    $pattern = '(?s)```mermaid(.*?)```'
    $matches = [regex]::Matches($content, $pattern)
    
    if ($matches.Count -gt 0) {
        return $matches[0].Groups[1].Value.Trim()
    }
    
    return $null
}

# Function to export single figure
function Export-Figure {
    param (
        [string]$InputFile,
        [string]$FigureName,
        [string]$Format,
        [int]$DPI,
        [int]$Width,
        [int]$Height
    )
    
    Write-Host "📊 Processing: $FigureName" -ForegroundColor Cyan
    
    # Extract Mermaid code
    $mermaidCode = Extract-MermaidCode -FilePath $InputFile
    
    if ([string]::IsNullOrWhiteSpace($mermaidCode)) {
        Write-Host "   ⚠️  No Mermaid code found" -ForegroundColor Yellow
        return $false
    }
    
    # Save to temporary file
    $tempFile = Join-Path $TempDir "$FigureName.mmd"
    $mermaidCode | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline
    
    $success = $true
    
    # Export based on format
    switch ($Format.ToLower()) {
        "svg" {
            Write-Host "   → Exporting to SVG (Illustrator-ready)..." -ForegroundColor Gray
            
            # SVG with high quality settings
            mmdc -i $tempFile `
                 -o (Join-Path $OutputBaseDir "svg\$FigureName.svg") `
                 -b white `
                 -w $Width `
                 -H $Height `
                 -s 2 `
                 --puppeteerConfigFile (Join-Path $PSScriptRoot "..\mermaid_config.json") `
                 --cssFile (Join-Path $PSScriptRoot "..\mermaid_style.css")
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ SVG exported successfully" -ForegroundColor Green
                Write-Host "      File: exports\svg\$FigureName.svg" -ForegroundColor Gray
            } else {
                Write-Host "   ❌ SVG export failed" -ForegroundColor Red
                $success = $false
            }
        }
        
        "png" {
            Write-Host "   → Exporting to PNG (High Resolution)..." -ForegroundColor Gray
            
            # Calculate PNG dimensions based on DPI
            $pngWidth = [math]::Round(8.5 * $DPI)  # 8.5 inches at specified DPI
            $pngHeight = [math]::Round(11 * $DPI)   # 11 inches at specified DPI
            
            mmdc -i $tempFile `
                 -o (Join-Path $OutputBaseDir "png\$FigureName.png") `
                 -b white `
                 -w $pngWidth `
                 -H $pngHeight `
                 -s 3
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ PNG exported successfully" -ForegroundColor Green
                Write-Host "      File: exports\png\$FigureName.png ($pngWidth × $pngHeight px @ $DPI DPI)" -ForegroundColor Gray
            } else {
                Write-Host "   ❌ PNG export failed" -ForegroundColor Red
                $success = $false
            }
        }
        
        "pdf" {
            Write-Host "   → Exporting to PDF..." -ForegroundColor Gray
            
            # First export to PNG, then convert to PDF
            $pngFile = Join-Path $TempDir "$FigureName.pdf_temp.png"
            $pdfFile = Join-Path $OutputBaseDir "pdf\$FigureName.pdf"
            
            $pngWidth = [math]::Round(8.5 * $DPI)
            $pngHeight = [math]::Round(11 * $DPI)
            
            mmdc -i $tempFile `
                 -o $pngFile `
                 -b white `
                 -w $pngWidth `
                 -H $pngHeight `
                 -s 3
            
            if ($LASTEXITCODE -eq 0) {
                # Convert PNG to PDF using ImageMagick if available
                try {
                    magick $pngFile -quality 100 $pdfFile
                    Write-Host "   ✅ PDF exported successfully" -ForegroundColor Green
                } catch {
                    Write-Host "   ⚠️  ImageMagick not found. PDF conversion skipped." -ForegroundColor Yellow
                    Write-Host "      Install ImageMagick for PDF export: https://imagemagick.org/" -ForegroundColor Gray
                }
            } else {
                Write-Host "   ❌ PDF export failed" -ForegroundColor Red
                $success = $false
            }
        }
        
        "all" {
            # Export to all formats
            Export-Figure -InputFile $InputFile -FigureName $FigureName -Format "svg" -DPI $DPI -Width $Width -Height $Height
            Export-Figure -InputFile $InputFile -FigureName $FigureName -Format "png" -DPI $DPI -Width $Width -Height $Height
            Export-Figure -InputFile $InputFile -FigureName $FigureName -Format "pdf" -DPI $DPI -Width $Width -Height $Height
        }
    }
    
    # Cleanup
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    
    return $success
}

# Find all figure files
$figureFiles = @()

if ($All) {
    # Get all figure markdown files
    $figureFiles = Get-ChildItem -Path $SourceDir -Filter "Figure_*.md" | ForEach-Object {
        @{
            Name = $_.BaseName
            Path = $_.FullName
        }
    }
    Write-Host "📋 Found $($figureFiles.Count) figure files" -ForegroundColor Cyan
} elseif (-not [string]::IsNullOrWhiteSpace($FigureName)) {
    # Single figure
    $figurePath = Join-Path $SourceDir "$FigureName.md"
    if (Test-Path $figurePath) {
        $figureFiles = @(@{
            Name = $FigureName
            Path = $figurePath
        })
    } else {
        Write-Host "❌ Figure file not found: $figurePath" -ForegroundColor Red
        exit 1
    }
} else {
    # Default: export all
    $figureFiles = Get-ChildItem -Path $SourceDir -Filter "Figure_*.md" | ForEach-Object {
        @{
            Name = $_.BaseName
            Path = $_.FullName
        }
    }
    Write-Host "📋 No figure specified. Processing all figures..." -ForegroundColor Cyan
}

Write-Host ""

# Process each figure
$successCount = 0
$failCount = 0

foreach ($figure in $figureFiles) {
    Write-Host "────────────────────────────────────────────────────────" -ForegroundColor Gray
    
    $success = Export-Figure `
        -InputFile $figure.Path `
        -FigureName $figure.Name `
        -Format $OutputFormat `
        -DPI $DPI `
        -Width $Width `
        -Height $Height
    
    if ($success) {
        $successCount++
    } else {
        $failCount++
    }
    
    Write-Host ""
}

# Summary
Write-Host "="*80 -ForegroundColor Green
Write-Host "  ✅ Export Complete!" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   Success: $successCount" -ForegroundColor Green
Write-Host "   Failed:  $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host ""
Write-Host "📁 Output Location:" -ForegroundColor Cyan
Write-Host "   $OutputBaseDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎨 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Open SVG files in Adobe Illustrator" -ForegroundColor White
Write-Host "   2. Create new document: 8.5\" × 11\"" -ForegroundColor White
Write-Host "   3. Place SVG file and scale to fit" -ForegroundColor White
Write-Host "   4. Add Reference Numerals and enhance" -ForegroundColor White
Write-Host "   5. Export to TIFF (600 DPI) for Patent submission" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   - Complete Guide: docs/PATENT_DRAWINGS/COMPLETE_CONVERSION_GUIDE.md" -ForegroundColor White
Write-Host "   - Step-by-Step: docs/PATENT_DRAWINGS/STEP_BY_STEP_TUTORIAL.md" -ForegroundColor White
Write-Host ""

# Cleanup temp directory
Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue

