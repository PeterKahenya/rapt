package rapt.chat.raptandroid.data.model

import com.google.gson.annotations.SerializedName

data class Sender(
    val client_apps: List<Any>,
    val contacts: List<Any>,
    val created_at: String,
    val id: String,
    val is_active: Boolean,
    val is_superuser: Boolean,
    val is_verified: Boolean,
    val last_seen: String,
    val name: String,
    val phone: String,
    val phone_verification_code: String,
    val phone_verification_code_expiry_at: String,
    val roles: List<Any>,
    val updated_at: String
)

data class RoomChat(
    @SerializedName("created_at")
    val createdAt: String,
    val id: String,
    @SerializedName("is_read")
    val isRead: Boolean,
    val media: List<Media>,
    val message: String,
    val room: Room,
    val sender: Sender,
    @SerializedName("updated_at")
    val updatedAt: String
)