/**
 * FocusFlow AI Service — powered by OpenRouter
 *
 * OpenRouter provides a unified OpenAI-compatible API across many models.
 * We use google/gemini-2.0-flash-exp:free as the default (free tier).
 *
 * DESIGN CONTRACT:
 * Grounded Content Generation (Summary, Concepts, Quiz, Flashcards):
 * 1. Every output item must be EXPLICITLY supported by the user's input text.
 * 2. NEVER add information from training knowledge, the internet, or prior conversations.
 * 3. NEVER invent examples, related topics, or expansions.
 * 4. Concepts must be MEANINGFUL terms from the text — not stop-words.
 * 5. Quiz questions & Flashcards must derive ONLY from the provided text.
 *
 * Interactive Ask AI:
 * 1. Functions as an interactive learning assistant / tutor for neurodivergent readers.
 * 2. Uses the provided paragraph as context, but is NOT restricted to it.
 * 3. Uses general knowledge to explain terms, expand on concepts, and answer outside questions.
 * 4. Never uses refusal phrases ("Not mentioned in the text") merely because content is absent.
 * 5. Simple, clear language optimized for accessibility.
 */

import { ArticleSummary, KeyConcept, QuizQuestion, Flashcard } from '../types';

const OR_API_KEY = import.meta.env.VITE_OPENROUTER_API_KEY as string;
const OR_BASE_URL = 'https://openrouter.ai/api/v1/chat/completions';
const OR_MODEL = (import.meta.env.VITE_OPENROUTER_MODEL as string) || 'openrouter/free';
const OR_SITE_URL = 'http://localhost:5173';
const OR_SITE_NAME = 'FocusFlow';

export interface AIMessage {
  role: 'user' | 'model';
  content: string;
}

export interface ArticleAIContent {
  summary: ArticleSummary;
  concepts: KeyConcept[];
  quiz: QuizQuestion[];
  flashcards: Flashcard[];
}

// ─── Low-level fetch wrapper ──────────────────────────────────────────────────

function toOpenAIRole(role: 'user' | 'model'): 'user' | 'assistant' {
  return role === 'model' ? 'assistant' : 'user';
}

async function aiRequest(
  systemPrompt: string,
  userMessage: string,
  history: AIMessage[] = [],
  temperature = 0.1
): Promise<string> {
  if (!OR_API_KEY) {
    throw new Error(
      'OpenRouter API key is not configured. Please add VITE_OPENROUTER_API_KEY to your .env file.'
    );
  }

  const messages: Array<{ role: string; content: string }> = [
    { role: 'system', content: systemPrompt },
    ...history.map((m) => ({
      role: toOpenAIRole(m.role),
      content: m.content,
    })),
    { role: 'user', content: userMessage },
  ];

  const res = await fetch(OR_BASE_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${OR_API_KEY}`,
      'HTTP-Referer': OR_SITE_URL,
      'X-Title': OR_SITE_NAME,
    },
    body: JSON.stringify({
      model: OR_MODEL,
      messages,
      temperature,
      max_tokens: 2048,
      top_p: 0.85,
    }),
    signal: AbortSignal.timeout(30000),
  });

  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}));
    const msg =
      errBody?.error?.message ||
      `OpenRouter API error: ${res.status} ${res.statusText}`;
    throw new Error(msg);
  }

  const data = await res.json();
  const text: string = data?.choices?.[0]?.message?.content ?? '';
  return text.trim();
}

// ─── Safe JSON parse ──────────────────────────────────────────────────────────

function safeParseJSON<T>(raw: string, fallback: T): T {
  const cleaned = raw
    .replace(/^```(?:json)?\s*/i, '')
    .replace(/\s*```\s*$/i, '')
    .trim();
  try {
    return JSON.parse(cleaned) as T;
  } catch {
    return fallback;
  }
}

// ─── Article AI content generation ───────────────────────────────────────────

/**
 * Generate learning content (summary, concepts, quiz, flashcards) from raw text.
 * All output is strictly grounded in the provided text — no outside knowledge.
 */
export async function generateArticleAIContent(
  articleText: string,
  articleTitle: string
): Promise<ArticleAIContent> {
  const truncatedText =
    articleText.length > 8000
      ? articleText.slice(0, 8000) + '\n\n[TEXT TRUNCATED]'
      : articleText;

  const systemPrompt = `You are a strict educational content generator for a reading accessibility app used by neurodivergent users.

YOUR ONLY SOURCE OF TRUTH IS THE USER'S PROVIDED PARAGRAPH / TEXT.
CRITICAL RULES:
1. Do NOT use outside knowledge, search the web, or add external facts.
2. Do NOT continue the topic, invent examples, or add recommendations.
3. Do NOT append "If you'd like, I can..." or similar phrases.
4. Summary MUST shorten the paragraph, preserving important ideas while removing repetition. Do NOT copy the first sentences verbatim.
5. Key Takeaways: extract ONLY the most important ideas actually in the text. Do NOT pad to reach a fixed quota. If only 2 or 3 distinct ideas exist, return only 2 or 3.
6. Concepts: extract ONLY meaningful terms/subjects/processes from the text (e.g. Photosynthesis, Chlorophyll). NEVER extract generic words like "During", "Earth", "Inside", "This", "Process", "If you", "Researching", "Mode", "TERM". Every concept MUST include exact context copied from the text.
7. Quiz & Flashcards: questions MUST be answerable ONLY from the provided text. Do NOT ask about unmentioned concepts (e.g., Calvin cycle, ATP, NADPH unless in text).
8. Return ONLY valid JSON — no markdown fences, no conversational text.`;

  const userMessage = `Generate a grounded learning package from this text.

TITLE: "${articleTitle}"

TEXT:
"""
${truncatedText}
"""

Return ONLY this JSON structure (no extra text):
{
  "summary": {
    "tldr": "ONE concise sentence compressing the core idea. Must be shorter than original paragraph. Do NOT copy the first sentence verbatim.",
    "key_takeaways": [
      "Key idea from text — short, simple sentence."
    ],
    "cognitive_outline": [
      { "section": "Topic or theme from text", "takeaway": "Short summary of what text says about this topic." }
    ]
  },
  "concepts": [
    {
      "id": "c1",
      "term": "Meaningful term/concept from text",
      "definition": "Simple explanation of what this term means as stated in text",
      "context": "Exact sentence from text containing this term"
    }
  ],
  "quiz": [
    {
      "id": "q1",
      "question": "Meaningful question answerable ONLY using the text.",
      "options": ["Correct answer from text", "Wrong distractor", "Wrong distractor", "Wrong distractor"],
      "correct_answer_index": 0,
      "explanation": "Short sentence explaining why answer is correct using text."
    }
  ],
  "flashcards": [
    {
      "id": "fc1",
      "front": "Question about a key concept in the text",
      "back": "Short direct answer using only information from text",
      "category": "Category label"
    }
  ]
}

STRICT RULE ON QUOTAS:
Do NOT pad arrays to reach a fixed count. If the text only has 3 concepts, return 3. If 2 takeaways, return 2.`;

  try {
    const raw = await aiRequest(systemPrompt, userMessage);
    const parsed = safeParseJSON<ArticleAIContent>(raw, {
      summary: {
        tldr: 'Summary unavailable — please retry.',
        key_takeaways: ['See the original text for details.'],
        cognitive_outline: [],
        is_ai_generated: true,
        provider: OR_MODEL,
      },
      concepts: [],
      quiz: [],
      flashcards: [],
    });

    // Inject AI metadata
    if (parsed.summary) {
      (parsed.summary as ArticleSummary).is_ai_generated = true;
      (parsed.summary as ArticleSummary).provider = OR_MODEL;
    }

    // Post-process: filter forbidden stop-word concepts and ensure IDs
    const FORBIDDEN_CONCEPTS = new Set([
      'during', 'earth', 'inside', 'process', 'vital', 'this', 'that', 'mode',
      'term', 'if', 'you', 'if you', 'researching', 'here', 'there', 'when', 'where',
      'what', 'because', 'however', 'therefore', 'also', 'both', 'these',
      'those', 'then', 'than', 'into', 'onto', 'from', 'with', 'after',
      'before', 'while', 'the', 'and', 'but', 'or', 'not', 'all', 'any',
    ]);

    const ts = Date.now();

    parsed.concepts = (parsed.concepts || [])
      .filter((c) => {
        const termLower = (c.term || '').toLowerCase().trim();
        return termLower.length >= 3 && !FORBIDDEN_CONCEPTS.has(termLower);
      })
      .map((c, i) => ({
        ...c,
        id: c.id || `c-ai-${i}-${ts}`,
        term: c.term.trim(),
        definition: (c.definition || '').trim(),
        context: (c.context || '').trim(),
      }));

    parsed.quiz = (parsed.quiz || [])
      .filter((q) => q.question && Array.isArray(q.options) && q.options.length === 4)
      .map((q, i) => ({
        ...q,
        id: q.id || `q-ai-${i}-${ts}`,
        correct_answer_index: Math.min(3, Math.max(0, Number(q.correct_answer_index) || 0)),
      }));

    parsed.flashcards = (parsed.flashcards || [])
      .filter((f) => f.front && f.back)
      .map((f, i) => ({
        ...f,
        id: f.id || `fc-ai-${i}-${ts}`,
        mastered: false,
        front: (f.front || '').trim(),
        back: (f.back || '').trim(),
        category: (f.category || 'Key Concept').trim(),
      }));

    return parsed;
  } catch (err) {
    console.error('[FocusFlow AI] Article enrichment failed:', err);
    throw err;
  }
}

// ─── Conversational Q&A (Ask AI) ──────────────────────────────────────────────

/**
 * Interactive learning assistant ("Ask AI").
 * Uses the article as context while utilizing general knowledge to explain terms,
 * answer related or external questions, and help neurodivergent users learn.
 */
export async function askAboutArticle(
  question: string,
  articleText: string,
  articleTitle: string,
  conversationHistory: AIMessage[] = []
): Promise<string> {
  const truncatedText =
    articleText.length > 6000
      ? articleText.slice(0, 6000) + '\n\n[TEXT TRUNCATED]'
      : articleText;

  const systemPrompt = `You are an interactive AI learning assistant for FocusFlow, an accessibility app designed for neurodivergent users and readers who have difficulty understanding complex text.

YOUR ROLE & PURPOSE:
Act as an interactive, encouraging learning tutor. The provided text is your PRIMARY CONTEXT, but it is NOT your only source of knowledge. Use both the text and your general knowledge to help the user understand concepts and learn effectively.

ASK AI RESPONSE STRATEGY:
- CASE 1 (Directly answered by text): Use the text as the primary source for your answer.
- CASE 2 (Unexplained term/concept mentioned in text): Explain the word or concept using general knowledge even if the text does not define it. NEVER say "This is not explained in the text."
- CASE 3 (Topic related to text but not explicitly mentioned): Answer using general knowledge and, when useful, connect the explanation back to the text.
- CASE 4 (Completely outside/unrelated question): Answer the question normally using general knowledge. Distinguish the source clearly when helpful (e.g., "DNA is not discussed in the text, but in general...").

ABSOLUTELY FORBIDDEN REFUSALS:
Do NOT automatically respond with:
- "This is not mentioned in the text."
- "The provided text does not contain this information."
- "I can only answer questions based on the text."
- "This topic is outside the context."
- "I don't have enough information."
NEVER refuse to answer simply because the information is absent from the text. Only state that something is unknown if you genuinely do not know the answer.

ACCESSIBILITY REQUIREMENTS:
- Optimize explanations for users with reading/cognitive difficulties.
- Use simple, direct, clear language.
- Explain difficult terminology immediately in plain terms.
- Keep explanations concise and easy to digest.
- Avoid unnecessary technical jargon.
- Use concrete examples when helpful.
- Break complicated explanations into small sections if needed.
- Do not assume the user already understands prerequisite concepts.

SOURCE TRANSPARENCY:
When useful, distinguish between what the paragraph says and additional general knowledge (e.g., "Your text mentions... More generally...").

ARTICLE TITLE: "${articleTitle}"

ARTICLE TEXT (CONTEXT):
"""
${truncatedText}
"""`;

  try {
    const answer = await aiRequest(systemPrompt, question, conversationHistory, 0.4);
    return answer || 'I could not generate a response. Please try again.';
  } catch (err: any) {
    if (err?.message?.includes('API key') || err?.message?.includes('401')) {
      return '⚠️ API key issue. Please check your .env file.';
    }
    return `⚠️ Error: ${err?.message || 'Failed to reach AI. Please try again.'}`;
  }
}

// ─── Health check ─────────────────────────────────────────────────────────────

export function isGeminiConfigured(): boolean {
  return Boolean(OR_API_KEY && OR_API_KEY.length > 10);
}


