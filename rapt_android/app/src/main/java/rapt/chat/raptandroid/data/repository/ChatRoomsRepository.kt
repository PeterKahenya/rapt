package rapt.chat.raptandroid.data.repository

import android.os.Build
import androidx.annotation.RequiresApi
import io.ktor.websocket.WebSocketSession
import kotlinx.coroutines.flow.MutableSharedFlow
import rapt.chat.raptandroid.common.Constants
import rapt.chat.raptandroid.data.model.APIChatRoom
import rapt.chat.raptandroid.data.source.ChatMessage
import rapt.chat.raptandroid.data.source.ChatRoom
import rapt.chat.raptandroid.data.source.ChatRoomDao
import rapt.chat.raptandroid.data.source.ChatRoomMember
import rapt.chat.raptandroid.data.source.Contact
import rapt.chat.raptandroid.data.source.ContactDao
import rapt.chat.raptandroid.data.source.RaptApi
import rapt.chat.raptandroid.data.source.RaptSocketClient
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import javax.inject.Inject

data class ChatRoomSocket(
    val room: ChatRoom,
    val socket: WebSocketSession,
    val messageFlow: MutableSharedFlow<SocketMessage>
)

data class DisplayChatRoom(
    val roomId: String,
    val members: List<Contact>,
    val messages: List<ChatMessage>
)

interface ChatRoomsRepository {
    suspend fun getAllDBChatRooms(): List<DisplayChatRoom>
    suspend fun getAllAPIChatRooms(): List<APIChatRoom>
    suspend fun saveChatRoom(chatRoom: APIChatRoom)
//    suspend fun connectToChatRooms(chatRooms: List<ChatRoom>): List<ChatRoomSocket>
}

class ChatRoomsRepositoryImpl @Inject constructor(
    private val api: RaptApi,
    private val chatRoomDao: ChatRoomDao,
    private val contactDao: ContactDao,
    private val authRepository: AuthRepository,
    private val socketClient: RaptSocketClient
): ChatRoomsRepository {

    override suspend fun getAllDBChatRooms(): List<DisplayChatRoom> {
        val chatRoomIds =  chatRoomDao.getAllChatRooms().map { it.chatRoomId }
        val chatRooms = mutableListOf<DisplayChatRoom>()
        for (roomId in chatRoomIds){
            val contactIds = chatRoomDao.getChatRoomMembers(roomId)
            val members = mutableListOf<Contact>()
            for (contactId in contactIds){
                members.add(contactDao.getByContactId(contactId)[0])
            }
            val messages = chatRoomDao.getChatRoomMessages(roomId)
            chatRooms.add(DisplayChatRoom(roomId, members, messages))
        }
        return chatRooms
    }

    override suspend fun getAllAPIChatRooms(): List<APIChatRoom> {
        println("Getting chat rooms from api")
        val auth = authRepository.auth()
        if (auth != null){
            return api.getChatRooms(accessToken = "Bearer ${auth.accessToken}")
        } else {
            throw Exception("No auth")
        }
    }

    @RequiresApi(Build.VERSION_CODES.O)
    fun parseStringToMillis(dateTimeString: String): Long {
        val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss")
        val localDateTime = LocalDateTime.parse(dateTimeString, formatter)
        return localDateTime.toInstant(ZoneOffset.UTC).toEpochMilli()
    }

    @RequiresApi(Build.VERSION_CODES.O)
    override suspend fun saveChatRoom(chatRoom: APIChatRoom) {
        val chatRoomId = chatRoomDao.getChatRoomById(chatRoom.id)
        // If no chat room with this id exists, insert it
        if (chatRoomId == null) {
            chatRoomDao.insertChatRoom(ChatRoom(chatRoomId = chatRoom.id))
        }
        // save messages
        for (chat in chatRoom.roomChats){
            val messageDB = chatRoomDao.getMessageByChatId(chat.id)
            if (messageDB == null){
                chatRoomDao.insertChatMessage(
                    ChatMessage(
                        chatId = chat.id,
                        message = chat.message,
                        senderId = chat.sender.id,
                        chatRoomId = chatRoom.id,
                        isRead = chat.isRead,
                        timestamp = parseStringToMillis(chat.createdAt),
                        type = MessageType.CHAT.toString(),
                        status = "sent",
                        messageId = chat.id+chat.sender.id
                    )
                )
            } else {
                chatRoomDao.updateChatMessage(
                    ChatMessage(
                        id = messageDB.id,
                        chatId = chat.id,
                        message = chat.message,
                        senderId = chat.sender.id,
                        chatRoomId = chatRoom.id,
                        isRead = chat.isRead,
                        timestamp = parseStringToMillis(chat.createdAt),
                        type = MessageType.CHAT.toString(),
                        status = "sent",
                        messageId = chat.id+chat.sender.id
                    )
                )
            }
        }
        // save contacts
        for (member in chatRoom.members){
            val contactDB = contactDao.getByContactId(member.id)
            if (contactDB.isEmpty()){
                contactDao.insert(
                    Contact(
                        name = member.name,
                        phone = member.phone,
                        contactId = member.id,
                        isActive = member.is_active
                    )
                )
            }
        }
        // save chat room members
        for (member in chatRoom.members){
            val dbChatRoomMember = chatRoomDao.getMembersByRoomAndContact(member.id, chatRoom.id)
            if (dbChatRoomMember == null) {
                chatRoomDao.insertChatRoomMember(
                    ChatRoomMember(
                        contactId = member.id,
                        chatRoomId = chatRoom.id
                    )
                )
            }
        }

    }

//    override suspend fun connectToChatRooms(chatRooms: List<ChatRoom>): List<ChatRoomSocket> {
//        val chatRoomsSockets = mutableListOf<ChatRoomSocket>()
//        for (room in chatRooms) {
//            val messageFlow = MutableSharedFlow<SocketMessage>()
//            val socketSession = socketClient.connect("${Constants.SOCKET_URL}chatsocket/${room.chatRoomId}")
//            if (socketSession != null) {
//                socketClient.startListening(messageFlow,socketSession)
//                chatRoomsSockets.add(ChatRoomSocket(room, socketSession, messageFlow))
//            }
//        }
//        return chatRoomsSockets
//    }
}