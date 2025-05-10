package android.rapt.chat.models

import com.google.gson.annotations.SerializedName

data class Media(
    @SerializedName("chat_id")
    val chatId: String,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("file_type")
    val fileType: String,
    val id: String,
    val link: String,
    @SerializedName("updated_at")
    val updatedAt: String
)

data class RoomObj(
    val id: String
)
data class SenderObj(
    val id: String
)

data class Chat(
    @SerializedName("created_at")
    val createdAt: String,
    val id: String,
    @SerializedName("is_read")
    val isRead: Boolean,
    val media: List<Media>,
    val message: String,
    val room: RoomObj,
    val sender: SenderObj,
    @SerializedName("updated_at")
    val updatedAt: String
)



