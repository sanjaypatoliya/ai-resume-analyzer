export interface UploadResponse {
  upload_url: string;
  upload_fields: Record<string, string>;
  s3_key: string;
  expires_in: number;
}

export interface CategoryScore {
  name: string;
  score: number;
  rationale: string;
}

export interface ExperienceItem {
  title: string;
  company: string;
  duration: string;
}

export interface EducationItem {
  degree: string;
  institution: string;
  year: string;
}

export interface AnalysisResult {
  id: string;
  overall_score: number;
  categories: CategoryScore[];
  skills: string[];
  experience: ExperienceItem[];
  education: EducationItem[];
  suggestions: string[];
  created_at: string;
  file_name: string;
  job_description: string;
}

export interface HistoryItem {
  id: string;
  file_name: string;
  overall_score: number;
  created_at: string;
}

export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
}
