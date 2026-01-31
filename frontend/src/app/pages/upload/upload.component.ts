import { Component } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadPageComponent {
  selectedFile: File | null = null;
  uploading = false;
  uploadSuccess = false;
  uploadError: string | null = null;

  constructor(private apiService: ApiService) {}

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      this.selectedFile = file;
      this.uploadError = null;
    } else {
      this.uploadError = 'Please select a PDF file';
    }
  }

  onUpload() {
    if (!this.selectedFile) {
      this.uploadError = 'No file selected';
      return;
    }

    this.uploading = true;
    this.uploadError = null;
    this.uploadSuccess = false;

    this.apiService.uploadPaper(this.selectedFile).subscribe({
      next: (response) => {
        this.uploading = false;
        this.uploadSuccess = true;
        this.selectedFile = null;
        console.log('Upload successful:', response);
      },
      error: (error) => {
        this.uploading = false;
        this.uploadError = error.error?.detail || error.message || 'Error during upload';
        console.error('Upload error:', error);
      }
    });
  }
}
