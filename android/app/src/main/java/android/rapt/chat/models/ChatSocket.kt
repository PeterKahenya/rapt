package android.rapt.chat.models

import android.rapt.chat.sources.DBChat
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

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
data class ChatObj(
    val id: String,
    val message: String
)

@Serializable
data class UserObj(
    val id: String
)

@Serializable
data class SocketMessage(
    val id: String,
    val type: MessageType,
    val obj: ChatObj? = null,
    val user: UserObj? = null,
    val timestamp: String
)

fun SocketMessage.toDBChat(roomId: String): DBChat {
    return DBChat(
        chatId = this.obj?.id?: "",
        message = this.obj?.message?: "",
        socketMessageId = this.id,
        senderId = this.user?.id ?: "",
        chatRoomId = roomId,
        isRead = false,
        timestamp = System.currentTimeMillis() // TODO: Convert timestamp to Date Long
    )
}