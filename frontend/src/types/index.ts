export interface Resume {
  id: string
  original_filename: string
  status: string
  parse_method?: string
  confidence?: number
  extracted_name?: string
  extracted_phone?: string
  extracted_email?: string
  education_summary?: string
  skills_summary?: string[]
}

export interface ATSAnalysis {
  overall_score: number
  keyword_coverage: number
  format_issues: string[]
  missing_sections: string[]
  detected_keywords: string[]
  missing_keywords: string[]
  recommendations: string[]
}

export interface DiagnosisResult {
  resume_id: string
  match_score: number
  radar_scores: Record<string, number>
  analysis: string
  skill_gap: string[]
  suggestions: string[]
  ats_analysis?: ATSAnalysis
}

export interface Job {
  id: string
  title: string
  company?: string
  description?: string
  requirements?: {
    education?: string
    experience?: string
    skills?: string[]
    [key: string]: unknown
  }
  category?: string
}

export interface JobAnalysis {
  title: string
  company: string
  job_level: string
  experience_required: string
  education_required: string
  salary_range: string
  core_skills: string[]
  bonus_skills: string[]
  responsibilities: string[]
  hard_requirements: string[]
  difficulty_score: number
  market_demand: string
  career_outlook: string
  summary: string
}

export interface MatchReasons {
  why_match: string
  advantages: string[]
  gaps: string[]
}

export interface MatchingResult {
  resume_id: string
  job_id?: string
  match_score: number
  dimensions: Record<string, number>
  strengths: string[]
  weaknesses: string[]
  gaps: string[]
  suggestion: string
  match_reasons?: MatchReasons
}

export interface InterviewMessage {
  id: string
  role: 'interviewer' | 'user'
  content: string
  created_at: string
}

export interface Evaluation {
  professional: number
  logic: number
  communication: number
  project: number
  match: number
  learning?: number | null
  stress_resistance?: number | null
  decomposition?: number | null
  engineering_quality?: number | null
  innovation?: number | null
  overall: number
  confidence: number
  feedback: string
  should_follow_up: boolean
  follow_up_question?: string
}

export interface ReviewItem {
  id: string
  interview_id: string
  overall_score: number
  created_at: string
}

export interface ReviewDetail {
  id: string
  interview_id: string
  overall_score: number
  radar_data: Record<string, number>
  question_reviews: QuestionReview[]
  interviewer_summary: string
  suggestions: Suggestion[]
  created_at: string
}

export interface QuestionReview {
  question: string
  answer_summary: string
  score: number
  strengths: string[]
  improvements: string[]
}

export interface Suggestion {
  priority: string
  dimension: string
  action: string
}

export interface GrowthRadar {
  dimensions: string[]
  latest_scores: number[]
  previous_scores: number[]
}

export interface GrowthTrend {
  dimension: string
  data: { date: string; score: number }[]
}

export interface Interview {
  id: string
  round: string
  status: string
  duration: number
  created_at: string
  resume_id?: string
  job_id?: string
}

export interface Application {
  id: string
  company: string
  position: string
  stage: string
  city?: string
  salary_range?: string
  notes?: string
  contact_info?: string
  feedback?: string
  created_at: string
}

export interface ResumeDetail {
  id: string
  original_filename: string
  status: string
  parse_method?: string
  confidence?: number
  extracted_name?: string
  extracted_phone?: string
  extracted_email?: string
  education_summary?: string
  skills_summary?: string[]
  parsed_data?: {
    name?: string
    phone?: string
    email?: string
    education?: Array<{
      school: string
      degree: string
      major: string
      start_date?: string
      end_date?: string
    }>
    experience?: Array<{
      company: string
      position: string
      start_date?: string
      end_date?: string
      description?: string
    }>
    projects?: Array<{
      name: string
      description?: string
    }>
    skills?: string[]
    summary?: string
    raw_text?: string
  }
}
