from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field as PydanticField
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Server(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=2, max_length=120)
    ip: str = Field(index=True, min_length=7, max_length=45)
    port: int = Field(default=22, ge=1, le=65535)
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=255)
    cpu_cores: int = Field(default=1, ge=1)
    ram_gb: int = Field(default=1, ge=1)
    environment: str = Field(default="production", max_length=50)
    note: str = Field(default="", max_length=500)


class ServerCreate(BaseModel):
    name: str = PydanticField(min_length=2, max_length=120)
    ip: str = PydanticField(min_length=7, max_length=45)
    port: int = PydanticField(default=22, ge=1, le=65535)
    username: str = PydanticField(min_length=1, max_length=100)
    password: str = PydanticField(min_length=1, max_length=255)
    cpu_cores: int = PydanticField(default=1, ge=1)
    ram_gb: int = PydanticField(default=1, ge=1)
    environment: str = PydanticField(default="production", max_length=50)
    note: str = PydanticField(default="", max_length=500)


class ServerUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = PydanticField(default=None, min_length=2, max_length=120)
    ip: Optional[str] = PydanticField(default=None, min_length=7, max_length=45)
    port: Optional[int] = PydanticField(default=None, ge=1, le=65535)
    username: Optional[str] = PydanticField(default=None, min_length=1, max_length=100)
    password: Optional[str] = PydanticField(default=None, min_length=1, max_length=255)
    cpu_cores: Optional[int] = PydanticField(default=None, ge=1)
    ram_gb: Optional[int] = PydanticField(default=None, ge=1)
    environment: Optional[str] = PydanticField(default=None, max_length=50)
    note: Optional[str] = PydanticField(default=None, max_length=500)


class ServerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ip: str
    port: int
    username: str
    password: str
    cpu_cores: int
    ram_gb: int
    environment: str
    note: str


engine = create_engine("sqlite:///servers.db", connect_args={"check_same_thread": False})


@asynccontextmanager
async def lifespan(_: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="DevOps Server Manager API", lifespan=lifespan)


def get_session():
    with Session(engine) as session:
        yield session


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/servers", response_model=ServerRead, status_code=201)
def create_server(server_in: ServerCreate, session: Session = Depends(get_session)) -> ServerRead:
    server = Server.model_validate(server_in)
    session.add(server)
    session.commit()
    session.refresh(server)
    return ServerRead.model_validate(server)


@app.get("/servers", response_model=list[ServerRead])
def list_servers(
    env: Optional[str] = Query(default=None, description="Filter by environment"),
    session: Session = Depends(get_session),
) -> list[ServerRead]:
    statement = select(Server)
    if env:
        statement = statement.where(Server.environment == env)
    servers = session.exec(statement).all()
    return [ServerRead.model_validate(item) for item in servers]


@app.get("/servers/{server_id}", response_model=ServerRead)
def get_server(server_id: int, session: Session = Depends(get_session)) -> ServerRead:
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return ServerRead.model_validate(server)


@app.patch("/servers/{server_id}", response_model=ServerRead)
def update_server(
    server_id: int,
    server_in: ServerUpdate,
    session: Session = Depends(get_session),
) -> ServerRead:
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    update_data = server_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(server, key, value)

    session.add(server)
    session.commit()
    session.refresh(server)
    return ServerRead.model_validate(server)


@app.delete("/servers/{server_id}", status_code=204)
def delete_server(server_id: int, session: Session = Depends(get_session)) -> None:
    server = session.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    session.delete(server)
    session.commit()
