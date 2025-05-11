package android.rapt.chat.repositories

import android.rapt.chat.models.ChatRoomCreate
import android.rapt.chat.models.MemberObj
import android.rapt.chat.sources.ChatRoomDao
import android.rapt.chat.sources.ContactDao
import android.rapt.chat.sources.DBChat
import android.rapt.chat.sources.DBChatRoom
import android.rapt.chat.sources.DBChatRoomMember
import android.rapt.chat.sources.DBChatRoomWithMembersAndMessages
import android.rapt.chat.sources.DBContact
import android.rapt.chat.sources.RaptAPI
import javax.inject.Inject

interface ChatsRepository {
    suspend fun sync(): List<DBChatRoomWithMembersAndMessages>
}

class ChatsRepositoryImpl @Inject constructor(
    private val api: RaptAPI,
    private val chatRoomDB: ChatRoomDao,
    private val contactDB: ContactDao,
    private val authRepository: AuthRepository
) : ChatsRepository {

    override suspend fun sync(): List<DBChatRoomWithMembersAndMessages> {
        try {
            val auth = authRepository.auth() ?: throw Exception("No auth found")
            val dbChatRooms = chatRoomDB.getAllChatRooms()
            val apiChatRooms = api.getChatRooms(accessToken = "Bearer ${auth.accessToken}")
            // Any chatroom in the db not in the api should be created in the api
            for (dbChatRoom in dbChatRooms) {
                if (dbChatRoom.chatRoomId !in apiChatRooms.map { it.id }) {
                    api.createChatRoom(
                        accessToken = "Bearer ${auth.accessToken}",
                        chatRoomRequest = ChatRoomCreate(
                            members = chatRoomDB.getChatRoomMembers(dbChatRoom.chatRoomId).map { MemberObj(id = it, name = "", phone = "") }
                        )
                    )
                }
            }
            // Any chatroom in the api not in the db should be added
            for (apiChatRoom in apiChatRooms) {
                if (apiChatRoom.id !in dbChatRooms.map { it.chatRoomId }) {
                    chatRoomDB.insertChatRoom(DBChatRoom(chatRoomId = apiChatRoom.id))
                }
                for (member in apiChatRoom.members) {
                    if (contactDB.getByContactId(contactId = member.id) == null){
                        contactDB.insert(
                            DBContact(
                                name = member.name,
                                phone = member.phone,
                                userId = auth.userId,
                                contactId = member.id,
                                isActive = false
                            )
                        )
                        chatRoomDB.insertChatRoomMember(
                            chatRoomMember = DBChatRoomMember(
                                contactId = member.id,
                                chatRoomId = apiChatRoom.id
                            )
                        )
                    }
                }
                for (message in apiChatRoom.chats) {
                    if (chatRoomDB.getMessageById(message.id) == null) {
                        chatRoomDB.insertMessage(
                            DBChat(
                                chatId = message.id,
                                senderId = message.sender.id,
                                chatRoomId = apiChatRoom.id,
                                message = message.message,
                                isRead = message.isRead,
                                timestamp = System.currentTimeMillis()
                            )
                        )
                    }
                }
            }
            val chatRooms = chatRoomDB.getChatRoomsWithMembersAndMessages().map {
                DBChatRoomWithMembersAndMessages(
                    room = it.room,
                    chats = it.chats,
                    members = it.members.filter { contact -> contact.phone != auth.phone }
                )
            }
            return chatRooms

        } catch (ex: Exception){
            return chatRoomDB.getChatRoomsWithMembersAndMessages()
        }
    }

}