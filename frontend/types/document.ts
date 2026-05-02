export interface Document {
  id: number;
  resume_id: number;
  filename: string;
  file_type: string;
  file_path: string;
  file_size?: number;
  storage_type: string;
  s3_url?: string;
  content_type?: string;
  created_at: string;
  expires_at?: string;
}