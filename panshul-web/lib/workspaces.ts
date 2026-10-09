import type { WorkspaceConfig } from "@/components/AgentWorkspace";

export const CAREER_WORKSPACE: WorkspaceConfig = {
  agent: "career",
  title: "Plan a career path that fits you.",
  description: "Explore courses, skills, and realistic next steps with Panshul’s Career Advisor.",
  emptyTitle: "What would you like your future work to look like?",
  emptyDescription: "Share your class or current stage, the subjects you enjoy, and what you want from a career. The advisor can ask follow-up questions where useful.",
  prompts: [
    "I enjoy biology and design. What paths could I explore after class 12?",
    "Help me compare computer science and electronics as degree paths.",
    "Build an affordable 6-month plan to start learning data analysis.",
  ],
  guideTitle: "A plan grounded in your context",
  guideItems: [
    "Match options to your interests and strengths",
    "Compare courses, skills, and entry routes",
    "Build a phased roadmap with practical milestones",
    "Start with affordable learning resources",
  ],
};

export const INTERVIEW_WORKSPACE: WorkspaceConfig = {
  agent: "interview",
  title: "Practice one interview question at a time.",
  description: "Choose a role and rehearse with Panshul’s Mock Interview coach. Each answer gets focused feedback and a next question.",
  emptyTitle: "Get ready for your first question.",
  emptyDescription: "Add the role you are preparing for. Panshul will ask one question, wait for your answer, give feedback, and continue.",
  prompts: [],
  guideTitle: "Your practice loop",
  guideItems: [
    "One realistic question at a time",
    "Feedback on content, structure, and communication",
    "A new question after each answer",
    "Keep practicing in the same interview session",
  ],
};

export const STARTUP_WORKSPACE: WorkspaceConfig = {
  agent: "startup",
  title: "Turn an idea into a small test.",
  description: "Work with Panshul’s Startup Advisor to validate the problem before investing in a big build.",
  emptyTitle: "What idea are you thinking about?",
  emptyDescription: "Describe the people you hope to help and the problem you want to solve. The advisor can help shape a useful first experiment.",
  prompts: [
    "I want to build a tutoring app for class 10 maths. Help me validate the idea.",
    "How can I find and interview my first target users?",
    "Help me scope the smallest MVP for a student budgeting tool.",
  ],
  guideTitle: "Move from idea to evidence",
  guideItems: [
    "Validate the problem before building",
    "Identify and talk to target users",
    "Scope a small, testable MVP",
    "Surface risks and choose a next step",
  ],
};
