import { AgentWorkspace } from "@/components/AgentWorkspace";
import { RequireAuth } from "@/components/RequireAuth";
import { CAREER_WORKSPACE } from "@/lib/workspaces";

export default function CareerPage() {
  return <RequireAuth><AgentWorkspace config={CAREER_WORKSPACE} /></RequireAuth>;
}
