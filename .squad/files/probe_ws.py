import asyncio, json, ssl, sys
import websockets

async def main():
    url = "wss://orchestrator.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/ws/voice"
    try:
        async with websockets.connect(url, ssl=ssl.create_default_context()) as ws:
            print("CONNECTED")
            await ws.send(json.dumps({"type":"start","conversationId":None,"mode":"push_to_talk"}))
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=5)
                print("GOT:", str(msg)[:300])
            except asyncio.TimeoutError:
                print("recv timeout (connected, no msg yet)")
    except Exception as e:
        print("CONNECT ERR:", type(e).__name__, e)

asyncio.run(main())
