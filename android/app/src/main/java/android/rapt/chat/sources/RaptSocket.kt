package android.rapt.chat.sources

import android.rapt.chat.models.SocketMessage
import android.rapt.chat.repositories.AuthRepository
import android.rapt.chat.viewmodels.ConnectionStatus
import android.util.Log
import io.ktor.client.HttpClient
import io.ktor.client.plugins.websocket.webSocketSession
import io.ktor.client.request.url
import io.ktor.websocket.Frame
import io.ktor.websocket.WebSocketSession
import io.ktor.websocket.close
import io.ktor.websocket.readText
import kotlinx.coroutines.channels.ClosedReceiveChannelException
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import javax.inject.Inject


class RaptSocket @Inject constructor(
    private val client: HttpClient,
    private val authRepository: AuthRepository
) {
    private var session: WebSocketSession? = null

    suspend fun connect(serverUrl: String, messageFlow: MutableSharedFlow<SocketMessage>, connectionStatusFlow: MutableSharedFlow<ConnectionStatus>) {
        var retryDelay = 1000L
        while (true) {
            try {
                connectionStatusFlow.emit(ConnectionStatus.Reconnecting)
                val auth = authRepository.auth()
                session = client.webSocketSession {
                    url(serverUrl)
                    headers.append("Authorization", "Bearer ${auth?.accessToken}")
                }
                connectionStatusFlow.emit(ConnectionStatus.Connected)
                retryDelay = 1000L
                listenIncoming(messageFlow)
            } catch (e: Exception) {
                Log.e("RaptSocket", "Socket connection failed, retrying in $retryDelay ms", e)
                connectionStatusFlow.emit(ConnectionStatus.Disconnected)
                delay(retryDelay)
                retryDelay = (retryDelay * 2).coerceAtMost(16000L)
            }
        }
    }

    private suspend fun listenIncoming(messageFlow: MutableSharedFlow<SocketMessage>) {
        try {
            Log.i("RaptSocket", "Listening for incoming messages")
            session?.let { socket ->
                for (frame in socket.incoming) {
                    frame as? Frame.Text ?: continue
                    val json = Json { ignoreUnknownKeys = true }
                    val chatMessage = json.decodeFromString<SocketMessage>(frame.readText())
                    messageFlow.emit(chatMessage)
                }
            }
        } catch (e: Exception) {
            throw e
        }
    }

    suspend fun sendSocketMessage(socketMessage: SocketMessage) {
        try {
            val json = Json { ignoreUnknownKeys = true }
            val messageString = json.encodeToString(socketMessage)
            session?.send(Frame.Text(messageString))
        } catch (e: Exception) {
            Log.e("RaptSocket", "Error sending message", e)
        }
    }

    suspend fun disconnect() {
        session?.close()
        client.close()
        Log.d("RaptSocket", "Disconnected")
    }


}