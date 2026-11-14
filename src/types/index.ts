export interface Chunk {
  id: string;
  index: number;
  text: string;
  key_takeaway?: string;
  word_count: number;
  estimated_seconds: number;
  entities: string[];
  cognitive_difficulty: 'easy' | 'medium' | 'dense' | 'Easy' | 'Medium' | 'Hard' | 'Very Hard' | string;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_answer_index: number;
  explanation: string;
}

export interface Flashcard {
  id: string;
  front: string;
  back: string;
  category: string;
  mastered?: boolean;
}

export interface KeyConcept {
  id: string;
  term: string;
  definition: string;
  analogy?: string;
  context?: string;
}

export interface ArticleSummary {
  tldr: string;
  detailed_explanation?: string;
  key_takeaways: string[];
  cognitive_outline: Array<{
    section: string;
    takeaway: string;
  }>;
  is_ai_generated?: boolean;
  provider?: string;
  fallback_notice?: string;
}

export interface SemanticHighlight {
  id: string;
  category: 'concept' | 'definition' | 'evidence';
  text: string;
  start_char: number;
  end_char: number;
  label: string;
  explanation?: string;
}

export interface Article {
  id: string;
  title: string;
  author?: string;
  source_url?: string;
  domain?: string;
  raw_content?: string;
  reading_time_minutes: number;
  word_count: number;
  flesch_score: number;
  cognitive_rating: string;
  predicted_difficulty?: DifficultyClass;
  chunks: Chunk[];
  summary?: ArticleSummary;
  concepts: KeyConcept[];
  quiz: QuizQuestion[];
  flashcards: Flashcard[];
  highlights?: SemanticHighlight[];
  progress_percent: number;
  current_chunk_index: number;
  is_favorite: boolean;
  is_completed: boolean;
  created_at: string;
}

export interface ArticleListItem {
  id: string;
  title: string;
  author?: string;
  domain?: string;
  reading_time_minutes: number;
  word_count: number;
  progress_percent: number;
  current_chunk_index: number;
  is_favorite: boolean;
  is_completed: boolean;
  total_chunks: number;
  created_at: string;
}

export interface UserSettings {
  font_family: 'lexend' | 'atkinson' | 'dyslexic' | 'sans' | 'serif' | 'mono';
  font_size: number; // 14 to 28 px
  line_spacing: number; // 1.4 to 2.4
  letter_spacing: number; // 0 to 3 px
  content_width: number; // 500 to 900 px
  bionic_reading: boolean;
  focus_ruler: boolean;
  chunk_mode: boolean; // true = chunk-by-chunk, false = full flow
  chunk_size_words: number; // 40 to 140 words
  enable_semantic_highlights: boolean;
  focus_mode: boolean; // Zen mode (hides header/footer/distractions)
  tts_speed: number; // 0.75, 1.0, 1.25, 1.5
  theme: 'warm' | 'white' | 'dark' | 'slate';
  reduced_motion: boolean;
  high_contrast: boolean;
}

export interface ReadingStats {
  total_articles: number;
  completed_articles: number;
  total_minutes_focused: number;
  total_chunks_read: number;
  streak_days: number;
}

export type ActiveTab = 'landing' | 'reader' | 'dashboard' | 'settings' | 'extension-popup' | 'sidepanel' | 'mlops';

export interface AIMessage {
  role: 'user' | 'model';
  content: string;
}

// -----------------------------------------------------------------------------
// ACLI MLOps Types
// -----------------------------------------------------------------------------

export type DifficultyClass = 'Easy' | 'Medium' | 'Hard' | 'Very Hard';

export interface FeatureContribution {
  feature: string;
  description: string;
  raw_value: number;
  shap_value: number;
  impact: 'increases_difficulty' | 'decreases_difficulty';
  abs_impact: number;
}

export interface PredictDifficultyResponse {
  status: 'success' | 'error';
  predicted_difficulty: DifficultyClass;
  confidence: number;
  probabilities: Record<string, number>;
  model_version?: string;
  latency_ms: number;
  features: Record<string, number>;
  recommendations: string[];
  error?: string;
}

export interface ExplainDifficultyResponse {
  available: boolean;
  predicted_class?: DifficultyClass;
  confidence?: number;
  base_value?: number;
  feature_contributions: FeatureContribution[];
  human_explanation: string;
  model_version?: string;
  error?: string;
}

export interface ModelInfoResponse {
  status: 'ready' | 'unavailable';
  model_version?: string;
  algorithm?: string;
  dataset_version?: string;
  feature_schema_version?: string;
  training_duration_seconds?: number;
  accuracy?: number;
  macro_f1?: number;
  features?: string[];
  classes?: string[];
  message?: string;
}

export interface ModelMetricsResponse {
  model_version: string;
  algorithm: string;
  hyperparameters: Record<string, any>;
  dataset_version: string;
  training_duration_seconds: number;
  created_at: string;
  approved: boolean;
  approval_reason: string;
  metrics: {
    accuracy: number;
    macro_precision: number;
    macro_recall: number;
    macro_f1: number;
    per_class: Record<string, {
      precision: number;
      recall: number;
      f1: number;
      support: number;
    }>;
    confusion_matrix: number[][];
    class_labels: string[];
  };
}

export interface FeatureDriftItem {
  psi: number;
  status: 'STABLE' | 'MODERATE_DRIFT' | 'SIGNIFICANT_DRIFT' | 'INSUFFICIENT_SAMPLES';
  current_mean: number;
  reference_mean: number;
  description: string;
}

export interface ModelMonitoringResponse {
  has_data: boolean;
  total_requests: number;
  successful_requests: number;
  error_rate: number;
  latency: {
    p50_ms: number;
    p95_ms: number;
    mean_ms: number;
  };
  class_counts: Record<string, number>;
  class_distribution: Record<string, number>;
  feature_drift: {
    overall_drift_status: 'STABLE' | 'WARNING' | 'DRIFT_DETECTED' | 'NO_DATA';
    features: Record<string, FeatureDriftItem>;
  };
  recent_predictions: Array<{
    id: number;
    timestamp: string;
    model_version: string;
    predicted_difficulty: string;
    confidence: number;
    latency_ms: number;
    success: boolean;
  }>;
  approved_model_version?: string;
  approved_at?: string;
  model_metadata?: any;
  experiment_history: Array<{
    version: string;
    algorithm: string;
    created_at: string;
    approved: boolean;
    approval_reason: string;
    training_duration_seconds: number;
    metrics: {
      accuracy: number;
      macro_f1: number;
    };
  }>;
}
