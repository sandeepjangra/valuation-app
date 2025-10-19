import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface DatabaseInfo {
  name: string;
  collections: string[];
}

export interface CollectionDocument {
  _id: string;
  [key: string]: any;
}

export interface AuditLogEntry {
  _id: string;
  operation: 'CREATE' | 'UPDATE' | 'DELETE';
  database: string;
  collection: string;
  documentId: string;
  userId: string;
  userName: string;
  timestamp: string;
  changes?: any;
  previousVersion?: any;
}

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private readonly baseUrl = `${environment.apiUrl}/admin`;

  constructor(private http: HttpClient) {}

  // Database and Collection Management
  getDatabases(): Observable<DatabaseInfo[]> {
    return this.http.get<DatabaseInfo[]>(`${this.baseUrl}/databases`);
  }

  getCollections(database: string): Observable<string[]> {
    return this.http.get<string[]>(`${this.baseUrl}/databases/${database}/collections`);
  }

  // Document Management
  getDocuments(database: string, collection: string, page: number = 1, limit: number = 20): Observable<{documents: CollectionDocument[], total: number, page: number, totalPages: number}> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());
    
    return this.http.get<{documents: CollectionDocument[], total: number, page: number, totalPages: number}>(
      `${this.baseUrl}/databases/${database}/collections/${collection}/documents`,
      { params }
    );
  }

  getDocument(database: string, collection: string, id: string): Observable<CollectionDocument> {
    return this.http.get<CollectionDocument>(`${this.baseUrl}/databases/${database}/collections/${collection}/documents/${id}`);
  }

  createDocument(database: string, collection: string, document: any): Observable<{_id: string}> {
    return this.http.post<{_id: string}>(`${this.baseUrl}/databases/${database}/collections/${collection}/documents`, document);
  }

  updateDocument(database: string, collection: string, id: string, document: any): Observable<{success: boolean}> {
    return this.http.put<{success: boolean}>(`${this.baseUrl}/databases/${database}/collections/${collection}/documents/${id}`, document);
  }

  deleteDocument(database: string, collection: string, id: string): Observable<{success: boolean}> {
    return this.http.delete<{success: boolean}>(`${this.baseUrl}/databases/${database}/collections/${collection}/documents/${id}`);
  }

  // Search functionality
  searchDocuments(database: string, collection: string, query: any, page: number = 1, limit: number = 20): Observable<{documents: CollectionDocument[], total: number}> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());
    
    return this.http.post<{documents: CollectionDocument[], total: number}>(
      `${this.baseUrl}/databases/${database}/collections/${collection}/search`,
      query,
      { params }
    );
  }

  // Audit Trail
  getAuditLogs(database?: string, collection?: string, page: number = 1, limit: number = 50): Observable<{logs: AuditLogEntry[], total: number}> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());
    
    if (database) params = params.set('database', database);
    if (collection) params = params.set('collection', collection);
    
    return this.http.get<{logs: AuditLogEntry[], total: number}>(
      `${this.baseUrl}/audit-logs`,
      { params }
    );
  }

  // Collection Statistics
  getCollectionStats(database: string, collection: string): Observable<{count: number, size: number, avgObjSize: number, indexes: any[]}> {
    return this.http.get<{count: number, size: number, avgObjSize: number, indexes: any[]}>(`${this.baseUrl}/databases/${database}/collections/${collection}/stats`);
  }
}