package rapt.chat.raptandroid.data.model

import com.google.gson.annotations.SerializedName



data class APIChatRoomMember(
    val id: String
)

data class APIChatRoomMemberResponse(
    val created_at: String,
    val id: String,
    val is_active: Boolean,
    val last_seen: String,
    val name: String,
    val phone: String,
    val updated_at: String
)

data class ChatRoomCreate(
    val members: List<APIChatRoomMember>
)

data class ChatRoomUpdate(
    val members: List<APIChatRoomMember>
)

data class APIChatRoom(
    val id: String,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String,
    val members: List<APIChatRoomMemberResponse>,
    @SerializedName("room_chats")
    val roomChats: MutableList<RoomChat>,

)

data class Room(
    val id: String
)