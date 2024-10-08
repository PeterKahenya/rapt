package rapt.chat.raptandroid.data.model

import com.google.gson.annotations.SerializedName
import retrofit2.http.Field

data class ProfileUpdateRequest(
    @Field("name")
    val name: String? = null,
    @Field("device_fcm_token")
    val deviceFcmToken: String? = null
)

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

data class ProfileResponse(
    @SerializedName("client_apps")
    val clientApps: List<ClientApp>,
    @SerializedName("created_at")
    val createdAt: String,
    val id: String,
    @SerializedName("is_active")
    val isActive: Boolean,
    @SerializedName("is_superuser")
    val isSuperUser: Boolean,
    @SerializedName("is_verified")
    val isVerified: Boolean,
    @SerializedName("last_seen")
    val lastSeen: Any,
    val name: String,
    val phone: String,
    val roles: List<Role>,
    @SerializedName("updated_at")
    val updatedAt: String
)

data class UserProfile(
    val name: String,
    val phone: String,
    val userId: String
)

fun ProfileResponse.toUserProfile() = UserProfile(
    name = name,
    phone = phone,
    userId = id
)