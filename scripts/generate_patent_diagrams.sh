#!/bin/bash
# Script to Generate Patent-Quality Diagrams from Mermaid Source Files
# این اسکریپت دیاگرام‌های Mermaid را به فرمت‌های مناسب برای Patent Drawings تبدیل می‌کند

echo "====================================="
echo "  Patent Diagrams Generator"
echo "====================================="
echo ""

# Configuration
OUTPUT_DIR="docs/PATENT_DRAWINGS/exports"
SOURCE_DIR="docs/PATENT_DRAWINGS"
RESOLUTION="2400x1800"
DPI=600

# Create output directory
mkdir -p "$OUTPUT_DIR"/{svg,png,pdf}

# Check if mermaid-cli is installed
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

# Function to convert Mermaid file
convert_mermaid() {
    local input_file=$1
    local figure_name=$2
    
    if [ ! -f "$input_file" ]; then
        echo "⚠️  File not found: $input_file"
        return 1
    fi
    
    echo "📊 Processing: $figure_name"
    
    # Extract Mermaid code from markdown file
    # (Assuming Mermaid code is between ```mermaid and ```)
    sed -n '/```mermaid/,/```/p' "$input_file" | sed '1d;$d' > "/tmp/${figure_name}.mmd"
    
    if [ ! -s "/tmp/${figure_name}.mmd" ]; then
        echo "   ⚠️  No Mermaid code found in file"
        return 1
    fi
    
    # Convert to SVG
    echo "   → Converting to SVG..."
    mmdc -i "/tmp/${figure_name}.mmd" \
         -o "$OUTPUT_DIR/svg/${figure_name}.svg" \
         -b white \
         -w 2400 \
         -H 1800 \
         -s 2
    
    if [ $? -eq 0 ]; then
        echo "   ✅ SVG generated: $OUTPUT_DIR/svg/${figure_name}.svg"
    else
        echo "   ❌ Failed to generate SVG"
    fi
    
    # Convert to PNG (High Resolution)
    echo "   → Converting to PNG (High Resolution)..."
    mmdc -i "/tmp/${figure_name}.mmd" \
         -o "$OUTPUT_DIR/png/${figure_name}.png" \
         -b white \
         -w 3600 \
         -H 2700 \
         -s 3
    
    if [ $? -eq 0 ]; then
        echo "   ✅ PNG generated: $OUTPUT_DIR/png/${figure_name}.png"
    else
        echo "   ❌ Failed to generate PNG"
    fi
    
    # Cleanup
    rm -f "/tmp/${figure_name}.mmd"
    
    echo ""
}

# Process all figure files
echo "🔄 Processing Patent Diagram Files..."
echo ""

# Figure 1: System Architecture
if [ -f "$SOURCE_DIR/Figure_1_System_Architecture.md" ]; then
    convert_mermaid "$SOURCE_DIR/Figure_1_System_Architecture.md" "Figure_1_System_Architecture"
fi

# Figure 2: Neural Network Architecture
if [ -f "$SOURCE_DIR/Figure_2_Neural_Network_Architecture.md" ]; then
    convert_mermaid "$SOURCE_DIR/Figure_2_Neural_Network_Architecture.md" "Figure_2_Neural_Network"
fi

# Figure 3: Data Fusion System
if [ -f "$SOURCE_DIR/Figure_3_Data_Fusion_System.md" ]; then
    convert_mermaid "$SOURCE_DIR/Figure_3_Data_Fusion_System.md" "Figure_3_Data_Fusion"
fi

# Figure 4: Clinical Workflow
if [ -f "$SOURCE_DIR/Figure_4_Clinical_Workflow.md" ]; then
    convert_mermaid "$SOURCE_DIR/Figure_4_Clinical_Workflow.md" "Figure_4_Clinical_Workflow"
fi

echo "====================================="
echo "  ✅ Generation Complete!"
echo "====================================="
echo ""
echo "📁 Output Directory: $OUTPUT_DIR"
echo ""
echo "Generated Files:"
echo "  - SVG files: $OUTPUT_DIR/svg/"
echo "  - PNG files: $OUTPUT_DIR/png/"
echo ""
echo "Next Steps:"
echo "  1. Import SVG/PNG files to Illustrator/Inkscape"
echo "  2. Add Reference Numerals"
echo "  3. Enhance and finalize"
echo "  4. Export to TIFF/PDF for Patent submission"
echo ""

