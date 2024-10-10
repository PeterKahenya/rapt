package rapt.chat.raptandroid.data.repository

import io.ktor.websocket.WebSocketSession
import rapt.chat.raptandroid.data.model.APIChatRoom
import rapt.chat.raptandroid.data.source.ChatMessage
import rapt.chat.raptandroid.data.source.ChatRoom
import rapt.chat.raptandroid.data.source.ChatRoomDao
import rapt.chat.raptandroid.data.source.Contact
import rapt.chat.raptandroid.data.source.ContactDao
import rapt.chat.raptandroid.data.source.RaptApi
import rapt.chat.raptandroid.data.source.RaptSocketClient
import javax.inject.Inject

data class ChatRoomSocket(
    val room: ChatRoom,
    val socket: WebSocketSession
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
    suspend fun connectToChatRooms(chatRooms: List<ChatRoom>): List<ChatRoomSocket>
}

class ChatRoomsRepositoryImpl @Inject constructor(
    private val api: RaptApi,
    private val chatRoomDao: ChatRoomDao,
    private val contactDao: ContactDao,
    private val authRepository: AuthRepository,
    private val socketClient: RaptSocketClient
): ChatRoomsRepository {

    override suspend fun getAllDBChatRooms(): List<DisplayChatRoom> {
        println("Getting chat rooms from db")
        val chatRoomIds =  chatRoomDao.getAllChatRooms().map { it.chatRoomId }
        val chatRooms = mutableListOf<DisplayChatRoom>()
        for (roomId in chatRoomIds){
            val contactIds = chatRoomDao.getChatRoomMembers(roomId)
            val members = mutableListOf<Contact>()
            for (contactId in contactIds){
                members.add(contactDao.getByContactId(contactId)[0])
            }
            val messages = chatRoomDao.getChatRoomMessages(roomId)
            println("MContacts: $messages $members")
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

    override suspend fun saveChatRoom(chatRoom: APIChatRoom) {
        val chatRoomId = chatRoomDao.getChatRoomById(chatRoom.id)
        if (chatRoomId == null) {
            chatRoomDao.insertChatRoom(ChatRoom(chatRoomId = chatRoom.id))
        }
        for (chat in chatRoom.roomChats){
            val messageDB = chatRoomDao.getMessageById(chat.id)
            if (messageDB == null){
                chatRoomDao.insertChatMessage(
                    ChatMessage(
                        id = chat.id,
                        message = chat.message,
                        senderId = chat.sender.id,
                        chatRoomId = chatRoom.id,
                        isRead = chat.isRead,
                        timestamp = System.currentTimeMillis()
                    )
                )
            }
        }
        for (member in chatRoom.members){
            val contactDB = contactDao.getByContactId(member.id)
            if (contactDB.isEmpty()){
                chatRoomDao.insertChatRoomMember(
                    rapt.chat.raptandroid.data.source.ChatRoomMember(
                        contactId = member.id,
                        chatRoomId = chatRoom.id
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
    }

    override suspend fun connectToChatRooms(chatRooms: List<ChatRoom>): List<ChatRoomSocket> {
        val auth = authRepository.auth()
        val chatRoomsSockets = mutableListOf<ChatRoomSocket>()
        for (room in chatRooms) {
            val socket = socketClient.connect("ws://rapt.chat/api/chatsocket/${room.chatRoomId}")
//            socketClient.startListening()
            chatRoomsSockets.add(ChatRoomSocket(room, socket))
        }
        return chatRoomsSockets
    }
}