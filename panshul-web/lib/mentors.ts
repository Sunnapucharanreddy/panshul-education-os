export const MENTORS = [
  {
    id: "teacher",
    title: "Teacher",
    headline: "Learn the idea, not just the answer.",
    line: "Doubts, homework, and step-by-step explanations. English, Hindi, or Telugu.",
    prompt: "Explain photosynthesis step by step, as if I am in class 8.",
  },
  {
    id: "quiz",
    title: "Quiz",
    headline: "Practice until it sticks.",
    line: "Ask for questions in chat, or open Quiz for a scored set that saves to your progress.",
    prompt: "Give me five practice questions on fractions, then check my answers one by one.",
  },
  {
    id: "career",
    title: "Career",
    headline: "Choose a path you can actually follow.",
    line: "Streams, courses, and roadmaps that start with free or low-cost steps.",
    prompt: "I like biology and design. What can I study after class 12 in India?",
  },
  {
    id: "interview",
    title: "Interview",
    headline: "Rehearse one question at a time.",
    line: "Mock interviews and spoken English, with direct feedback after each answer.",
    prompt: "Start a mock interview for a junior software developer role. Ask one question at a time.",
  },
  {
    id: "startup",
    title: "Startup",
    headline: "Shrink the idea until you can test it.",
    line: "Validation, a small first version, and the risks a new founder should face early.",
    prompt: "I want to build a tutoring app for class 10 maths. Help me test the idea before I build it.",
  },
] as const;

export type MentorId = (typeof MENTORS)[number]["id"];

export function mentorTitle(id: string) {
  if (id === "youtube") return "Video";
  return MENTORS.find((mentor) => mentor.id === id)?.title ?? "Mentor";
}
