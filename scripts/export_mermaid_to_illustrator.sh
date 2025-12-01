#!/bin/bash
# اسکریپت تبدیل Mermaid به فرمت‌های قابل استفاده در Illustrator
# Export Mermaid Diagrams to Illustrator-Compatible Formats

# Default values
FIGURE_NAME=""
ALL=false
OUTPUT_FORMAT="svg"  # svg, png, pdf, all
DPI=600
WIDTH=2400
HEIGHT=1800

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --figure|-f)
            FIGURE_NAME="$2"
            shift 2
            ;;
        --all|-a)
            ALL=true
            shift
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --dpi)
            DPI="$2"
            shift 2
            ;;
        --width)
            WIDTH="$2"
            shift 2
            ;;
        --height)
            HEIGHT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -f, --figure NAME    Export specific figure (e.g., Figure_1_System_Architecture)"
            echo "  -a, --all            Export all figures"
            echo "  --format FORMAT      Output format: svg, png, pdf, all (default: svg)"
            echo "  --dpi DPI            DPI for raster formats (default: 600)"
            echo "  --width WIDTH        Width for SVG (default: 2400)"
            echo "  --height HEIGHT      Height for SVG (default: 1800)"
            echo "  -h, --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo ""
echo "============================================================"
echo "  🎨 Mermaid to Illustrator Export Tool"
echo "============================================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
SOURCE_DIR="$PROJECT_ROOT/docs/PATENT_DRAWINGS"
OUTPUT_BASE_DIR="$PROJECT_ROOT/docs/PATENT_DRAWINGS/exports"
TEMP_DIR="/tmp/mermaid_exports_$$"

# Create output directories
mkdir -p "$OUTPUT_BASE_DIR"/{svg,png,pdf,illustrator}
mkdir -p "$TEMP_DIR"

echo "📁 Output Directory: $OUTPUT_BASE_DIR"
echo ""

# Check if Mermaid CLI is installed
if ! command -v mmdc &> /dev/null; then
    echo "⚠️  Mermaid CLI not found. Installing..."
    npm install -g @mermaid-js/mermaid-cli
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Mermaid CLI"
        echo "   Please install manually: npm install -g @mermaid-js/mermaid-cli"
        exit 1
    fi
fi

echo "✅ Mermaid CLI found"
echo ""

# Function to extract Mermaid code from markdown
extract_mermaid_code() {
    local file_path=$1
    sed -n '/```mermaid/,/```/p' "$file_path" | sed '1d;$d'
}

# Function to export single figure
export_figure() {
    local input_file=$1
    local figure_name=$2
    local format=$3
    
    echo "📊 Processing: $figure_name"
    
    # Extract Mermaid code
    local mermaid_code=$(extract_mermaid_code "$input_file")
    
    if [ -z "$mermaid_code" ]; then
        echo "   ⚠️  No Mermaid code found"
        return 1
    fi
    
    # Save to temporary file
    local temp_file="$TEMP_DIR/${figure_name}.mmd"
    echo "$mermaid_code" > "$temp_file"
    
    local success=true
    
    case "$format" in
        svg)
            echo "   → Exporting to SVG (Illustrator-ready)..."
            mmdc -i "$temp_file" \
                 -o "$OUTPUT_BASE_DIR/svg/${figure_name}.svg" \
                 -b white \
                 -w $WIDTH \
                 -H $HEIGHT \
                 -s 2
            
            if [ $? -eq 0 ]; then
                echo "   ✅ SVG exported successfully"
                echo "      File: exports/svg/${figure_name}.svg"
            else
                echo "   ❌ SVG export failed"
                success=false
            fi
            ;;
            
        png)
            echo "   → Exporting to PNG (High Resolution)..."
            
            # Calculate PNG dimensions based on DPI
            local png_width=$((8 * DPI + 4 * DPI / 10))  # 8.5 inches
            local png_height=$((11 * DPI))
            
            mmdc -i "$temp_file" \
                 -o "$OUTPUT_BASE_DIR/png/${figure_name}.png" \
                 -b white \
                 -w $png_width \
                 -H $png_height \
                 -s 3
            
            if [ $? -eq 0 ]; then
                echo "   ✅ PNG exported successfully"
                echo "      File: exports/png/${figure_name}.png (${png_width} × ${png_height} px @ ${DPI} DPI)"
            else
                echo "   ❌ PNG export failed"
                success=false
            fi
            ;;
            
        pdf)
            echo "   → Exporting to PDF..."
            
            local png_width=$((8 * DPI + 4 * DPI / 10))
            local png_height=$((11 * DPI))
            local png_file="$TEMP_DIR/${figure_name}.pdf_temp.png"
            local pdf_file="$OUTPUT_BASE_DIR/pdf/${figure_name}.pdf"
            
            mmdc -i "$temp_file" \
                 -o "$png_file" \
                 -b white \
                 -w $png_width \
                 -H $png_height \
                 -s 3
            
            if [ $? -eq 0 ]; then
                # Convert PNG to PDF using ImageMagick or convert
                if command -v convert &> /dev/null; then
                    convert "$png_file" -quality 100 "$pdf_file"
                    echo "   ✅ PDF exported successfully"
                elif command -v magick &> /dev/null; then
                    magick "$png_file" -quality 100 "$pdf_file"
                    echo "   ✅ PDF exported successfully"
                else
                    echo "   ⚠️  ImageMagick not found. PDF conversion skipped."
                    echo "      Install ImageMagick for PDF export: https://imagemagick.org/"
                fi
            else
                echo "   ❌ PDF export failed"
                success=false
            fi
            ;;
            
        all)
            export_figure "$input_file" "$figure_name" "svg"
            export_figure "$input_file" "$figure_name" "png"
            export_figure "$input_file" "$figure_name" "pdf"
            ;;
    esac
    
    # Cleanup
    rm -f "$temp_file"
    
    if [ "$success" = true ]; then
        return 0
    else
        return 1
    fi
}

# Find all figure files
FIGURE_FILES=()

if [ "$ALL" = true ] || [ -z "$FIGURE_NAME" ]; then
    # Get all figure markdown files
    while IFS= read -r file; do
        FIGURE_FILES+=("$file")
    done < <(find "$SOURCE_DIR" -name "Figure_*.md" -type f)
    
    echo "📋 Found ${#FIGURE_FILES[@]} figure files"
else
    # Single figure
    FIGURE_PATH="$SOURCE_DIR/${FIGURE_NAME}.md"
    if [ -f "$FIGURE_PATH" ]; then
        FIGURE_FILES=("$FIGURE_PATH")
    else
        echo "❌ Figure file not found: $FIGURE_PATH"
        exit 1
    fi
fi

echo ""

# Process each figure
SUCCESS_COUNT=0
FAIL_COUNT=0

for figure_file in "${FIGURE_FILES[@]}"; do
    echo "────────────────────────────────────────────────────────"
    
    figure_name=$(basename "$figure_file" .md)
    
    if export_figure "$figure_file" "$figure_name" "$OUTPUT_FORMAT"; then
        ((SUCCESS_COUNT++))
    else
        ((FAIL_COUNT++))
    fi
    
    echo ""
done

# Summary
echo "============================================================"
echo "  ✅ Export Complete!"
echo "============================================================"
echo ""
echo "📊 Summary:"
echo "   Success: $SUCCESS_COUNT"
echo "   Failed:  $FAIL_COUNT"
echo ""
echo "📁 Output Location:"
echo "   $OUTPUT_BASE_DIR"
echo ""
echo "🎨 Next Steps:"
echo "   1. Open SVG files in Adobe Illustrator"
echo "   2. Create new document: 8.5\" × 11\""
echo "   3. Place SVG file and scale to fit"
echo "   4. Add Reference Numerals and enhance"
echo "   5. Export to TIFF (600 DPI) for Patent submission"
echo ""

# Cleanup
rm -rf "$TEMP_DIR"

