package rapt.chat.raptandroid.data.repository

import io.ktor.websocket.WebSocketSession
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.serialization.Serializable
import rapt.chat.raptandroid.data.model.ChatRoom
import rapt.chat.raptandroid.data.model.ChatRoomCreateRequest

enum class MessageType {
    ONLINE, OFFLINE, CHAT, READ, READING, AWAY, TYPING, THINKING
}

@Serializable
data class Message(
    val type: MessageType,
    val obj: Map<String, String>,
    val user: Map<String, String>? = null,
    val timestamp: String? = null
)

@Serializable
data class AuthenticatedMessage(
    val message: Message,
    val authorization: String
)

interface ChatRepository{
    val messages: SharedFlow<Message>
    suspend fun createChatRoom(contactIds: List<String>): ChatRoom
    suspend fun connectToChatSocket(roomId: String): WebSocketSession
    suspend fun listenToMessages(): Flow<Message>
    suspend fun sendMessage(message: String)
    suspend fun disconnectFromChatSocket()
    suspend fun getChatRooms(): List<ChatRoom>
    suspend fun getChatRoom(id: String): ChatRoom
    suspend fun updateChatRoom(id: String, chatRoomCreateRequest: ChatRoomCreateRequest): ChatRoom
    suspend fun deleteChatRoom(id: String)
}