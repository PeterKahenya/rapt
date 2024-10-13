package rapt.chat.raptandroid.data.repository

import android.util.Log
import io.ktor.websocket.WebSocketSession
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.flow
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import rapt.chat.raptandroid.common.Constants
import rapt.chat.raptandroid.data.model.APIChatRoom
import rapt.chat.raptandroid.data.model.APIChatRoomMember
import rapt.chat.raptandroid.data.model.Auth
import rapt.chat.raptandroid.data.model.ChatRoomCreate
import rapt.chat.raptandroid.data.source.ChatMessage
import rapt.chat.raptandroid.data.source.ChatRoom
import rapt.chat.raptandroid.data.source.ChatRoomDao
import rapt.chat.raptandroid.data.source.ChatRoomMember
import rapt.chat.raptandroid.data.source.Contact
import rapt.chat.raptandroid.data.source.ContactDao
import rapt.chat.raptandroid.data.source.RaptApi
import rapt.chat.raptandroid.data.source.RaptSocketClient
import java.util.UUID
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
    val message: String,
    val created_at: String? = null,
    val updated_at: String? = null,
    val id: String? = ""
)

@Serializable
data class SocketMessage(
    val type: MessageType,
    val obj: ChatObj? = null,
    val user: User? = null,
    val timestamp: String? = null,
    @SerialName("message_id")
    val messageId: String
)

fun SocketMessage.toChatMessage(roomId: String): ChatMessage {
    return ChatMessage(
        chatId = this.obj?.id?:"",
        message = this.obj?.message ?: "",
        senderId = this.user?.id ?: "",
        chatRoomId = roomId,
        isRead = false,
        timestamp = System.currentTimeMillis(),
        messageId = this.messageId,
        status = "sent"
    )
}

interface ChatRepository{
    val messages: SharedFlow<SocketMessage>
    suspend fun createChatRoom(contactId: String): APIChatRoom
    suspend fun dbSaveChatRoom(apiChatRoom: APIChatRoom)
    suspend fun dbGetChatRoomByContactId(contactId: String): String?
    suspend fun dbGetChatRoomMembers(chatRoomId: String): List<Contact>
    suspend fun dbGetChatRoomMessages(chatRoomId: String): MutableList<ChatMessage>
    suspend fun dbSaveChatMessage(roomId: String, socketMessage: SocketMessage, checkExists: Boolean = true): ChatMessage
    suspend fun connectToChatSocket(roomId: String): Flow<ChatMessage>
    suspend fun sendMessage(roomId: String, message: String, messageType: MessageType): ChatMessage
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
        val chatRoomCreateRequest = ChatRoomCreate(members = listOf(APIChatRoomMember(id = contactId), APIChatRoomMember(id = profileRepository.getProfile().id)))
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
            chatRoomDao.insertChatRoom(ChatRoom(chatRoomId = apiChatRoom.id))
        }
        for (member in apiChatRoom.members){
            val dbChatRoomMember = chatRoomDao.getMembersByRoomAndContact(member.id, apiChatRoom.id)
            if (dbChatRoomMember == null){
                chatRoomDao.insertChatRoomMember(
                    ChatRoomMember(
                        contactId = member.id,
                        chatRoomId = apiChatRoom.id
                    )
                )
            }

            val dbContact = contactDao.getByContactId(member.id)
            if (dbContact.isEmpty()) {
                contactDao.insert(
                    Contact(
                        name = member.name,
                        phone = member.phone,
                        contactId = member.id,
                        isActive = false
                    )
                )
            }
        }
    }

    override suspend fun dbGetChatRoomByContactId(contactId: String): String? {
        return contactDao.getChatRoom(contactId)
    }

    override suspend fun dbGetChatRoomMembers(chatRoomId: String): List<Contact> {
        val memberContacts = mutableListOf<Contact>()
        val auth = authRepository.auth()
        if (auth != null){
            val chatRoomMembers = chatRoomDao.getChatRoomMembers(chatRoomId)
            for (member in chatRoomMembers){
                if (member != auth.userId){
                    memberContacts.add(contactDao.getByContactId(member)[0])
                }
            }
        }
        return memberContacts
    }

    override suspend fun dbGetChatRoomMessages(chatRoomId: String): MutableList<ChatMessage> {
        val dbMessages = chatRoomDao.getChatRoomMessages(chatRoomId)
        return dbMessages
    }

    override suspend fun dbSaveChatMessage(roomId: String, socketMessage: SocketMessage, checkExists: Boolean): ChatMessage {
        val chatMessage = socketMessage.toChatMessage(roomId)
        if (checkExists) {
            val existingMessage = chatRoomDao.getMessageById(chatMessage.messageId)
            if (existingMessage != null) {
                existingMessage.chatId = chatMessage.chatId
                existingMessage.status = chatMessage.status
                chatRoomDao.updateChatMessage(existingMessage)
                return existingMessage
            }else{
                chatRoomDao.insertChatMessage(chatMessage)
            }
        }else{
            chatRoomDao.insertChatMessage(chatMessage)
        }
        return chatMessage
    }

    override suspend fun connectToChatSocket(roomId: String): Flow<ChatMessage> = flow{
        Log.d("RaptSocketClient:", "connectToChatSocket: $roomId")
        socketClient.connect("${Constants.SOCKET_URL}chatsocket/$roomId").collect{ socketMessage ->
            when(socketMessage.type){
                MessageType.ONLINE -> {
                    println("User ${socketMessage.user?.name} is online")
                }
                MessageType.OFFLINE -> {
                    println("User ${socketMessage.user?.name} is offline")
                }
                MessageType.CHAT -> {
                    val chatMessage = dbSaveChatMessage(roomId,socketMessage)
                    emit(chatMessage)
                }
                MessageType.READ -> {
                    val chatMessage = dbSaveChatMessage(roomId,socketMessage)
                    emit(chatMessage)
                }
                MessageType.READING -> TODO()
                MessageType.AWAY -> TODO()
                MessageType.TYPING -> TODO()
                MessageType.THINKING -> TODO()
            }
        }
    }

    override suspend fun sendMessage(roomId: String, message: String, messageType: MessageType): ChatMessage {
        val auth = authRepository.auth()
        val socketMessage = SocketMessage(
            type = messageType,
            obj = ChatObj(message=message),
            user = User(id = auth?.userId?:""),
            timestamp = System.currentTimeMillis().toString(),
            messageId = UUID.randomUUID().toString()+ (auth?.userId ?: "")
        )
        socketClient.sendMessage(socketMessage)
        val chatMessage = dbSaveChatMessage(roomId, socketMessage, checkExists = false)
        return chatMessage
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