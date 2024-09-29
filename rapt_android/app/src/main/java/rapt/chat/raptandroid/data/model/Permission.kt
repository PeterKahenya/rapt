package rapt.chat.raptandroid.data.model

import com.google.gson.annotations.SerializedName

data class Permission(
    val codename: String,
    @SerializedName("content_type")
    val contentType: ContentType,
    @SerializedName("created_at")
    val createdAt: String,
    val id: String,
    val name: String,
    @SerializedName("updated_at")
    val updatedAt: Any
)