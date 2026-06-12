from langgraph.checkpoint.base import BaseCheckpointSaver
class DummySaver(BaseCheckpointSaver):
    async def aget_tuple(self, config): pass
    async def alist(self, config, *, filter=None, before=None, limit=None):
        yield None
    async def aput(self, config, checkpoint, metadata, new_versions): pass
    async def aput_writes(self, config, writes, task_id, task_path=""): pass

saver = DummySaver()
checkpoint = {"id": "123", "v": 1, "channel_values": {}}
fmt, data = saver.serde.dumps_typed(checkpoint)
print("dumps_typed returns:", fmt, data)
loaded = saver.serde.loads_typed((fmt, data))
print("loads_typed returns:", loaded)
