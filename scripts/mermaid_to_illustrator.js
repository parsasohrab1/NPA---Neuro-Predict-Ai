/**
 * Node.js Script for Exporting Mermaid Diagrams to Illustrator-Compatible Formats
 * اسکریپت Node.js برای خروجی گرفتن از Mermaid به فرمت‌های قابل استفاده در Illustrator
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const config = {
    sourceDir: path.join(__dirname, '..', 'docs', 'PATENT_DRAWINGS'),
    outputBaseDir: path.join(__dirname, '..', 'docs', 'PATENT_DRAWINGS', 'exports'),
    tempDir: path.join(require('os').tmpdir(), 'mermaid_exports'),
    formats: {
        svg: { width: 2400, height: 1800, scale: 2 },
        png: { dpi: 600, scale: 3 },
        pdf: { dpi: 600, scale: 3 }
    }
};

// Create output directories
const outputDirs = ['svg', 'png', 'pdf', 'illustrator'];
outputDirs.forEach(dir => {
    const dirPath = path.join(config.outputBaseDir, dir);
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
});

// Create temp directory
if (!fs.existsSync(config.tempDir)) {
    fs.mkdirSync(config.tempDir, { recursive: true });
}

/**
 * Check if Mermaid CLI is installed
 */
function checkMermaidCLI() {
    try {
        execSync('mmdc --version', { stdio: 'ignore' });
        return true;
    } catch (error) {
        console.log('⚠️  Mermaid CLI not found. Installing...');
        try {
            execSync('npm install -g @mermaid-js/mermaid-cli', { stdio: 'inherit' });
            return true;
        } catch (installError) {
            console.error('❌ Failed to install Mermaid CLI');
            console.error('   Please install manually: npm install -g @mermaid-js/mermaid-cli');
            return false;
        }
    }
}

/**
 * Extract Mermaid code from markdown file
 */
function extractMermaidCode(filePath) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const mermaidPattern = /```mermaid([\s\S]*?)```/;
    const match = content.match(mermaidPattern);
    
    if (match && match[1]) {
        return match[1].trim();
    }
    
    return null;
}

/**
 * Export figure to SVG
 */
function exportToSVG(mermaidFile, outputFile, width, height, scale) {
    try {
        execSync(
            `mmdc -i "${mermaidFile}" -o "${outputFile}" -b white -w ${width} -H ${height} -s ${scale}`,
            { stdio: 'inherit' }
        );
        return true;
    } catch (error) {
        return false;
    }
}

/**
 * Export figure to PNG
 */
function exportToPNG(mermaidFile, outputFile, dpi, scale) {
    const width = Math.round(8.5 * dpi);  // 8.5 inches
    const height = Math.round(11 * dpi);   // 11 inches
    
    try {
        execSync(
            `mmdc -i "${mermaidFile}" -o "${outputFile}" -b white -w ${width} -H ${height} -s ${scale}`,
            { stdio: 'inherit' }
        );
        return { success: true, width, height };
    } catch (error) {
        return { success: false };
    }
}

/**
 * Export figure to PDF (via PNG conversion)
 */
function exportToPDF(mermaidFile, outputFile, dpi, scale) {
    const tempPng = path.join(config.tempDir, path.basename(outputFile, '.pdf') + '.png');
    
    // First export to PNG
    const pngResult = exportToPNG(mermaidFile, tempPng, dpi, scale);
    
    if (!pngResult.success) {
        return false;
    }
    
    // Convert PNG to PDF using ImageMagick if available
    try {
        execSync(`magick "${tempPng}" -quality 100 "${outputFile}"`, { stdio: 'ignore' });
        fs.unlinkSync(tempPng); // Cleanup temp file
        return true;
    } catch (error) {
        // Try convert command (older ImageMagick)
        try {
            execSync(`convert "${tempPng}" -quality 100 "${outputFile}"`, { stdio: 'ignore' });
            fs.unlinkSync(tempPng);
            return true;
        } catch (convertError) {
            console.log('   ⚠️  ImageMagick not found. PDF conversion skipped.');
            console.log('      Install ImageMagick for PDF export: https://imagemagick.org/');
            if (fs.existsSync(tempPng)) {
                fs.unlinkSync(tempPng);
            }
            return false;
        }
    }
}

/**
 * Export a single figure
 */
function exportFigure(figurePath, figureName, format) {
    console.log(`📊 Processing: ${figureName}`);
    
    // Extract Mermaid code
    const mermaidCode = extractMermaidCode(figurePath);
    
    if (!mermaidCode) {
        console.log('   ⚠️  No Mermaid code found');
        return false;
    }
    
    // Save to temporary file
    const tempFile = path.join(config.tempDir, `${figureName}.mmd`);
    fs.writeFileSync(tempFile, mermaidCode, 'utf-8');
    
    let success = false;
    
    switch (format.toLowerCase()) {
        case 'svg':
            console.log('   → Exporting to SVG (Illustrator-ready)...');
            success = exportToSVG(
                tempFile,
                path.join(config.outputBaseDir, 'svg', `${figureName}.svg`),
                config.formats.svg.width,
                config.formats.svg.height,
                config.formats.svg.scale
            );
            if (success) {
                console.log('   ✅ SVG exported successfully');
                console.log(`      File: exports/svg/${figureName}.svg`);
            } else {
                console.log('   ❌ SVG export failed');
            }
            break;
            
        case 'png':
            console.log('   → Exporting to PNG (High Resolution)...');
            const pngResult = exportToPNG(
                tempFile,
                path.join(config.outputBaseDir, 'png', `${figureName}.png`),
                config.formats.png.dpi,
                config.formats.png.scale
            );
            success = pngResult.success;
            if (success) {
                console.log('   ✅ PNG exported successfully');
                console.log(`      File: exports/png/${figureName}.png (${pngResult.width} × ${pngResult.height} px @ ${config.formats.png.dpi} DPI)`);
            } else {
                console.log('   ❌ PNG export failed');
            }
            break;
            
        case 'pdf':
            console.log('   → Exporting to PDF...');
            success = exportToPDF(
                tempFile,
                path.join(config.outputBaseDir, 'pdf', `${figureName}.pdf`),
                config.formats.pdf.dpi,
                config.formats.pdf.scale
            );
            if (success) {
                console.log('   ✅ PDF exported successfully');
                console.log(`      File: exports/pdf/${figureName}.pdf`);
            } else {
                console.log('   ❌ PDF export failed');
            }
            break;
            
        case 'all':
            // Export to all formats
            exportFigure(figurePath, figureName, 'svg');
            exportFigure(figurePath, figureName, 'png');
            exportFigure(figurePath, figureName, 'pdf');
            success = true;
            break;
            
        default:
            console.log(`   ❌ Unknown format: ${format}`);
            success = false;
    }
    
    // Cleanup
    if (fs.existsSync(tempFile)) {
        fs.unlinkSync(tempFile);
    }
    
    return success;
}

/**
 * Main function
 */
function main() {
    const args = process.argv.slice(2);
    let figureName = '';
    let all = false;
    let format = 'svg';
    
    // Parse arguments
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--figure':
            case '-f':
                figureName = args[++i];
                break;
            case '--all':
            case '-a':
                all = true;
                break;
            case '--format':
                format = args[++i];
                break;
            case '--help':
            case '-h':
                console.log(`
Usage: node mermaid_to_illustrator.js [OPTIONS]

Options:
  -f, --figure NAME    Export specific figure (e.g., Figure_1_System_Architecture)
  -a, --all            Export all figures
  --format FORMAT      Output format: svg, png, pdf, all (default: svg)
  -h, --help           Show this help message
                `);
                process.exit(0);
                break;
        }
    }
    
    console.log('');
    console.log('='.repeat(80));
    console.log('  🎨 Mermaid to Illustrator Export Tool');
    console.log('='.repeat(80));
    console.log('');
    console.log(`📁 Output Directory: ${config.outputBaseDir}`);
    console.log('');
    
    // Check Mermaid CLI
    if (!checkMermaidCLI()) {
        process.exit(1);
    }
    
    console.log('✅ Mermaid CLI found');
    console.log('');
    
    // Find figure files
    let figureFiles = [];
    
    if (all || !figureName) {
        // Get all figure markdown files
        const files = fs.readdirSync(config.sourceDir)
            .filter(file => file.startsWith('Figure_') && file.endsWith('.md'))
            .map(file => ({
                name: path.basename(file, '.md'),
                path: path.join(config.sourceDir, file)
            }));
        figureFiles = files;
        console.log(`📋 Found ${figureFiles.length} figure files`);
    } else {
        // Single figure
        const figurePath = path.join(config.sourceDir, `${figureName}.md`);
        if (fs.existsSync(figurePath)) {
            figureFiles = [{
                name: figureName,
                path: figurePath
            }];
        } else {
            console.error(`❌ Figure file not found: ${figurePath}`);
            process.exit(1);
        }
    }
    
    console.log('');
    
    // Process each figure
    let successCount = 0;
    let failCount = 0;
    
    figureFiles.forEach((figure, index) => {
        if (index > 0) {
            console.log('─'.repeat(64));
        }
        
        if (exportFigure(figure.path, figure.name, format)) {
            successCount++;
        } else {
            failCount++;
        }
        
        console.log('');
    });
    
    // Summary
    console.log('='.repeat(80));
    console.log('  ✅ Export Complete!');
    console.log('='.repeat(80));
    console.log('');
    console.log('📊 Summary:');
    console.log(`   Success: ${successCount}`);
    console.log(`   Failed:  ${failCount}`);
    console.log('');
    console.log('📁 Output Location:');
    console.log(`   ${config.outputBaseDir}`);
    console.log('');
    console.log('🎨 Next Steps:');
    console.log('   1. Open SVG files in Adobe Illustrator');
    console.log('   2. Create new document: 8.5" × 11"');
    console.log('   3. Place SVG file and scale to fit');
    console.log('   4. Add Reference Numerals and enhance');
    console.log('   5. Export to TIFF (600 DPI) for Patent submission');
    console.log('');
    
    // Cleanup
    if (fs.existsSync(config.tempDir)) {
        fs.rmSync(config.tempDir, { recursive: true, force: true });
    }
}

// Run main function
if (require.main === module) {
    main();
}

module.exports = { exportFigure, extractMermaidCode };

