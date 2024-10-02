package rapt.chat.raptandroid.data.model

data class ChatRoom(
    val created_at: String,
    val id: String,
    val members: List<Member>,
    val room_chats: List<RoomChat>,
    val updated_at: String
)