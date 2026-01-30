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

    // TODO: Décommenter quand le backend sera prêt
    /*
    this.apiService.listPapers().subscribe({
      next: (papers) => {
        this.papers = papers;
        this.loading = false;
      },
      error: (error) => {
        console.error('Erreur chargement papers:', error);
        this.loading = false;
      }
    });
    */

    // Données mockées pour le moment
    setTimeout(() => {
      this.papers = [];
      this.loading = false;
    }, 500);
  }

  deletePaper(id: number) {
    if (confirm('Voulez-vous vraiment supprimer cet article?')) {
      // TODO: Implémenter la suppression
      console.log('Suppression du paper:', id);
    }
  }
}
