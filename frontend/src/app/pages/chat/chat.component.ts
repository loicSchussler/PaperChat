import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { ApiService, Message, ConversationListItem } from '../../services/api.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatPageComponent implements OnInit {
  questionControl = new FormControl('');
  loading = false;
  error: string | null = null;

  // Conversation management
  currentConversationId: number | null = null;
  messages: Message[] = [];
  conversations: ConversationListItem[] = [];
  showConversationList = true;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadConversations();
  }

  loadConversations() {
    this.apiService.listConversations().subscribe({
      next: (conversations) => {
        this.conversations = conversations;
      },
      error: (err) => {
        console.error('Error loading conversations:', err);
      }
    });
  }

  selectConversation(conversationId: number) {
    this.currentConversationId = conversationId;
    this.error = null;
    this.loading = true;

    this.apiService.getConversation(conversationId).subscribe({
      next: (conversation) => {
        this.messages = conversation.messages;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading conversation:', err);
        this.error = 'Erreur lors du chargement de la conversation';
        this.loading = false;
      }
    });
  }

  newConversation() {
    this.currentConversationId = null;
    this.messages = [];
    this.error = null;

    // Hide conversation list on mobile to show we're in a new conversation
    if (this.isMobile()) {
      this.showConversationList = false;
    }
  }

  isMobile(): boolean {
    return window.innerWidth <= 768;
  }

  deleteConversation(conversationId: number, event: Event) {
    event.stopPropagation();

    if (!confirm('Voulez-vous vraiment supprimer cette conversation ?')) {
      return;
    }

    this.apiService.deleteConversation(conversationId).subscribe({
      next: () => {
        if (this.currentConversationId === conversationId) {
          this.newConversation();
        }
        this.loadConversations();
      },
      error: (err) => {
        console.error('Error deleting conversation:', err);
        this.error = 'Erreur lors de la suppression';
      }
    });
  }

  askQuestion() {
    const question = this.questionControl.value?.trim();

    if (!question) {
      this.error = 'Veuillez entrer une question';
      return;
    }

    this.loading = true;
    this.error = null;

    // Add user message optimistically to UI
    const userMessage: Partial<Message> = {
      role: 'user',
      content: question,
      cost_usd: 0,
      response_time_ms: 0,
      created_at: new Date().toISOString()
    };
    this.messages.push(userMessage as Message);

    this.apiService.askQuestion({
      question,
      conversation_id: this.currentConversationId || undefined
    }).subscribe({
      next: (response) => {
        // Update conversation ID if this was a new conversation
        if (!this.currentConversationId) {
          this.currentConversationId = response.conversation_id;
          this.loadConversations();
        }

        // Add assistant message
        const assistantMessage: Partial<Message> = {
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
          cost_usd: response.cost_usd,
          response_time_ms: response.response_time_ms,
          created_at: new Date().toISOString()
        };
        this.messages.push(assistantMessage as Message);

        this.questionControl.setValue('');
        this.loading = false;
      },
      error: (err) => {
        console.error('Error during chat request:', err);
        this.error = err.error?.detail || err.message || 'Erreur lors de la requête';
        // Remove optimistic user message on error
        this.messages.pop();
        this.loading = false;
      }
    });
  }

  toggleConversationList() {
    // Only toggle on mobile, keep sidebar always visible on desktop
    if (this.isMobile()) {
      this.showConversationList = !this.showConversationList;
    }
  }

  closeConversationListOnMobile() {
    // Close sidebar on mobile when clicking on main chat area
    if (this.isMobile() && this.showConversationList) {
      this.showConversationList = false;
    }
  }
}
