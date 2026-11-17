from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ScenarioDefinition(BaseModel):

    id: str
    workspace_id: str
    name: str
    definition: dict[str, Any]
    created_at: datetime


class CreateScenarioRequest(BaseModel):

    name: str = Field(min_length=1)
    definition: dict[str, Any]


class ScenarioNotFound(Exception):

    def __init__(self, scenario_id: str) -> None:
        self.scenario_id = scenario_id
        super().__init__(f"Scenario '{scenario_id}' not found")


class ScenarioStore:

    def __init__(self, workspace_dir: Path) -> None:
        self._dir = workspace_dir / "scenarios"

    def _path(self, workspace_id: str, scenario_id: str) -> Path:
        return self._dir / workspace_id / f"{scenario_id}.json"

    def create(
        self,
        workspace_id: str,
        request: CreateScenarioRequest,
    ) -> ScenarioDefinition:


        scenario = ScenarioDefinition(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            name=request.name,
            definition=request.definition,
            created_at=datetime.now(UTC),
        )

        path = self._path(workspace_id, scenario.id)
        path.parent.mkdir(parents=True, exist_ok=True)

        tmp_path = path.with_suffix(".json.tmp")
        tmp_path.write_text(scenario.model_dump_json(), encoding="utf-8")
        tmp_path.replace(path)

        return scenario