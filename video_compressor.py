import os
import subprocess
from pathlib import Path

def compress_video(input_path, output_path, resolution='original', bitrate=None):
    """Compress video using FFmpeg with specified parameters.
    
    Args:
        input_path (str): Path to input video file
        output_path (str): Path to save compressed video
        resolution (str): Target resolution ('original', '1080p', '720p', '480p')
        bitrate (str, optional): Target bitrate (e.g., '1M', '2M')
        
    Returns:
        dict: Dictionary containing compression results
    """
    try:
        # Get original video info
        original_size = os.path.getsize(input_path)
        
        # Prepare FFmpeg command
        command = ['ffmpeg', '-i', input_path, '-y']
        
        # Add resolution filter if not original
        if resolution != 'original':
            if resolution == '1080p':
                command.extend(['-vf', 'scale=1920:1080'])
            elif resolution == '720p':
                command.extend(['-vf', 'scale=1280:720'])
            elif resolution == '480p':
                command.extend(['-vf', 'scale=854:480'])
        
        # Add quality settings
        command.extend([
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k'
        ])
        
        # Add custom bitrate if specified
        if bitrate:
            command.extend(['-b:v', bitrate])
        
        # Add output path
        command.append(output_path)
        
        # Run FFmpeg
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        # Get compressed size
        compressed_size = os.path.getsize(output_path)
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        return {
            'success': True,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'reduction': reduction,
            'file_path': output_path
        }
        
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'error': f'FFmpeg error: {e.stderr}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }