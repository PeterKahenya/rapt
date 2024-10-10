package rapt.chat.raptandroid.data.source

import android.util.Log
import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import io.ktor.client.plugins.websocket.WebSockets
import io.ktor.client.plugins.websocket.webSocketSession
import io.ktor.client.request.url
import io.ktor.websocket.Frame
import io.ktor.websocket.WebSocketSession
import io.ktor.websocket.close
import io.ktor.websocket.readText
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import rapt.chat.raptandroid.data.repository.AuthRepository
import rapt.chat.raptandroid.data.repository.SocketMessage
import javax.inject.Inject

class RaptSocketClient @Inject constructor(
    private val authRepository: AuthRepository
) {
    private val client = HttpClient(CIO) {
        install(WebSockets)
    }
    private var socket: WebSocketSession? = null

//    private val _messages = MutableSharedFlow<Message>()
//    val messages: SharedFlow<Message> = _messages.asSharedFlow()

    suspend fun connect(serverUrl: String): WebSocketSession {
        try {
            println("Socket Connecting to $serverUrl")
            val auth = authRepository.auth()
            socket = client.webSocketSession {
                url(serverUrl)
                headers.append("Authorization", "Bearer ${auth?.accessToken}")
            }
            Log.d("ChatClient", "Connected to $serverUrl")
            println("ChatClient Connected to $serverUrl")
            return socket!!
        } catch (e: Exception) {
            Log.e("ChatClient", "Error connecting to $serverUrl", e)
            throw e
        }
    }

    fun startListening(messagesFlow: MutableSharedFlow<SocketMessage>) = CoroutineScope(Dispatchers.IO).launch {
        try {
            socket?.let { socket ->
                for (frame in socket.incoming) {
                    frame as? Frame.Text ?: continue
                    val receivedText = frame.readText()
                    println("ChatClient Received message: $receivedText")
                    Log.i("ChatClient", "Message: $receivedText")
                    val json = Json { ignoreUnknownKeys = true }
                    val chatMessage = json.decodeFromString<SocketMessage>(receivedText)
                    println("ChatClient Message: $chatMessage")
                    messagesFlow.emit(chatMessage)
                }
            }
        } catch (e: Exception) {
            Log.e("ChatClient", "Error while listening", e)
        }
    }

    suspend fun sendMessage(message: String) {
        try {
            socket?.send(Frame.Text(message))
        } catch (e: Exception) {
            Log.e("ChatClient", "Error sending message", e)
        }
    }

    suspend fun disconnect() {
        socket?.close()
        client.close()
        Log.d("ChatClient", "Disconnected")
    }
}