import os
from PIL import Image
import io

def compress_jpg(input_path, output_path=None, quality=80):
    """
    Compress a JPG image with specified quality
    
    Parameters:
    input_path (str): Path to the input JPG file
    output_path (str, optional): Path to save the compressed JPG file
    quality (int): Compression quality (1-100, higher is better quality)
    """
    if output_path is None:
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(os.path.dirname(input_path), f"{name}_compressed{ext}")
    
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Save with compression
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        return {
            'success': True,
            'file_path': output_path,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'reduction': reduction
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def compress_png(input_path, output_path=None, compression_level=6, max_colors=256):
    """
    Compress a PNG image with specified compression level and color reduction
    
    Parameters:
    input_path (str): Path to the input PNG file
    output_path (str, optional): Path to save the compressed PNG file
    compression_level (int): PNG compression level (1-9, higher means smaller size)
    max_colors (int): Maximum number of colors in the output image
    """
    if output_path is None:
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(os.path.dirname(input_path), f"{name}_compressed{ext}")
    
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                # Create a white background image
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Quantize image to reduce number of colors
            if img.mode == 'RGB':
                quantized = img.quantize(colors=max_colors, method=2)  # method=2 is median cut
                img = quantized.convert('RGB')
            
            # Save with optimization
            img.save(output_path, 'PNG', optimize=True, compression_level=compression_level)
            
            # Use BytesIO to try additional compression
            temp_buffer = io.BytesIO()
            img.save(temp_buffer, format='PNG', optimize=True, compression_level=compression_level)
            temp_buffer.seek(0)
            
            # If BytesIO version is smaller, use it
            if temp_buffer.getbuffer().nbytes < os.path.getsize(output_path):
                with open(output_path, 'wb') as f:
                    f.write(temp_buffer.getvalue())
        
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        return {
            'success': True,
            'file_path': output_path,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'reduction': reduction
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }