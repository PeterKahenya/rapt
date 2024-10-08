package rapt.chat.raptandroid.data.source

import androidx.room.ColumnInfo
import androidx.room.Dao
import androidx.room.Database
import androidx.room.Delete
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.RoomDatabase
import androidx.room.Update

/*
    One Contact Many ChatRooms but we handle one for now
    One ChatRoom Many Contacts
    One ChatRoom Many ChatMessages
 */

/* Entities */
@Entity
data class Contact(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    @ColumnInfo(name = "name") var name: String,
    @ColumnInfo(name = "phone") val phone: String,
    @ColumnInfo(name = "contact_id") var contactId: String,
    @ColumnInfo(name = "user_id") var userId: String,
    @ColumnInfo(name = "is_active") var isActive: Boolean
)

@Entity
data class ChatRoom(
    @PrimaryKey @ColumnInfo(name = "chatroom_id") val chatRoomId: String
)

@Entity
data class ChatRoomMember(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    @ColumnInfo(name = "contact_id") val contactId: String,
    @ColumnInfo(name = "chatroom_id") val chatRoomId: String,
)

@Entity
data class ChatMessage(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "message") val message: String,
    @ColumnInfo(name = "sender_id") val senderId: String,
    @ColumnInfo(name = "chatroom_id") val chatRoomId: String,
    @ColumnInfo(name = "is_read") val isRead: Boolean,
    @ColumnInfo(name = "timestamp") val timestamp: Long
    /* TODO add support for media */
)

/* DAOs */
@Dao
interface ContactDao{

    @Query("SELECT * FROM contact")
    suspend fun getAll(): List<Contact>

    @Query("SELECT * FROM contact WHERE phone = :phone")
    suspend fun getByPhone(phone: String): List<Contact>

    @Query("SELECT * FROM contact WHERE contact_id = :contactId")
    suspend fun getByContactId(contactId: String): List<Contact>

    @Query("SELECT * FROM contact WHERE " +
            "name LIKE '%' || :query || '%' "+
            "OR phone LIKE '%' || :query || '%'"
    )
    suspend fun search(query: String): List<Contact>

    @Insert
    suspend fun insert(contact: Contact)

    @Update
    suspend fun update(contact: Contact)

    @Delete
    suspend fun delete(contact: Contact)

    @Query("SELECT chatroom_id FROM chatroommember WHERE chatroommember.contact_id = :contactId LIMIT 1")
    suspend fun getChatRoom(contactId: String) : String?

}

@Dao
interface ChatRoomDao{

    @Query("SELECT * FROM chatroom")
    suspend fun getAllChatRooms(): List<ChatRoom>

    @Query("SELECT * FROM chatroom WHERE chatroom_id = :chatRoomId")
    suspend fun getChatRoomById(chatRoomId: String): ChatRoom?

    @Insert
    suspend fun insertChatRoom(chatRoom: ChatRoom)

    @Insert
    suspend fun insertChatRoomMember(chatRoomMember: ChatRoomMember)

    @Query("SELECT chatroommember.contact_id FROM chatroommember WHERE chatroommember.chatroom_id = :chatRoomId")
    suspend fun getChatRoomMembers(chatRoomId: String): List<String>

    @Query("SELECT * FROM chatmessage WHERE chatmessage.chatroom_id = :chatRoomId")
    suspend fun getChatRoomMessages(chatRoomId: String): MutableList<ChatMessage>

    @Delete
    suspend fun delete(chatRoom: ChatRoom)

    @Insert
    suspend fun insertChatMessage(chatMessage: ChatMessage)

    @Query("SELECT * FROM chatmessage WHERE chatmessage.id = :chatId")
    suspend fun getMessageById(chatId: String): ChatMessage?

}

/* Database */

@Database(entities = [Contact::class, ChatRoom::class, ChatMessage::class, ChatRoomMember::class], version = 1)
abstract class RaptDatabase : RoomDatabase() {
    abstract fun contactDao(): ContactDao
    abstract fun chatRoomDao(): ChatRoomDao
}





























