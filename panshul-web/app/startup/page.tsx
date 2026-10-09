import { AgentWorkspace } from "@/components/AgentWorkspace";
import { RequireAuth } from "@/components/RequireAuth";
import { STARTUP_WORKSPACE } from "@/lib/workspaces";

export default function StartupPage() {
  return <RequireAuth><AgentWorkspace config={STARTUP_WORKSPACE} /></RequireAuth>;
}
