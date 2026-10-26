from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt

CpuId = Annotated[StrictInt, Field(ge=0, le=1048575)]
Pid = Annotated[StrictInt, Field(gt=0, le=2147483647)]
Identity = Annotated[str, Field(pattern=r'^\d{1,30}$')]
CpuSet = Annotated[list[CpuId], Field(min_length=1, max_length=65536)]


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Target(Input):
    pid: Pid
    identity: Identity


class Preview(Target):
    cpus: CpuSet
    scope: Literal['main', 'task', 'threads', 'related'] = 'main'
    task_tid: Pid | None = None
    related: Annotated[list[Target], Field(max_length=128)] = []


class Apply(Input):
    preview_id: Annotated[str, Field(min_length=20, max_length=100)]
    confirmed: StrictBool


class Restore(Input):
    experiment_id: Annotated[str, Field(pattern=r'^[0-9a-f]{24}$')]


class Recommendation(Target):
    workload: Literal['gaming', 'competitive gaming', 'browsing', 'communication', 'encoding', 'rendering', 'compilation', 'streaming', 'ai inference', 'background', 'custom', 'unknown'] = 'unknown'
    restrictions: CpuSet | None = None


class Recording(Target):
    phase: Literal['baseline', 'experiment', 'restored']
    interval: Annotated[float, Field(ge=0.5, le=60)] = 2


class Profile(Input):
    name: Annotated[str, Field(min_length=1, max_length=80)]
    cpus: CpuSet
    note: Annotated[str, Field(max_length=500)] = ''
    generation: Annotated[str, Field(max_length=64)]


class Settings(Input):
    read_only: StrictBool
    display_offset: Annotated[StrictInt, Field(ge=0, le=1)] = 1


class TopologyResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    cpu_model: str
    architecture: str
    physical_core_count: int | None
    logical_cpu_count: int
    cores: list[dict]
    cache_domains: list[dict]
    x3d: dict
    generation: str
