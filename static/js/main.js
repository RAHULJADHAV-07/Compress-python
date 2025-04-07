document.addEventListener('DOMContentLoaded', () => {
    // Tab switching functionality
    const tabs = document.querySelectorAll('[data-tab]');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('border-blue-600', 'text-blue-600'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab and its content
            tab.classList.add('border-blue-600', 'text-blue-600');
            document.getElementById(`${tab.dataset.tab}-tab`).classList.add('active');
        });
    });

    // File upload handling for each type
    ['pdf', 'jpg', 'png', 'video'].forEach(type => {
        const dropZone = document.getElementById(`${type}DropZone`);
        const fileInput = document.getElementById(`${type}FileInput`);
        const form = document.getElementById(`${type}Form`);
        const uploadPlaceholder = document.getElementById(`${type}UploadPlaceholder`);
        const fileDetails = document.getElementById(`${type}FileDetails`);
        const fileName = document.getElementById(`${type}FileName`);
        const fileSize = document.getElementById(`${type}FileSize`);
        const removeButton = document.getElementById(`${type}RemoveFile`);
        const progress = document.getElementById(`${type}Progress`);
        const progressBar = progress.querySelector('.progress-bar');
        const status = document.getElementById(`${type}Status`);
        const stats = document.getElementById(`${type}CompressionStats`);

        // Drag and drop handling
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('dragover');
            });
        });

        dropZone.addEventListener('drop', (e) => {
            const file = e.dataTransfer.files[0];
            if (file) handleFile(file);
        });

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) handleFile(file);
        });

        function handleFile(file) {
            uploadPlaceholder.classList.add('hidden');
            fileDetails.classList.remove('hidden');
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            form.querySelector('button[type="submit"]').disabled = false;
        }

        removeButton.addEventListener('click', () => {
            fileInput.value = '';
            uploadPlaceholder.classList.remove('hidden');
            fileDetails.classList.add('hidden');
            form.querySelector('button[type="submit"]').disabled = true;
            progress.classList.add('hidden');
            stats.classList.add('hidden');
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            
            progress.classList.remove('hidden');
            progressBar.style.width = '0%';
            status.textContent = 'Uploading...';
            
            try {
                const response = await fetch(`/compress/${type}`, {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) throw new Error('Compression failed');
                
                const result = await response.json();
                
                if (result.error) throw new Error(result.error);
                
                progressBar.style.width = '100%';
                status.textContent = 'Compression complete!';
                
                // Update compression stats
                document.getElementById(`${type}OriginalSize`).textContent = formatFileSize(result.original_size);
                document.getElementById(`${type}CompressedSize`).textContent = formatFileSize(result.compressed_size);
                document.getElementById(`${type}Reduction`).textContent = `${result.reduction.toFixed(1)}%`;
                stats.classList.remove('hidden');
                
                // Trigger download
                window.location.href = `/download/${encodeURIComponent(result.file_path)}`;
            } catch (error) {
                status.textContent = `Error: ${error.message}`;
                progressBar.style.width = '0%';
            }
        });
    });
});

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}