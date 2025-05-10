package android.rapt.chat.models

import com.google.gson.annotations.SerializedName

data class MemberObj(
    val id: String
)

data class ChatRoom(
    val id: String,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String,
    val members: List<MemberObj>,
    @SerializedName("room_chats")
    val chats: MutableList<Chat>
)

data class ChatRoomCreate(
    val members: List<MemberObj>
)

data class ChatRoomUpdate(
    val members: List<MemberObj>
)