import os
import argparse
import pikepdf
import sys
import subprocess
import tempfile
import shutil

def compress_with_ghostscript(input_path, output_path, compression_level="screen"):
    """Use Ghostscript for compression when available"""
    
    # Define Ghostscript preset parameters
    presets = {
        "screen": "/screen",       # 72 dpi images, lowest quality (smallest)
        "ebook": "/ebook",         # 150 dpi images, medium quality
        "printer": "/printer",     # 300 dpi images, high quality
        "prepress": "/prepress"    # 300 dpi images, preserves color, highest quality
    }
    
    # Try to find Ghostscript
    gs_command = None
    for cmd in ["gs", "gswin64c", "gswin32c"]:
        try:
            subprocess.run([cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            gs_command = cmd
            break
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    
    if gs_command:
        print(f"Using Ghostscript for compression...")
        try:
            # Build Ghostscript command
            gs_params = [
                gs_command,
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS={presets[compression_level]}",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-sOutputFile={output_path}",
                input_path
            ]
            
            # Run Ghostscript
            subprocess.run(gs_params, check=True)
            return True
        except Exception as e:
            print(f"Ghostscript failed: {e}")
            return False
    else:
        print("Ghostscript not found")
        return False

def compress_with_qpdf(input_path, output_path):
    """Use QPDF for lossless compression when available - Disabled as QPDF is not supported"""
    print("QPDF compression is not available in this environment")
    return False

def compress_with_pikepdf(input_path, output_path, quality="low"):
    """Use pikepdf as the fallback compression method"""
    print("Using pikepdf for compression...")
    try:
        # Get quality settings
        quality_settings = {
            "high": {"image_quality": 60},
            "medium": {"image_quality": 40},
            "low": {"image_quality": 20}
        }
        
        # Open PDF with pikepdf
        with pikepdf.open(input_path) as pdf:
            # Save with compression settings
            pdf.save(output_path,
                    compress_streams=True,
                    object_stream_mode=pikepdf.ObjectStreamMode.generate,
                    normalize_content=True)
        return True
    except Exception as e:
        print(f"pikepdf compression failed: {e}")
        return False

def alternative_pdf_compression(input_path, output_path=None, method="auto"):
    """
    Try multiple PDF compression methods and use the best result
    
    Parameters:
    input_path (str): Path to the input PDF file
    output_path (str, optional): Path to save the compressed PDF file
    method (str): Compression method - auto, gs, qpdf, pikepdf
    """
    # Set default output path if not provided
    if output_path is None:
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(os.path.dirname(input_path), f"{name}_compressed{ext}")
    
    print(f"Attempting compression of {input_path}...")
    original_size = os.path.getsize(input_path)
    print(f"Original size: {format_size(original_size)}")
    
    # Create temp directory for working files
    temp_dir = tempfile.mkdtemp()
    best_path = None
    best_size = float('inf')
    
    try:
        # Try multiple methods and find the best one
        if method == "auto" or method == "gs":
            gs_out = os.path.join(temp_dir, "gs_output.pdf")
            if compress_with_ghostscript(input_path, gs_out, "screen"):
                if os.path.exists(gs_out):
                    gs_size = os.path.getsize(gs_out)
                    print(f"Ghostscript result: {format_size(gs_size)}")
                    if gs_size < best_size:
                        best_size = gs_size
                        best_path = gs_out
        
        if method == "auto" or method == "qpdf":
            qpdf_out = os.path.join(temp_dir, "qpdf_output.pdf")
            if compress_with_qpdf(input_path, qpdf_out):
                if os.path.exists(qpdf_out):
                    qpdf_size = os.path.getsize(qpdf_out)
                    print(f"QPDF result: {format_size(qpdf_size)}")
                    if qpdf_size < best_size:
                        best_size = qpdf_size
                        best_path = qpdf_out
        
        if method == "auto" or method == "pikepdf":
            pikepdf_out = os.path.join(temp_dir, "pikepdf_output.pdf")
            if compress_with_pikepdf(input_path, pikepdf_out, "low"):
                if os.path.exists(pikepdf_out):
                    pikepdf_size = os.path.getsize(pikepdf_out)
                    print(f"pikepdf result: {format_size(pikepdf_size)}")
                    if pikepdf_size < best_size:
                        best_size = pikepdf_size
                        best_path = pikepdf_out
        
        # Copy the best result to the output path
        if best_path and os.path.exists(best_path):
            shutil.copy2(best_path, output_path)
            compressed_size = os.path.getsize(output_path)
            reduction = (1 - (compressed_size / original_size)) * 100
            
            print(f"Compression complete!")
            print(f"Final size: {format_size(compressed_size)}")
            print(f"Size reduction: {reduction:.2f}%")
            
            if reduction < 0:
                print("\nWARNING: The file size increased after processing.")
                print("This PDF may already be optimally compressed or have special features.")
                print("The original file might be better to keep in this case.")
        else:
            print("All compression methods failed or increased file size.")
            print("Your PDF may already be optimally compressed.")
            # Copy the original as fallback
            shutil.copy2(input_path, output_path)
    
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)
    
    return output_path

def format_size(size_bytes):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def main():
    parser = argparse.ArgumentParser(description="Specialized PDF compression tool")
    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument("-o", "--output", help="Path to save the compressed PDF file (optional)")
    parser.add_argument(
        "-m", "--method", 
        choices=["auto", "gs", "qpdf", "pikepdf"], 
        default="auto",
        help="Compression method to use (default: auto tries all methods)"
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.isfile(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        return
    
    alternative_pdf_compression(args.input, args.output, args.method)

if __name__ == "__main__":
    main()