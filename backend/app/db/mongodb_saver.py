from typing import Any, AsyncIterator, Optional, Sequence
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    ChannelVersions,
)
from bson import Binary

class MongoDBSaver(BaseCheckpointSaver):
    """A custom asynchronous checkpointer for LangGraph that persists state in MongoDB."""

    def __init__(self, client: Optional[Any] = None, db_name: Optional[str] = None):
        super().__init__()
        self._client = client
        self._db_name = db_name

    @property
    def client(self):
        """Lazily resolve client to avoid connection issues on import."""
        if self._client is not None:
            return self._client
        from app.db.mongodb import get_database_client
        return get_database_client()

    @property
    def db(self):
        if self._db_name is not None:
            return self.client[self._db_name]
        from app.core.config import settings
        return self.client[settings.DB_NAME]

    @property
    def checkpoints_col(self):
        return self.db["checkpoints"]

    @property
    def writes_col(self):
        return self.db["checkpoint_writes"]

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Asynchronously fetch a checkpoint tuple using the given configuration."""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = config["configurable"].get("checkpoint_id")

        query = {
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
        }
        if checkpoint_id:
            query["checkpoint_id"] = checkpoint_id

        cursor = self.checkpoints_col.find(query)
        if not checkpoint_id:
            # Sort descending to get the latest checkpoint
            cursor = cursor.sort("checkpoint_id", -1).limit(1)

        docs = await cursor.to_list(length=1)
        if not docs:
            return None

        doc = docs[0]

        # Load serialized fields using loads_typed
        checkpoint = self.serde.loads_typed((doc["checkpoint_type"], doc["checkpoint"]))
        metadata = self.serde.loads_typed((doc["metadata_type"], doc["metadata"]))

        parent_config = {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": doc.get("parent_checkpoint_id"),
            }
        } if doc.get("parent_checkpoint_id") else None

        # Fetch writes associated with this checkpoint
        writes_cursor = self.writes_col.find({
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
            "checkpoint_id": doc["checkpoint_id"],
        }).sort("idx", 1)

        writes_docs = await writes_cursor.to_list(length=None)
        pending_writes = [
            (
                w["task_id"],
                w["channel"],
                self.serde.loads_typed((w["value_type"], w["value"])),
            )
            for w in writes_docs
        ]

        return CheckpointTuple(
            config={
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": doc["checkpoint_id"],
                }
            },
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config=parent_config,
            pending_writes=pending_writes,
        )

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Asynchronously store a checkpoint."""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = config["configurable"].get("checkpoint_id")

        # Serialize checkpoint, metadata, and new_versions using dumps_typed
        checkpoint_type, checkpoint_data = self.serde.dumps_typed(checkpoint)
        metadata_type, metadata_data = self.serde.dumps_typed(metadata)
        new_versions_type, new_versions_data = self.serde.dumps_typed(new_versions)

        doc = {
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
            "checkpoint_id": checkpoint_id,
            "parent_checkpoint_id": parent_checkpoint_id,
            "checkpoint_type": checkpoint_type,
            "checkpoint": Binary(checkpoint_data),
            "metadata_type": metadata_type,
            "metadata": Binary(metadata_data),
            "new_versions_type": new_versions_type,
            "new_versions": Binary(new_versions_data),
        }

        # Upsert checkpoint
        await self.checkpoints_col.update_one(
            {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            },
            {"$set": doc},
            upsert=True,
        )

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        }

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        """Asynchronously store checkpoint writes."""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = config["configurable"]["checkpoint_id"]

        operations = []
        for idx, (channel, value) in enumerate(writes):
            value_type, value_data = self.serde.dumps_typed(value)
            doc = {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
                "task_id": task_id,
                "task_path": task_path,
                "idx": idx,
                "channel": channel,
                "value_type": value_type,
                "value": Binary(value_data),
            }
            operations.append(doc)

        if operations:
            await self.writes_col.insert_many(operations)

    async def alist(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        """Asynchronously list checkpoints."""
        query = {}
        if config is not None:
            query["thread_id"] = config["configurable"]["thread_id"]
            if "checkpoint_ns" in config["configurable"]:
                query["checkpoint_ns"] = config["configurable"]["checkpoint_ns"]

        if before is not None:
            query["checkpoint_id"] = {"$lt": before["configurable"]["checkpoint_id"]}

        if filter is not None:
            for k, v in filter.items():
                query[f"metadata.{k}"] = v

        cursor = self.checkpoints_col.find(query).sort("checkpoint_id", -1)
        if limit is not None:
            cursor = cursor.limit(limit)

        async for doc in cursor:
            checkpoint = self.serde.loads_typed((doc["checkpoint_type"], doc["checkpoint"]))
            metadata = self.serde.loads_typed((doc["metadata_type"], doc["metadata"]))

            parent_config = {
                "configurable": {
                    "thread_id": doc["thread_id"],
                    "checkpoint_ns": doc["checkpoint_ns"],
                    "checkpoint_id": doc.get("parent_checkpoint_id"),
                }
            } if doc.get("parent_checkpoint_id") else None

            # Fetch pending writes
            writes_cursor = self.writes_col.find({
                "thread_id": doc["thread_id"],
                "checkpoint_ns": doc["checkpoint_ns"],
                "checkpoint_id": doc["checkpoint_id"],
            }).sort("idx", 1)

            writes_docs = await writes_cursor.to_list(length=None)
            pending_writes = [
                (
                    w["task_id"],
                    w["channel"],
                    self.serde.loads_typed((w["value_type"], w["value"])),
                )
                for w in writes_docs
            ]

            yield CheckpointTuple(
                config={
                    "configurable": {
                        "thread_id": doc["thread_id"],
                        "checkpoint_ns": doc["checkpoint_ns"],
                        "checkpoint_id": doc["checkpoint_id"],
                    }
                },
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=parent_config,
                pending_writes=pending_writes,
            )
