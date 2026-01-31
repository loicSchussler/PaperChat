import { Component, OnInit } from '@angular/core';
import { ApiService, Paper } from '../../services/api.service';

@Component({
  selector: 'app-library',
  templateUrl: './library.component.html',
  styleUrls: ['./library.component.scss']
})
export class LibraryPageComponent implements OnInit {
  papers: Paper[] = [];
  displayedColumns: string[] = ['title', 'authors', 'year', 'nb_chunks', 'actions'];
  loading = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadPapers();
  }

  loadPapers() {
    this.loading = true;

    // TODO: Uncomment when the backend is ready
    /*
    this.apiService.listPapers().subscribe({
      next: (papers) => {
        this.papers = papers;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading papers:', error);
        this.loading = false;
      }
    });
    */

    // Mock data for now
    setTimeout(() => {
      this.papers = [];
      this.loading = false;
    }, 500);
  }

  deletePaper(id: number) {
    if (confirm('Do you really want to delete this article?')) {
      // TODO: Implement deletion
      console.log('Deleting paper:', id);
    }
  }
}
