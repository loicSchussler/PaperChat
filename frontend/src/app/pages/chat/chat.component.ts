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
      this.error = 'Please enter a question';
      return;
    }

    this.loading = true;
    this.error = null;
    this.answer = null;
    this.sources = [];

    // TODO: Uncomment when the backend is ready
    console.log('Question:', question);

    // Simulation for now
    setTimeout(() => {
      this.answer = 'The backend is not yet implemented. Please code the RAG logic!';
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
        this.error = error.message || 'Error during request';
        this.loading = false;
      }
    });
    */
  }
}
