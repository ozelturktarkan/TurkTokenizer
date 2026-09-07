"""S02 phrase boundaries above the frozen CP1 context model."""
import bootstrap
from context_proposals import ContextProposalSelector
from joint_planner import JointProposalPlanner
from r5.engine import fingerprint

class ContiguousPhrasePlanner(JointProposalPlanner):
    def noun_phrases(self, tokens, indices):
        # Clause construction omits commas/coordinators. Build phrases within
        # each contiguous run, before any role beam prunes its candidates.
        runs = []
        for index in indices:
            if not runs or index != runs[-1][-1] + 1:
                runs.append([])
            runs[-1].append(index)
        return [phrase for run in runs for phrase in JointProposalPlanner.noun_phrases(self, tokens, run)]

class S02Selector(ContextProposalSelector):
    def __init__(self, model, rows, context_model):
        super().__init__(model, rows, context_model)
        self.planner = ContiguousPhrasePlanner(frames=self.planner.frames, beam=self.planner.beam)
        self.context_fingerprint = fingerprint(context_model)

    def manifest(self):
        residual = self.ranker.model.get("version", "").startswith("S02-context-")
        return {**super().manifest(), "selection_followup": "S02",
                "phrase_cross_gap_disabled": True, "additional_model_fit": residual,
                "context_model_version": self.ranker.model.get("version"),
                "context_model_fingerprint": self.context_fingerprint,
                "same_final_objective_as": self.ranker.model.get("version") if residual else "C1"}
