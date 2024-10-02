package rapt.chat.raptandroid.data.model

import com.google.gson.annotations.SerializedName
import retrofit2.http.Field

data class ProfileUpdateRequest(
    @Field("name")
    val name: String? = null,
    @Field("device_fcm_token")
    val deviceFcmToken: String? = null,
    @Field("contacts")
    val contacts: List<Contact>? = null
)

data class ProfileResponse(
    @SerializedName("client_apps")
    val clientApps: List<ClientApp>,
    val contacts: List<Contact>,
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
    @SerializedName("phone_verification_code")
    val phoneVerificationCode: Any,
    @SerializedName("phone_verification_code_expiry_at")
    val phoneVerificationCodeExpiryAt: Any,
    val roles: List<Role>,
    @SerializedName("updated_at")
    val updatedAt: String
)

fun ProfileResponse.toUserProfile() = UserProfile(
    name = name,
    phone = phone
)