import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { UploadPageComponent } from './pages/upload/upload.component';
import { LibraryPageComponent } from './pages/library/library.component';
import { ChatPageComponent } from './pages/chat/chat.component';
import { DashboardPageComponent } from './pages/dashboard/dashboard.component';

const routes: Routes = [
  { path: '', redirectTo: '/upload', pathMatch: 'full' },
  { path: 'upload', component: UploadPageComponent },
  { path: 'library', component: LibraryPageComponent },
  { path: 'chat', component: ChatPageComponent },
  { path: 'dashboard', component: DashboardPageComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
