package android.rapt.chat.repositories

import android.rapt.chat.common.RaptConstants
import android.rapt.chat.models.ChatRoom
import android.rapt.chat.models.ChatRoomCreate
import android.rapt.chat.models.MemberObj
import android.rapt.chat.models.SocketMessage
import android.rapt.chat.sources.ChatRoomDao
import android.rapt.chat.sources.DBChat
import android.rapt.chat.sources.DBChatRoom
import android.rapt.chat.sources.DBChatRoomMember
import android.rapt.chat.sources.RaptAPI
import android.rapt.chat.sources.RaptSocket
import kotlinx.coroutines.flow.MutableSharedFlow
import java.util.UUID
import javax.inject.Inject

interface ChatRepository{
    suspend fun createChatRoom(contactIds: List<String>): DBChatRoom
    suspend fun initializeChatSocket(roomId: String, messageFlow: MutableSharedFlow<SocketMessage>)
    suspend fun sendMessage(socketMessage: SocketMessage)
    suspend fun saveChat(message: String, roomId: String): DBChat
}

class ChatRepositoryImpl @Inject constructor(
    private val api: RaptAPI,
    private val chatRoomDao: ChatRoomDao,
    private val authRepository: AuthRepository,
    private val socket: RaptSocket,
    private val profileRepository: ProfileRepository
): ChatRepository {


    private suspend fun saveChatroom(apiChatRoom: ChatRoom): DBChatRoom{
        val dbChatRoom = if ( chatRoomDao.getChatRoomById(apiChatRoom.id) != null)  {
            chatRoomDao.getChatRoomById(apiChatRoom.id)?: throw Exception("Chat room not found")
        } else {
            chatRoomDao.insertChatRoom(DBChatRoom(chatRoomId = apiChatRoom.id))
            chatRoomDao.getChatRoomById(apiChatRoom.id)?: throw Exception("Chat room not found")
        }
        for (member in apiChatRoom.members) {
            if (chatRoomDao.getChatRoomMembers(apiChatRoom.id).contains(member.id)) continue
            chatRoomDao.insertChatRoomMember(
                DBChatRoomMember(
                    contactId = member.id,
                    chatRoomId = apiChatRoom.id
                )
            )
        }
        return dbChatRoom
    }

    override suspend fun createChatRoom(contactIds: List<String>): DBChatRoom {
        try {
            val auth = authRepository.auth() ?: throw Exception("Not authenticated")
            val apiChatRoom =  api.createChatRoom(
                accessToken = "Bearer ${auth.accessToken}",
                ChatRoomCreate(members = contactIds.map { MemberObj(id = it, name = "", phone = "") } + MemberObj(id = profileRepository.getProfile().id, name = "", phone = ""))
            )
            val dbChatRoom = this.saveChatroom(apiChatRoom)
            return dbChatRoom
        } catch (e: Exception) {
            throw e
        }
    }

    override suspend fun initializeChatSocket(roomId: String, messageFlow: MutableSharedFlow<SocketMessage>) {
        return socket.connect("ws://${RaptConstants.BASE_URL}chatsocket/$roomId", messageFlow)
    }

    override suspend fun saveChat(message: String, roomId: String): DBChat {
        val auth = authRepository.auth() ?: throw Exception("Not authenticated")
        val timeStamp = System.currentTimeMillis()
        val dbChat = DBChat(
            chatId = "temp_${UUID.randomUUID()}", // Temporary ID
            socketMessageId = UUID.randomUUID().toString(), // For message tracking
            message = message,
            senderId = auth.userId,
            chatRoomId = roomId,
            isRead = false,
            timestamp = timeStamp
        )
        chatRoomDao.insertMessage(dbChat)
        return dbChat
    }

    override suspend fun sendMessage(socketMessage: SocketMessage) {
        socket.sendSocketMessage(socketMessage)
    }

}