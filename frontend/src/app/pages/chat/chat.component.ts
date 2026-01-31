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
  costUsd: number | null = null;
  responseTimeMs: number | null = null;

  constructor(private apiService: ApiService) {}

  askQuestion() {
    const question = this.questionControl.value?.trim();

    if (!question) {
      this.error = 'Veuillez entrer une question';
      return;
    }

    this.loading = true;
    this.error = null;
    this.answer = null;
    this.sources = [];
    this.costUsd = null;
    this.responseTimeMs = null;

    this.apiService.askQuestion({ question }).subscribe({
      next: (response) => {
        this.answer = response.answer;
        this.sources = response.sources;
        this.costUsd = response.cost_usd;
        this.responseTimeMs = response.response_time_ms;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error during chat request:', err);
        this.error = err.error?.detail || err.message || 'Erreur lors de la requête';
        this.loading = false;
      }
    });
  }
}
