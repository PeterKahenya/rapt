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
import rapt.chat.raptandroid.data.model.APIChatRoom
import rapt.chat.raptandroid.data.model.APIChatRoomMember
import rapt.chat.raptandroid.data.model.ChatRoomCreate
import rapt.chat.raptandroid.data.source.ChatMessage
import rapt.chat.raptandroid.data.source.ChatRoom
import rapt.chat.raptandroid.data.source.ChatRoomDao
import rapt.chat.raptandroid.data.source.ChatRoomMember
import rapt.chat.raptandroid.data.source.Contact
import rapt.chat.raptandroid.data.source.ContactDao
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
data class SocketMessage(
    val type: MessageType,
    val obj: ChatObj? = null,
    val user: User? = null,
    val timestamp: String? = null
)

interface ChatRepository{
    val messages: SharedFlow<SocketMessage>
    suspend fun createChatRoom(contactId: String): APIChatRoom
    suspend fun dbSaveChatRoom(apiChatRoom: APIChatRoom)
    suspend fun dbGetChatRoomByContactId(contactId: String): String?
    suspend fun dbGetChatRoomMembers(chatRoomId: String): List<Contact>
    suspend fun dbGetChatRoomMessages(chatRoomId: String): MutableList<ChatMessage>
    suspend fun dbSaveChatMessage(socketMessage: SocketMessage): ChatMessage
    suspend fun connectToChatSocket(roomId: String): WebSocketSession
    suspend fun listenToMessages(messagesFlow: MutableSharedFlow<SocketMessage>): Flow<SocketMessage>
    suspend fun sendMessage(message: String): SocketMessage
    suspend fun disconnectFromChatSocket()
    suspend fun deleteChatRoom(id: String)
}

class ChatRepositoryImpl @Inject constructor(
    private val api: RaptApi,
    private val chatRoomDao: ChatRoomDao,
    private val contactDao: ContactDao,
    private val authRepository: AuthRepository,
    private val socketClient: RaptSocketClient,
    private val profileRepository: ProfileRepository
): ChatRepository {

    override val messages = MutableSharedFlow<SocketMessage> ()

    override suspend fun createChatRoom(contactId: String): APIChatRoom {
        println("createChatRoom for Contact: $contactId")
        val chatRoomCreateRequest = ChatRoomCreate(members = listOf(APIChatRoomMember(id = contactId), APIChatRoomMember(id = profileRepository.getProfile().id)))
        println("createChatRoom request: $chatRoomCreateRequest")
        val auth = authRepository.auth()
        if (auth == null) {
            throw Exception("Not authenticated")
        }else{
            return api.createChatRoom(
                accessToken = "Bearer ${auth.accessToken}",
                chatRoomCreateRequest
            )
        }
    }

    override suspend fun dbSaveChatRoom(apiChatRoom: APIChatRoom) {
        val dbChatRoom = chatRoomDao.getChatRoomById(apiChatRoom.id)
        if (dbChatRoom == null){
            chatRoomDao.insertChatRoom(
                ChatRoom(
                    chatRoomId = apiChatRoom.id
                )
            )
        }
        for (member in apiChatRoom.members){
            chatRoomDao.insertChatRoomMember(
                ChatRoomMember(
                    contactId = member.id,
                    chatRoomId = apiChatRoom.id
                )
            )
            contactDao.insert(
                Contact(
                    name = member.name,
                    phone = member.phone,
                    contactId = member.id,
                    userId = member.id,
                    isActive = false
                )
            )
        }
    }

    override suspend fun dbGetChatRoomByContactId(contactId: String): String? {
        return contactDao.getChatRoom(contactId)
    }

    override suspend fun dbGetChatRoomMembers(chatRoomId: String): List<Contact> {
        val chatRoomMembers = chatRoomDao.getChatRoomMembers(chatRoomId)
        return chatRoomMembers.map { it -> contactDao.getByContactId(it)[0] }
    }

    override suspend fun dbGetChatRoomMessages(chatRoomId: String): MutableList<ChatMessage> {
        return chatRoomDao.getChatRoomMessages(chatRoomId)
    }

    override suspend fun dbSaveChatMessage(socketMessage: SocketMessage): ChatMessage {
        val chatMessage = ChatMessage(
            id = socketMessage.user?.id ?: "",
            message = socketMessage.obj?.message ?: "",
            senderId = socketMessage.user?.id ?: "",
            chatRoomId = socketMessage.user?.id ?: "",
            isRead = false,
            timestamp = System.currentTimeMillis()
        )
        chatRoomDao.insertChatMessage(chatMessage)
        return chatMessage
    }

    override suspend fun connectToChatSocket(roomId: String): WebSocketSession {
        println("connectToChatSocket: $roomId")
        return socketClient.connect("ws://rapt.chat/api/chatsocket/$roomId")
    }

    override suspend fun listenToMessages(messagesFlow: MutableSharedFlow<SocketMessage>): Flow<SocketMessage> = flow {
        socketClient.startListening(messagesFlow)
    }

    override suspend fun sendMessage(message: String): SocketMessage {
        val auth = authRepository.auth()
        val msg = SocketMessage(
            type = MessageType.CHAT,
            obj = ChatObj(message=message),
            user = User(id = auth?.userId?:""),
            timestamp = null
        )
        val json = Json { ignoreUnknownKeys = true }
        val messageString = json.encodeToString(msg)
        println("sendMessage: $messageString")
        socketClient.sendMessage(messageString)
        return msg
    }

    override suspend fun disconnectFromChatSocket() {
        socketClient.disconnect()
    }

    override suspend fun deleteChatRoom(id: String) {
        val auth = authRepository.auth()
        api.deleteChatRoom(
            roomId = id,
            accessToken = "Bearer ${auth?.accessToken}"
        )
    }
}