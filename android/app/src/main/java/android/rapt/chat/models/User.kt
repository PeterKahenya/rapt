

package android.rapt.chat.data.models

import com.google.gson.annotations.SerializedName
import retrofit2.http.Field

data class User(
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

data class ProfileUpdateRequest(
    @Field("name")
    val name: String? = null,
    @Field("device_fcm_token")
    val deviceFcmToken: String? = null
)