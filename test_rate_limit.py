import asyncio
import websockets
import json
import time

async def test_rate_limit():
    uri = "ws://localhost:8000/ws/test-room/test-user"
    async with websockets.connect(uri) as websocket:
        print("Conectado. Enviando mensagens rápidas...")
        for i in range(20):
            msg = {"action": "vote", "value": "1"}
            await websocket.send(json.dumps(msg))
            print(f"Mensagem {i+1} enviada")
        
        # O backend não manda erro se ignorar, mas podemos ver se ele ainda responde ao estado final
        print("Aguardando 1 segundo...")
        await asyncio.sleep(1)
        # Se as 20 mensagens foram processadas, o estado mostraria o último voto.
        # Mas aqui só queremos ver se a conexão continua viva e não caiu por excesso de msgs (se implementado assim).
        print("Teste concluído.")

if __name__ == "__main__":
    asyncio.run(test_rate_limit())
