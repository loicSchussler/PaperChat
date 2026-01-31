import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ApiService, Paper } from '../../services/api.service';
import { PdfViewerDialogComponent } from '../../components/pdf-viewer-dialog/pdf-viewer-dialog.component';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-library',
  templateUrl: './library.component.html',
  styleUrls: ['./library.component.scss']
})
export class LibraryPageComponent implements OnInit {
  papers: Paper[] = [];
  loading = false;

  constructor(
    private apiService: ApiService,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.loadPapers();
  }

  loadPapers() {
    this.loading = true;

    this.apiService.listPapers(0, 100).subscribe({
      next: (papers) => {
        this.papers = papers;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading papers:', error);
        this.loading = false;
      }
    });
  }

  openPdfViewer(paper: Paper) {
    const pdfUrl = `${environment.apiUrl}/api/papers/${paper.id}/pdf`;

    console.log('🖱️ Opening PDF viewer for paper:', paper.title);
    console.log('🔗 PDF URL:', pdfUrl);
    console.log('📋 Paper ID:', paper.id);
    console.log('🌍 API URL:', environment.apiUrl);

    const isMobile = window.innerWidth <= 768;

    this.dialog.open(PdfViewerDialogComponent, {
      width: isMobile ? '100vw' : '90vw',
      height: isMobile ? '100vh' : '90vh',
      maxWidth: isMobile ? '100vw' : '1400px',
      panelClass: isMobile ? 'mobile-dialog' : '',
      data: {
        pdfUrl: pdfUrl,
        title: paper.title
      }
    });
  }

  deletePaper(paper: Paper, event: Event) {
    event.stopPropagation(); // Prevent card click

    if (confirm(`Voulez-vous vraiment supprimer "${paper.title}" ?`)) {
      this.apiService.deletePaper(paper.id).subscribe({
        next: () => {
          this.papers = this.papers.filter(p => p.id !== paper.id);
        },
        error: (error) => {
          console.error('Error deleting paper:', error);
          alert('Erreur lors de la suppression du document');
        }
      });
    }
  }
}
