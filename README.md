# Automated Rorschach Mood Journal (PoC)

A proof-of-concept system that uses LLM-based NLP to analyze free-form user text, inspired by the Rorschach inkblot test. It interprets emotional and cognitive patterns from ambiguous responses and returns a mood label with a short reflection.

## Idea

Traditional Rorschach tests are subjective and manual.
This project explores how LLMs can automate a similar interpretive process by analyzing open-ended text and generating structured emotional insights at scale.

## What it does

* Accepts free-text journal input
* Uses Groq API (Llama 3.3) for NLP analysis
* Detects mood / emotional state
* Generates a short reflective interpretation
* Stores entries for later review

## API

**POST /journal**

```json
{ "text": "Everything feels unclear and heavy today." }
```

Response:

```json
{
  "id": 1,
  "mood": "anxious",
  "reflection": "There’s a sense of mental weight and uncertainty in what you’re expressing.",
  "created_at": "2025-01-04T12:00:00"
}
```

**GET /journal**
Returns all saved entries.

**GET /health**
Health check endpoint.

## Purpose

A PoC exploring automated interpretation of ambiguous human text using LLMs, inspired by Rorschach-style projection analysis.

---

## 📅 Development History (POC Phase)

**January 3, 2025**
Major project test POC started with Kumar, Akshay, and Nishanth.

**January 4, 2025**
It seems to be working. We’re continuing the project test for a month and exploring how it behaves.

**January 5, 2025**
Had a surprisingly calm day after college. Sat with Kumar and Akshay in the campus cafe and talked about IA exams and placement season starting soon. It felt good to slow down for a bit.

**January 8, 2025**
Felt anxious throughout the day thinking about IA exams and placements together. Kumar and Nishanth were also discussing preparation, which made everything feel more intense.

**January 10, 2025**
Had a productive day in college. Group studied for IA with Kumar, Akshay, and Nishanth. We also started making our own question bank for IA preparation.

**January 13, 2025**
Spent most of the day thinking about IA marks and placement eligibility. Kumar and Akshay were talking about the same pressure, and it felt shared but still heavy.

**January 16, 2025**
College felt overwhelming today. IA revision, assignments, and placement-related discussions with Nishanth and Kumar all piled up. Hard to focus properly on anything for long.

**January 19, 2025**
Had a good group study session for IA with Kumar, Akshay, and Nishanth after class. We added more questions to our own question bank and also discussed placements.

**January 22, 2025**
IA exams went well today. Kumar, Akshay, and Nishanth also felt relieved after finishing them. Confidence about the semester improved a lot.

**January 26, 2025**
Stayed home and spent time on Discord with Kumar, Akshay, and Nishanth. We played Skribbl and Smash Karts and just relaxed after IA.

**January 30, 2025**
After college, went to the mall with Kumar, Akshay, and Nishanth. Felt like a good way to end the month after all the IA stress and project work.

**January 31, 2025**
This POC phase is now closed, and we’re moving on to a new automated test-based approach with a different idea.
