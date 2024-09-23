package rapt.chat.raptandroid.data.model

import com.google.gson.annotations.SerializedName

data class ContentType(
    val content: String,
    @SerializedName("created_at")
    val createdAt: String,
    val id: String,
    @SerializedName("updated_at")
    val updatedAt: Any
)