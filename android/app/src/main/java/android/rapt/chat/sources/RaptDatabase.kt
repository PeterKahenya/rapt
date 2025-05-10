package android.rapt.chat.sources

import android.rapt.chat.models.ChatObj
import android.rapt.chat.models.MessageType
import android.rapt.chat.models.SocketMessage
import android.rapt.chat.models.UserObj
import androidx.room.*

/* Entities */
@Entity
data class DBContact(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    @ColumnInfo(name = "name") var name: String,
    @ColumnInfo(name = "phone") val phone: String,
    @ColumnInfo(name = "contact_id") var contactId: String,
    @ColumnInfo(name = "user_id") var userId: String,
    @ColumnInfo(name = "is_active") var isActive: Boolean,
    @ColumnInfo(name = "is_online") var isOnline: Boolean = false,
    @ColumnInfo(name = "last_seen") var lastSeen: Long = 0
)

@Entity
data class DBChatRoom(
    @PrimaryKey
    @ColumnInfo(name = "chatroom_id") val chatRoomId: String
)

@Entity(primaryKeys = ["contact_id", "chatroom_id"])
data class DBChatRoomMember(
    @ColumnInfo(name = "contact_id") val contactId: String,
    @ColumnInfo(name = "chatroom_id") val chatRoomId: String,
)

@Entity
data class DBChat(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    @ColumnInfo(name = "chatId") val chatId: String,
    @ColumnInfo(name = "socket_message_id") val socketMessageId: String? = null,
    @ColumnInfo(name = "sender_id") val senderId: String,
    @ColumnInfo(name = "chatroom_id") val chatRoomId: String,
    @ColumnInfo(name = "message") val message: String,
    @ColumnInfo(name = "is_read") val isRead: Boolean,
    @ColumnInfo(name = "timestamp") val timestamp: Long
    /* TODO add support for media */
)

fun DBChat.toSocketMessage(): SocketMessage {
    return SocketMessage(
        id = this.socketMessageId ?: "",
        type = MessageType.CHAT,
        obj = ChatObj(
                message = this.message,
                id = "${this.timestamp}"
        ),
        user = UserObj(id = this.senderId),
        timestamp = "${this.timestamp}"
    )
}

/* DAOs */
@Dao
interface ContactDao{

    @Query("SELECT * FROM dbcontact")
    suspend fun getAll(): List<DBContact>

    @Query("SELECT * FROM dbcontact WHERE phone = :phone")
    suspend fun getByPhone(phone: String): List<DBContact>

    @Query("SELECT * FROM dbcontact WHERE contact_id = :contactId LIMIT 1")
    suspend fun getByContactId(contactId: String): DBContact?

    @Query("SELECT * FROM dbcontact WHERE " +
            "name LIKE '%' || :query || '%' "+
            "OR phone LIKE '%' || :query || '%'"
    )
    suspend fun search(query: String): List<DBContact>

    @Insert
    suspend fun insert(contact: DBContact)

    @Update
    suspend fun update(contact: DBContact)

    @Delete
    suspend fun delete(contact: DBContact)
}

@Dao
interface ChatRoomDao{

    @Query("SELECT * FROM dbchatroom")
    suspend fun getAllChatRooms(): List<DBChatRoom>

    @Query("SELECT * FROM dbchatroom WHERE chatroom_id = :chatRoomId")
    suspend fun getChatRoomById(chatRoomId: String): DBChatRoom?

    @Insert
    suspend fun insertChatRoom(chatRoom: DBChatRoom)

    @Insert
    suspend fun insertChatRoomMember(chatRoomMember: DBChatRoomMember)

    @Query("SELECT dbchatroommember.contact_id FROM dbchatroommember WHERE dbchatroommember.chatroom_id = :chatRoomId")
    suspend fun getChatRoomMembers(chatRoomId: String): List<String>

    @Query("SELECT * FROM dbchat WHERE dbchat.chatroom_id = :chatRoomId")
    suspend fun getChatRoomMessages(chatRoomId: String): MutableList<DBChat>

    @Delete
    suspend fun delete(chatRoom: DBChatRoom)

    @Insert(DBChat::class)
    suspend fun insertMessage(chatMessage: DBChat)

    @Query("SELECT * FROM dbchat WHERE dbchat.id = :chatId")
    suspend fun getMessageById(chatId: String): DBChat?

    @Query("SELECT * FROM dbchat WHERE dbchat.socket_message_id = :socketMessageId LIMIT 1")
    suspend fun getMessageBySocketMessageId(socketMessageId: String): DBChat?

    @Update(DBChat::class)
    suspend fun updateMessage(chatMessage: DBChat)

}

/* Database */
@Database(entities = [DBContact::class, DBChatRoom::class, DBChatRoomMember::class, DBChat::class], version = 1)
abstract class RaptDatabase : RoomDatabase() {
    abstract fun contactDao(): ContactDao
    abstract fun chatRoomDao(): ChatRoomDao
}