import { AgentWorkspace } from "@/components/AgentWorkspace";
import { RequireAuth } from "@/components/RequireAuth";
import { INTERVIEW_WORKSPACE } from "@/lib/workspaces";

export default function InterviewPage() {
  return <RequireAuth><AgentWorkspace config={INTERVIEW_WORKSPACE} /></RequireAuth>;
}
