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
      this.uploadError = 'Veuillez sélectionner un fichier PDF';
    }
  }

  onUpload() {
    if (!this.selectedFile) {
      this.uploadError = 'Aucun fichier sélectionné';
      return;
    }

    this.uploading = true;
    this.uploadError = null;
    this.uploadSuccess = false;

    // TODO: Implémenter l'upload réel quand le backend sera prêt
    console.log('Upload de:', this.selectedFile.name);

    // Simuler un upload pour le moment
    setTimeout(() => {
      this.uploading = false;
      this.uploadSuccess = true;
      this.selectedFile = null;
    }, 2000);

    // Code réel à décommenter quand le backend sera prêt:
    /*
    this.apiService.uploadPaper(this.selectedFile).subscribe({
      next: (response) => {
        this.uploading = false;
        this.uploadSuccess = true;
        this.selectedFile = null;
        console.log('Upload réussi:', response);
      },
      error: (error) => {
        this.uploading = false;
        this.uploadError = error.message || 'Erreur lors de l\'upload';
        console.error('Erreur upload:', error);
      }
    });
    */
  }
}
