package rapt.chat.raptandroid.data.model

import com.google.gson.annotations.SerializedName

data class Role(
    @SerializedName("created_at")
    val createdAt: String,
    val description: String,
    val id: String,
    val name: String,
    val permissions: List<Permission>,
    @SerializedName("updated_at")
    val updatedAt: Any
)