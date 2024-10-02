package rapt.chat.raptandroid.data.repository

import io.ktor.websocket.WebSocketSession
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.flow
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import rapt.chat.raptandroid.data.model.ChatRoom
import rapt.chat.raptandroid.data.model.ChatRoomCreateRequest
import rapt.chat.raptandroid.data.model.Contact
import rapt.chat.raptandroid.data.source.RaptApi
import rapt.chat.raptandroid.data.source.RaptSocketClient
import javax.inject.Inject

@Serializable
enum class MessageType {
    @SerialName("online") ONLINE,
    @SerialName("offline") OFFLINE,
    @SerialName("chat") CHAT,
    @SerialName("read") READ,
    @SerialName("reading") READING,
    @SerialName("away") AWAY,
    @SerialName("typing") TYPING,
    @SerialName("thinking") THINKING
}

@Serializable
data class User(
    val id: String,
    val created_at: String? = "",
    val updated_at: String? = "",
    val phone: String? ="",
    val name: String? = ""
)

@Serializable
data class ChatObj(
    val message: String
)

@Serializable
data class Message(
    val type: MessageType,
    val obj: ChatObj? = null,
    val user: User? = null,
    val timestamp: String? = null
)

interface ChatRepository{
    val messages: SharedFlow<Message>
    suspend fun createChatRoom(contactIds: List<String>): ChatRoom
    suspend fun connectToChatSocket(roomId: String): WebSocketSession
    suspend fun listenToMessages(messagesFlow: MutableSharedFlow<Message>): Flow<Message>
    suspend fun sendMessage(message: String)
    suspend fun disconnectFromChatSocket()
    suspend fun getChatRooms(): List<ChatRoom>
    suspend fun getChatRoom(id: String): ChatRoom
    suspend fun updateChatRoom(id: String, chatRoomCreateRequest: ChatRoomCreateRequest): ChatRoom
    suspend fun deleteChatRoom(id: String)
}

class ChatRepositoryImpl @Inject constructor(
    private val api: RaptApi,
    private val authRepository: AuthRepository,
    private val socketClient: RaptSocketClient,
    private val profileRepository: ProfileRepository
): ChatRepository {

    override val messages = MutableSharedFlow<Message> ()

    override suspend fun createChatRoom(contactIds: List<String>): ChatRoom {
        println("createChatRoom: $contactIds")
        val contacts = contactIds.map { id -> Contact(id = id, phone = "", name = "") }
        println("createChatRoom: $contacts")
        val chatRoomCreateRequest = ChatRoomCreateRequest(members = contacts)
        println("createChatRoom: $chatRoomCreateRequest")
        val auth = authRepository.auth()
        println("createChatRoom: $auth")
        return api.createChatRoom(
            accessToken = "Bearer ${auth?.accessToken}",
            chatRoomRequest = chatRoomCreateRequest
        )
    }


    override suspend fun connectToChatSocket(roomId: String): WebSocketSession {
        println("connectToChatSocket: $roomId")
        return socketClient.connect("ws://rapt.chat/api/chatsocket/$roomId")
    }

    override suspend fun listenToMessages(messagesFlow: MutableSharedFlow<Message>): Flow<Message> = flow {
        socketClient.startListening(messagesFlow)
    }

    override suspend fun sendMessage(message: String) {
        val auth = authRepository.auth()
        val user = profileRepository.getProfile()
        println(user)
        val msg = Message(
            type = MessageType.CHAT,
            obj = ChatObj(message=message),
            user = User(id = user.id),
            timestamp = null
        )
        val json = Json { ignoreUnknownKeys = true }
        val messageString = json.encodeToString(msg)
        println("sendMessage: $messageString")
        socketClient.sendMessage(messageString)
    }

    override suspend fun disconnectFromChatSocket() {
        socketClient.disconnect()
    }

    override suspend fun getChatRooms(): List<ChatRoom> {
        val auth = authRepository.auth()
        return api.getChatRooms(accessToken = "Bearer ${auth?.accessToken}")
    }

    override suspend fun getChatRoom(id: String): ChatRoom {
        val auth = authRepository.auth()
        return api.getChatRoom(roomId = id, accessToken = "Bearer ${auth?.accessToken}")
    }

    override suspend fun updateChatRoom(
        id: String,
        chatRoomCreateRequest: ChatRoomCreateRequest
    ): ChatRoom {
        val auth = authRepository.auth()
        return api.updateChatRoom(
            roomId = id,
            accessToken = "Bearer ${auth?.accessToken}",
            chatRoomRequest = chatRoomCreateRequest
        )
    }

    override suspend fun deleteChatRoom(id: String) {
        val auth = authRepository.auth()
        api.deleteChatRoom(
            roomId = id,
            accessToken = "Bearer ${auth?.accessToken}"
        )
    }
}