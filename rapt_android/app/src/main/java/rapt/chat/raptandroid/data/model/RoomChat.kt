package rapt.chat.raptandroid.data.model

data class RoomChat(
    val created_at: String,
    val id: String,
    val is_read: Boolean,
    val media: List<Media>,
    val message: String,
    val room: Room,
    val sender: Sender,
    val updated_at: String
)