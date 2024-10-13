package rapt.chat.raptandroid.data.source

import android.util.Log
import io.ktor.client.HttpClient
import io.ktor.client.plugins.websocket.DefaultClientWebSocketSession
import io.ktor.client.plugins.websocket.webSocketSession
import io.ktor.client.request.url
import io.ktor.websocket.Frame
import io.ktor.websocket.close
import io.ktor.websocket.readReason
import io.ktor.websocket.readText
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.channels.consumeEach
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.launch
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import rapt.chat.raptandroid.data.repository.AuthRepository
import rapt.chat.raptandroid.data.repository.SocketMessage
import javax.inject.Inject
import kotlin.coroutines.cancellation.CancellationException

class RaptSocketClient @Inject constructor(
    private val authRepository: AuthRepository,
    private val httpClient: HttpClient
) {

    private var socketSession: DefaultClientWebSocketSession? = null
    private var job: Job? = null
    private val coroutineScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val messageChannel = Channel<SocketMessage>()
    private val reconnectInterval = 50000L // 50 seconds

    suspend fun connect(serverUrl: String): Flow<SocketMessage> = flow {
        while (true){
            try {
                Log.d("RaptSocketClient:", "Connecting to $serverUrl")
                val auth = authRepository.auth()
                socketSession = httpClient.webSocketSession {
                    url(serverUrl)
                    headers.append("Authorization", "Bearer ${auth?.accessToken}")
                }
                Log.d("RaptSocketClient:", "Connected to $serverUrl")
                job = coroutineScope.launch {
                    launch { listenForMessages() }
                }
                println("Listening for messages")
                messageChannel.consumeEach { message ->
                    println("Received message: $message")
                    emit(message)
                }
            } catch (e: Exception) {
                Log.e("RaptSocketClient:", "Error in WebSocket connection ${e.message}", e)
                delay(reconnectInterval)
                Log.d("RaptSocketClient:", "Attempting to reconnect...")
            } finally {
                job?.cancelAndJoin()
                socketSession?.close()
            }
        }
    }

    private suspend fun listenForMessages() {
        println("listenForMessages")
        try {
            socketSession?.incoming?.consumeEach { frame ->
                when (frame) {
                    is Frame.Text -> {
                        val receivedText = frame.readText()
                        Log.d("RaptSocketClient", "Received raw message: $receivedText")
                        val json = Json { ignoreUnknownKeys = true }
                        val chatMessage = json.decodeFromString<SocketMessage>(receivedText)
                        Log.i("RaptSocketClient", "Received parsed message: $chatMessage")
                        messageChannel.send(chatMessage)
                    }
                    is Frame.Close -> {
                        Log.w("RaptSocketClient", "WebSocket closed with reason: ${frame.readReason()}")
                        throw CancellationException("WebSocket closed")
                    }
                    else -> Log.d("RaptSocketClient", "Received frame: $frame")
                }
            }
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            Log.e("RaptSocketClient:", "Error in message listener", e)
        }
    }

    suspend fun sendMessage(socketMessage: SocketMessage) {
        try {
            val json = Json { ignoreUnknownKeys = true }
            val socketMessageString = json.encodeToString(socketMessage)
            socketSession?.send(Frame.Text(socketMessageString))
        } catch (e: Exception) {
            Log.e("RaptSocketClient:", "Error sending message", e)
        }
    }

    suspend fun disconnect() {
        socketSession?.close()
        httpClient.close()
        Log.d("RaptSocketClient:", "Disconnected")
    }
}