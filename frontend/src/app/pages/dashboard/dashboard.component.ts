import { Component, OnInit } from '@angular/core';
import { ApiService, MonitoringStats } from '../../services/api.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardPageComponent implements OnInit {
  stats: MonitoringStats | null = null;
  loading = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadStats();
  }

  loadStats() {
    this.loading = true;

    // TODO: Uncomment when the backend is ready
    /*
    this.apiService.getStats().subscribe({
      next: (stats) => {
        this.stats = stats;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading stats:', error);
        this.loading = false;
      }
    });
    */

    // Mock data
    setTimeout(() => {
      this.stats = {
        total_papers: 0,
        total_chunks: 0,
        total_queries: 0,
        total_cost_usd: 0,
        avg_response_time_ms: 0,
        queries_today: 0
      };
      this.loading = false;
    }, 500);
  }
}
