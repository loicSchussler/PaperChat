import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Paper {
  id: number;
  title: string;
  authors: string[];
  year: number;
  abstract: string;
  keywords: string[];
  nb_chunks: number;
  created_at: string;
}

export interface ChatRequest {
  question: string;
  paper_ids?: number[];
  max_sources?: number;
}

export interface ChatResponse {
  answer: string;
  sources: SourceCitation[];
  cost_usd: number;
  response_time_ms: number;
}

export interface SourceCitation {
  paper_title: string;
  paper_year: number;
  section_name: string;
  content: string;
  relevance_score: number;
}

export interface MonitoringStats {
  total_papers: number;
  total_chunks: number;
  total_queries: number;
  total_cost_usd: number;
  avg_response_time_ms: number;
  queries_today: number;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  // Papers endpoints
  uploadPaper(file: File): Observable<Paper> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<Paper>(`${this.apiUrl}/api/papers/upload`, formData);
  }

  listPapers(skip: number = 0, limit: number = 10, search?: string, year?: number): Observable<Paper[]> {
    let params: any = { skip, limit };
    if (search) params.search = search;
    if (year) params.year = year;
    return this.http.get<Paper[]>(`${this.apiUrl}/api/papers`, { params });
  }

  getPaper(id: number): Observable<Paper> {
    return this.http.get<Paper>(`${this.apiUrl}/api/papers/${id}`);
  }

  deletePaper(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/api/papers/${id}`);
  }

  // Chat endpoint
  askQuestion(request: ChatRequest): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/api/chat`, request);
  }

  // Monitoring endpoint
  getStats(): Observable<MonitoringStats> {
    return this.http.get<MonitoringStats>(`${this.apiUrl}/api/monitoring/stats`);
  }
}
