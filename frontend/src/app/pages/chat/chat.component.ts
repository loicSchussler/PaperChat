import { Component } from '@angular/core';
import { FormControl } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatPageComponent {
  questionControl = new FormControl('');
  answer: string | null = null;
  sources: any[] = [];
  loading = false;
  error: string | null = null;

  constructor(private apiService: ApiService) {}

  askQuestion() {
    const question = this.questionControl.value?.trim();

    if (!question) {
      this.error = 'Veuillez saisir une question';
      return;
    }

    this.loading = true;
    this.error = null;
    this.answer = null;
    this.sources = [];

    // TODO: Décommenter quand le backend sera prêt
    console.log('Question:', question);

    // Simulation pour le moment
    setTimeout(() => {
      this.answer = 'Le backend n\'est pas encore implémenté. Veuillez coder la logique RAG!';
      this.loading = false;
    }, 1000);

    /*
    this.apiService.askQuestion({ question }).subscribe({
      next: (response) => {
        this.answer = response.answer;
        this.sources = response.sources;
        this.loading = false;
      },
      error: (error) => {
        this.error = error.message || 'Erreur lors de la requête';
        this.loading = false;
      }
    });
    */
  }
}
