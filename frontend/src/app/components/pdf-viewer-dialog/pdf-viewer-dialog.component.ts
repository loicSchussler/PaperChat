import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

export interface PdfViewerDialogData {
  pdfUrl: string;
  title: string;
}

@Component({
  selector: 'app-pdf-viewer-dialog',
  templateUrl: './pdf-viewer-dialog.component.html',
  styleUrls: ['./pdf-viewer-dialog.component.scss']
})
export class PdfViewerDialogComponent implements OnInit {
  zoom = 1.0;
  page = 1;
  totalPages = 0;
  isLoaded = false;
  error: string | null = null;

  constructor(
    public dialogRef: MatDialogRef<PdfViewerDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: PdfViewerDialogData
  ) {}

  ngOnInit(): void {
    console.log('🔍 PDF Viewer Dialog initialized');
    console.log('📄 PDF URL:', this.data.pdfUrl);
    console.log('📝 Title:', this.data.title);
  }

  onClose(): void {
    this.dialogRef.close();
  }

  afterLoadComplete(pdf: any): void {
    this.totalPages = pdf.numPages;
    this.isLoaded = true;
    console.log('✅ PDF loaded successfully!');
    console.log('📊 Total pages:', this.totalPages);
    console.log('📄 PDF object:', pdf);
  }

  onError(error: any): void {
    console.error('❌ Error loading PDF:', error);
    console.error('Error details:', JSON.stringify(error, null, 2));
    this.error = 'Erreur lors du chargement du PDF: ' + (error.message || 'Erreur inconnue');
  }

  onProgress(progressData: any): void {
    console.log('⏳ Loading progress:', progressData);
  }

  onPageRendered(event: any): void {
    console.log('🎨 Page rendered:', event);
    console.log('Page number:', event.pageNumber);
    console.log('Source:', event.source);
  }

  zoomIn(): void {
    this.zoom += 0.1;
    console.log('🔍 Zoom in:', this.zoom);
  }

  zoomOut(): void {
    if (this.zoom > 0.2) {
      this.zoom -= 0.1;
      console.log('🔍 Zoom out:', this.zoom);
    }
  }

  nextPage(): void {
    if (this.page < this.totalPages) {
      this.page++;
      console.log('➡️ Next page:', this.page);
    }
  }

  previousPage(): void {
    if (this.page > 1) {
      this.page--;
      console.log('⬅️ Previous page:', this.page);
    }
  }
}
