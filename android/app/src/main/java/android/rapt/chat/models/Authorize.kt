package android.rapt.chat.models

import com.google.gson.annotations.SerializedName

data class ClientApp(
    val id: String
)

data class ContentType(
    val content: String,
    @SerializedName("created_at")
    val createdAt: String,
    val id: String,
    @SerializedName("updated_at")
    val updatedAt: Any
)

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